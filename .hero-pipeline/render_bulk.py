#!/usr/bin/env python3
"""
Phase 2 Bulk — Render all remaining hero images via Flux 1.1 Pro.

Renders every row in render_manifest.csv that isn't already on disk.
Safe to re-run: skips files that already exist (idempotent).

Writes a persistent bulk_log.csv with per-image status, time, cost.

Usage (from repo root):
    cd ~/Desktop/drivewayz-usa/.hero-pipeline
    export REPLICATE_API_TOKEN='r8_your_token_here'
    python3 render_bulk.py

Options:
    python3 render_bulk.py --limit 50    Only render first 50 pending
    python3 render_bulk.py --pile A      Only render pile A rows
    python3 render_bulk.py --pile B      Only render pile B rows
    python3 render_bulk.py --dry-run     Show what would be rendered, no API calls
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import replicate
    import requests
except ImportError:
    print("ERROR: dependencies missing. Run:")
    print("  pip3 install replicate requests")
    sys.exit(1)

# ---- Config ----
HERE = Path(__file__).parent
MANIFEST = HERE / "render_manifest.csv"
RENDERS_DIR = HERE / "renders"
BULK_LOG = HERE / "bulk_log.csv"

MODEL = "black-forest-labs/flux-1.1-pro"
FLUX_INPUT = {
    "aspect_ratio": "16:9",
    "output_format": "webp",
    "output_quality": 90,
    "safety_tolerance": 2,
    "prompt_upsampling": False,
}
COST_PER_IMAGE_USD = 0.04

# Between-request pause to be nice to Replicate
# Tuned up from 0.5s to 8s after observed 429 throttling on new paid accounts.
INTER_REQUEST_SLEEP = 8  # seconds

# Retry config
# More retries with longer backoff for stubborn throttling.
MAX_RETRIES_PER_IMAGE = 5
RETRY_BACKOFF_SEC = 15

# Progress checkpoint every N images (flushes log)
CHECKPOINT_EVERY = 25

# ---- Args ----
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None, help="Only render N images")
    p.add_argument("--pile", choices=["A", "B"], default=None, help="Only render one pile")
    p.add_argument("--dry-run", action="store_true", help="Show what would render, no API calls")
    return p.parse_args()

# ---- Preflight ----

def preflight():
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print("ERROR: REPLICATE_API_TOKEN not set.")
        sys.exit(1)
    if not MANIFEST.exists():
        print(f"ERROR: Manifest not found at {MANIFEST}")
        sys.exit(1)
    RENDERS_DIR.mkdir(exist_ok=True)
    print(f"[preflight] Token set ({token[:6]}...{token[-4:]})")
    print(f"[preflight] Manifest: {MANIFEST}")
    print(f"[preflight] Renders: {RENDERS_DIR}")

# ---- Load ----

def load_rows(args):
    with open(MANIFEST, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if args.pile:
        want = f"{args.pile}_REPLACE_{'PRIORITY' if args.pile == 'A' else 'BULK'}"
        rows = [r for r in rows if r["pile"] == want]
        print(f"[filter] --pile {args.pile}: {len(rows)} rows")

    # Skip rows whose file already exists
    pending = []
    existing = 0
    for r in rows:
        out = RENDERS_DIR / r["working_filename"]
        if out.exists():
            existing += 1
        else:
            pending.append(r)

    print(f"[load] Total in scope: {len(rows)}, already rendered: {existing}, pending: {len(pending)}")

    if args.limit:
        pending = pending[:args.limit]
        print(f"[limit] Capped to first {len(pending)}")

    return pending

# ---- Load existing log ----

def load_existing_log():
    if not BULK_LOG.exists():
        return []
    with open(BULK_LOG, encoding="utf-8") as f:
        return list(csv.DictReader(f))

# ---- Save log ----

def save_log(log_rows):
    if not log_rows:
        return
    with open(BULK_LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "timestamp", "slug", "working_filename", "pile",
            "status", "attempts", "elapsed_s", "cost_usd", "size_kb", "error"
        ])
        w.writeheader()
        w.writerows(log_rows)

# ---- Render one with retry ----

def render_one_with_retry(row):
    filename = row["working_filename"]
    output_path = RENDERS_DIR / filename
    payload = {**FLUX_INPUT, "prompt": row["render_prompt"]}

    last_error = None
    for attempt in range(1, MAX_RETRIES_PER_IMAGE + 1):
        t0 = time.time()
        try:
            output = replicate.run(MODEL, input=payload)
            if hasattr(output, "url"):
                image_url = output.url
            elif isinstance(output, str):
                image_url = output
            elif isinstance(output, list) and output:
                image_url = output[0].url if hasattr(output[0], "url") else output[0]
            else:
                raise ValueError(f"Unexpected output: {type(output)}")

            resp = requests.get(image_url, timeout=90)
            resp.raise_for_status()
            output_path.write_bytes(resp.content)

            elapsed = time.time() - t0
            size_kb = output_path.stat().st_size / 1024
            return {
                "status": "rendered",
                "attempts": attempt,
                "elapsed_s": round(elapsed, 1),
                "cost_usd": COST_PER_IMAGE_USD,
                "size_kb": round(size_kb, 1),
                "error": "",
            }
        except Exception as e:
            last_error = str(e)
            if attempt < MAX_RETRIES_PER_IMAGE:
                print(f"    retry {attempt}/{MAX_RETRIES_PER_IMAGE} in {RETRY_BACKOFF_SEC}s: {last_error[:80]}")
                time.sleep(RETRY_BACKOFF_SEC)
            else:
                elapsed = time.time() - t0
                return {
                    "status": "failed",
                    "attempts": attempt,
                    "elapsed_s": round(elapsed, 1),
                    "cost_usd": 0.0,
                    "size_kb": 0,
                    "error": last_error,
                }

# ---- Main ----

def main():
    args = parse_args()

    print("=" * 70)
    print(f"Phase 2 Bulk — Flux 1.1 Pro renders")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    if not args.dry_run:
        preflight()

    pending = load_rows(args)
    if not pending:
        print("Nothing to render. Exiting.")
        return

    est_cost = len(pending) * COST_PER_IMAGE_USD
    est_time_min = len(pending) * 3.5 / 60
    print(f"[plan] {len(pending)} images to render")
    print(f"[plan] Estimated cost: ${est_cost:.2f}")
    print(f"[plan] Estimated wall time: {est_time_min:.1f} min")

    if args.dry_run:
        print("\n[dry-run] Would render:")
        for r in pending[:10]:
            print(f"  {r['pile'][:1]} · {r['slug'][:60]} → {r['working_filename']}")
        if len(pending) > 10:
            print(f"  ... and {len(pending) - 10} more")
        return

    log_rows = load_existing_log()
    already_logged = {row["working_filename"] for row in log_rows if row["status"] == "rendered"}

    total_cost = 0.0
    total_elapsed = 0.0
    n_ok = 0
    n_fail = 0

    for i, row in enumerate(pending, 1):
        slug = row["slug"]
        filename = row["working_filename"]

        if filename in already_logged:
            print(f"[{i}/{len(pending)}] {slug} — already in log, skipping")
            continue

        print(f"[{i}/{len(pending)}] {row['pile'][:1]} · {slug[:55]}")
        result = render_one_with_retry(row)

        log_rows.append({
            "timestamp": datetime.now().isoformat(),
            "slug": slug,
            "working_filename": filename,
            "pile": row["pile"],
            **result,
        })

        total_cost += result["cost_usd"]
        total_elapsed += result["elapsed_s"]

        if result["status"] == "rendered":
            n_ok += 1
            print(f"    OK: {result['size_kb']} KB in {result['elapsed_s']}s (attempt {result['attempts']})")
        else:
            n_fail += 1
            print(f"    FAILED after {result['attempts']} attempts: {result['error'][:100]}")

        # Checkpoint log every N images
        if i % CHECKPOINT_EVERY == 0:
            save_log(log_rows)
            print(f"    [checkpoint] log saved ({n_ok} ok, {n_fail} failed, ${total_cost:.2f} spent)")

        time.sleep(INTER_REQUEST_SLEEP)

    # Final save
    save_log(log_rows)

    print("\n" + "=" * 70)
    print(f"BULK COMPLETE — {datetime.now().isoformat()}")
    print(f"  Rendered: {n_ok}")
    print(f"  Failed:   {n_fail}")
    print(f"  Total wall time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    print(f"  Total spend: ${total_cost:.2f}")
    print(f"  Log:      {BULK_LOG}")
    print(f"  Renders:  {RENDERS_DIR}")
    print("=" * 70)

    if n_fail:
        print("\nFAILURES (re-run this script to retry them):")
        for row in log_rows:
            if row.get("status") == "failed":
                print(f"  {row['slug']}: {row['error'][:100]}")

if __name__ == "__main__":
    main()
