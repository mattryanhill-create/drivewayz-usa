#!/usr/bin/env python3
"""
Drivewayz → Lumar Daily Log Push

Runs from GitHub Actions on a daily cron OR manual dispatch.
Pulls yesterday's BigQuery aggregations and uploads them to Lumar as the two
CSVs that Lumar's project 461823 expects:

  - drivewayz-ai-bot-requests-YYYY-MM-DD.csv  (projectUploadType: AIBotLogRequests)
  - drivewayz-log-summary-YYYY-MM-DD.csv      (projectUploadType: GenericLogfileCSV)

Authentication:
  - GCP: google-github-actions/auth populates GOOGLE_APPLICATION_CREDENTIALS
         so the BigQuery client picks up the service account automatically.
  - Lumar: createSessionUsingUserKey mutation using env vars
           LUMAR_USER_KEY_ID + LUMAR_USER_KEY_SECRET to get a session token,
           then x-auth-token on subsequent calls.

Exit codes:
  0   success (uploads landed; skipped if no data)
  1   data fetch failed
  2   Lumar auth/upload failed
"""

import io
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import date, datetime, timedelta, timezone

from google.cloud import bigquery


LUMAR_API = "https://api.lumar.io/graphql"


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def graphql(token: str | None, query: str, variables: dict | None = None) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["x-auth-token"] = token
    req = urllib.request.Request(LUMAR_API, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"Lumar HTTP {e.code}: {e.read().decode(errors='replace')[:400]}\n")
        raise
    if "errors" in data and data["errors"]:
        raise RuntimeError(f"Lumar GraphQL error: {json.dumps(data['errors'])[:600]}")
    return data["data"]


def csv_safe(s: str) -> str:
    if "," not in s and '"' not in s and "\n" not in s:
        return s
    return '"' + s.replace('"', '""') + '"'


def http_put(url: str, body: bytes) -> None:
    """PUT body to S3 signed URL. No extra headers (X-Amz-SignedHeaders=host)."""
    req = urllib.request.Request(url, data=body, method="PUT")
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status != 200:
            raise RuntimeError(f"S3 PUT failed: {r.status} {r.read().decode(errors='replace')[:400]}")


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

def main() -> int:
    # 1. Figure out report date (end-of-window) and window length
    requested = os.environ.get("REPORT_DATE", "").strip()
    if requested:
        try:
            report_date = datetime.strptime(requested, "%Y-%m-%d").date()
        except ValueError:
            log(f"Invalid REPORT_DATE='{requested}'. Use YYYY-MM-DD.")
            return 1
    else:
        report_date = (datetime.now(timezone.utc) - timedelta(days=1)).date()

    # WINDOW_DAYS controls how many days to roll up ending at report_date.
    # Default 1 = single-day push (same as before). Lumar accepts the aggregate.
    try:
        window_days = max(1, int(os.environ.get("WINDOW_DAYS", "1").strip() or "1"))
    except ValueError:
        log(f"Invalid WINDOW_DAYS='{os.environ.get('WINDOW_DAYS','')}'. Falling back to 1.")
        window_days = 1
    start_date = report_date - timedelta(days=window_days - 1)

    project_id = os.environ["LUMAR_PROJECT_ID"]
    gcp_project = os.environ["GCP_PROJECT"]
    gcp_dataset = os.environ["GCP_DATASET"]

    label = (f"{report_date}" if window_days == 1
             else f"{start_date}..{report_date} ({window_days}d)")
    log(f"Push for window={label}  ·  Lumar project={project_id}")
    log(f"BigQuery: {gcp_project}.{gcp_dataset}")

    bq = bigquery.Client(project=gcp_project)

    # 2. Lumar auth
    log("Authenticating to Lumar…")
    secret_raw = os.environ["LUMAR_USER_KEY_SECRET"]
    key_raw = os.environ["LUMAR_USER_KEY_ID"]
    # Aggressive whitespace strip + filter to expected charsets to defeat any
    # stray newline/CR/space from secret storage.
    import re
    secret = re.sub(r'[^0-9a-fA-F]', '', secret_raw)
    user_key_id = re.sub(r'[^0-9]', '', key_raw)
    log(f"  key len raw={len(key_raw)} clean={len(user_key_id)}; "
        f"secret len raw={len(secret_raw)} clean={len(secret)}")
    inline_mutation = (
        'mutation { createSessionUsingUserKey(input: '
        '{secret: "' + secret + '", userKeyId: "' + user_key_id + '"}) '
        '{ token } }'
    )
    try:
        auth = graphql(None, inline_mutation, None)
        token = auth["createSessionUsingUserKey"]["token"]
        log(f"  ✓ Got session token (len={len(token)})")
    except Exception as e:
        log(f"  ✗ Lumar auth FAILED: {e}")
        return 2

    # 2b. Dedup: delete any prior uploads whose filename starts with our
    # window-specific stem. This protects against partial-failure retries
    # leaving orphan duplicates in Lumar. Idempotent: a clean re-run finds
    # nothing to delete and continues.
    suffix_for_window = (report_date.isoformat() if window_days == 1
                         else f"{start_date.isoformat()}_to_{report_date.isoformat()}")
    stems = [
        f"drivewayz-ai-bot-requests-{suffix_for_window}",
        f"drivewayz-log-summary-{suffix_for_window}",
    ]
    log(f"Dedup: looking for prior uploads matching {stems}…")
    try:
        existing = graphql(token, (
            'query { getProject(id: "' + project_id + '") {'
            '  urlFileUploads(first: 100) {'
            '    nodes { id fileName status }'
            '  }'
            '} }'
        ))
        prior = [n for n in existing["getProject"]["urlFileUploads"]["nodes"]
                 if any(n["fileName"].startswith(stem) for stem in stems)]
        log(f"  found {len(prior)} prior upload(s) to remove")
        for n in prior:
            try:
                graphql(token, (
                    'mutation Del($id: ObjectID!) {'
                    '  deleteUrlFileUpload(input: {urlFileUploadId: $id}) {'
                    '    urlFileUpload { id }'
                    '  }'
                    '}'
                ), {"id": n["id"]})
                log(f"  ✓ deleted {n['fileName']} (id={n['id']})")
            except Exception as e:
                log(f"  ⚠ could not delete {n['fileName']}: {e}")
    except Exception as e:
        log(f"  ⚠ dedup probe failed (continuing anyway): {e}")

    # 3. AI Bot Requests (rolled up across the window per url + aiBot)
    log("Querying ai_bot_requests_daily…")
    ai_rows = list(bq.query(f"""
        SELECT url, aiBot, SUM(logRequests) AS logRequests
        FROM `{gcp_project}.{gcp_dataset}.ai_bot_requests_daily`
        WHERE report_date BETWEEN DATE('{start_date.isoformat()}')
                              AND DATE('{report_date.isoformat()}')
        GROUP BY url, aiBot
        ORDER BY logRequests DESC
    """).result())
    log(f"  → {len(ai_rows)} rows")

    ai_upload_id = None
    if ai_rows:
        # Build CSV
        lines = ["url,aiBot,logRequests"]
        for r in ai_rows:
            lines.append(f"{csv_safe(r.url)},{csv_safe(r.aiBot)},{r.logRequests}")
        csv = "\n".join(lines)

        suffix = (report_date.isoformat() if window_days == 1
                  else f"{start_date.isoformat()}_to_{report_date.isoformat()}")
        file_name = f"drivewayz-ai-bot-requests-{suffix}.csv"
        log(f"Creating signed upload for {file_name}…")
        try:
            res = graphql(token, (
                "mutation Up($pid: ObjectID!, $ft: String!, $pt: ProjectUploadType!) {"
                "  createSignedUrlFileUpload(input: {"
                "    projectId: $pid, crawlTypeCode: LogSummary, enabled: true,"
                "    fileName: $ft, projectUploadType: $pt"
                "  }) { signedS3UploadUrl urlFileUpload { id } }"
                "}"
            ), {"pid": project_id, "ft": file_name, "pt": "AIBotLogRequests"})
            up = res["createSignedUrlFileUpload"]
            ai_upload_id = up["urlFileUpload"]["id"]
            log(f"  → upload id {ai_upload_id}")
            log("PUTting CSV to S3…")
            http_put(up["signedS3UploadUrl"], csv.encode("utf-8"))
            log(f"  ✓ AI bot CSV uploaded ({len(csv)} bytes)")
        except Exception as e:
            log(f"  ✗ AI bot upload FAILED: {e}")
            return 2
    else:
        log("  (skipped — no rows)")

    # 4. Log Summary (rolled up across the window per url)
    log("Querying log_summary_daily…")
    ls_rows = list(bq.query(f"""
        WITH agg AS (
          SELECT
            url,
            SUM(desktop_bot_request_count) AS desktop_bot_request_count,
            SUM(mobile_bot_request_count)  AS mobile_bot_request_count
          FROM `{gcp_project}.{gcp_dataset}.log_summary_daily`
          WHERE report_date BETWEEN DATE('{start_date.isoformat()}')
                                AND DATE('{report_date.isoformat()}')
          GROUP BY url
        )
        SELECT url, desktop_bot_request_count, mobile_bot_request_count
        FROM agg
        ORDER BY (desktop_bot_request_count + mobile_bot_request_count) DESC
    """).result())
    log(f"  → {len(ls_rows)} rows")

    ls_upload_id = None
    if ls_rows:
        lines = ["url,desktop bot request count,mobile bot request count"]
        for r in ls_rows:
            lines.append(
                f"{csv_safe(r.url)},{r.desktop_bot_request_count},{r.mobile_bot_request_count}"
            )
        csv = "\n".join(lines)

        suffix = (report_date.isoformat() if window_days == 1
                  else f"{start_date.isoformat()}_to_{report_date.isoformat()}")
        file_name = f"drivewayz-log-summary-{suffix}.csv"
        log(f"Creating signed upload for {file_name}…")
        try:
            res = graphql(token, (
                "mutation Up($pid: ObjectID!, $ft: String!, $pt: ProjectUploadType!) {"
                "  createSignedUrlFileUpload(input: {"
                "    projectId: $pid, crawlTypeCode: LogSummary, enabled: true,"
                "    fileName: $ft, projectUploadType: $pt"
                "  }) { signedS3UploadUrl urlFileUpload { id } }"
                "}"
            ), {"pid": project_id, "ft": file_name, "pt": "GenericLogfileCSV"})
            up = res["createSignedUrlFileUpload"]
            ls_upload_id = up["urlFileUpload"]["id"]
            log(f"  → upload id {ls_upload_id}")
            log("PUTting CSV to S3…")
            http_put(up["signedS3UploadUrl"], csv.encode("utf-8"))
            log(f"  ✓ Log summary CSV uploaded ({len(csv)} bytes)")
        except Exception as e:
            log(f"  ✗ Log summary upload FAILED: {e}")
            return 2
    else:
        log("  (skipped — no rows)")

    # 5. Verify both Processed (poll up to 30s each)
    log("Verifying ingestion in Lumar…")
    def verify(uid: str | None, label: str) -> None:
        if not uid:
            log(f"  {label}: nothing to verify (skipped)")
            return
        for attempt in range(8):  # ~30s total at 4s intervals
            try:
                res = graphql(token, (
                    "query { getProject(id: \"" + project_id + "\") {"
                    "  urlFileUploads(first: 30) {"
                    "    nodes { id status totalRows errorMessage }"
                    "  }"
                    "} }"
                ))
                for n in res["getProject"]["urlFileUploads"]["nodes"]:
                    if n["id"] == uid:
                        if n["status"] == "Processed":
                            log(f"  ✓ {label}: Processed ({n.get('totalRows')} rows)")
                            return
                        if n["status"] in ("Errored", "Failed"):
                            log(f"  ✗ {label}: {n['status']} — {n.get('errorMessage')}")
                            return
                        # Still Processing / Draft → wait
                        break
            except Exception as e:
                log(f"  ⚠ verify attempt {attempt+1} errored: {e}")
            time.sleep(4)
        log(f"  ⚠ {label}: still not Processed after 30s — check Lumar UI")

    verify(ai_upload_id, "AI bot CSV")
    verify(ls_upload_id, "Log summary CSV")

    log("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
