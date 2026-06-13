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
    # 1. Figure out report date
    requested = os.environ.get("REPORT_DATE", "").strip()
    if requested:
        try:
            report_date = datetime.strptime(requested, "%Y-%m-%d").date()
        except ValueError:
            log(f"Invalid REPORT_DATE='{requested}'. Use YYYY-MM-DD.")
            return 1
    else:
        report_date = (datetime.now(timezone.utc) - timedelta(days=1)).date()

    project_id = os.environ["LUMAR_PROJECT_ID"]
    gcp_project = os.environ["GCP_PROJECT"]
    gcp_dataset = os.environ["GCP_DATASET"]

    log(f"Push for report_date={report_date}  ·  Lumar project={project_id}")
    log(f"BigQuery: {gcp_project}.{gcp_dataset}")

    bq = bigquery.Client(project=gcp_project)

    # 2. Lumar auth
    log("Authenticating to Lumar…")
    secret = os.environ["LUMAR_USER_KEY_SECRET"].strip()
    user_key_id_raw = os.environ["LUMAR_USER_KEY_ID"].strip()
    # Lumar's ObjectID! scalar accepts an integer for numeric user-key IDs.
    # Send as int if numeric, else fall back to string.
    try:
        user_key_id = int(user_key_id_raw)
    except ValueError:
        user_key_id = user_key_id_raw
    try:
        auth = graphql(None, (
            "mutation Auth($s: String!, $u: ObjectID!) {"
            "  createSessionUsingUserKey(input: {secret: $s, userKeyId: $u}) { token }"
            "}"
        ), {"s": secret, "u": user_key_id})
        token = auth["createSessionUsingUserKey"]["token"]
        log(f"  ✓ Got session token (len={len(token)})")
    except Exception as e:
        log(f"  ✗ Lumar auth FAILED: {e}")
        return 2

    # 3. AI Bot Requests
    log("Querying ai_bot_requests_daily…")
    ai_rows = list(bq.query(f"""
        SELECT url, aiBot, logRequests
        FROM `{gcp_project}.{gcp_dataset}.ai_bot_requests_daily`
        WHERE report_date = DATE('{report_date.isoformat()}')
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

        file_name = f"drivewayz-ai-bot-requests-{report_date.isoformat()}.csv"
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

    # 4. Log Summary
    log("Querying log_summary_daily…")
    ls_rows = list(bq.query(f"""
        SELECT url, desktop_bot_request_count, mobile_bot_request_count
        FROM `{gcp_project}.{gcp_dataset}.log_summary_daily`
        WHERE report_date = DATE('{report_date.isoformat()}')
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

        file_name = f"drivewayz-log-summary-{report_date.isoformat()}.csv"
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
