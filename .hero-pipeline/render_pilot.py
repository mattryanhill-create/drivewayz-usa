#!/usr/bin/env python3
"""
Phase 2 Pilot — Render 8 hero images via Flux 1.1 Pro on Replicate.

Reads render_manifest.csv, picks top 8 pile A rows (highest impressions),
generates images via Replicate, saves .webp files to .hero-pipeline/renders/,
and writes a pilot log with elapsed time + cost per row.

Does NOT modify the original render_manifest.csv. Writes a pilot-only
status log to .hero-pipeline/pilot_log.csv.

Usage (from repo root):
    cd ~/Desktop/drivewayz-usa/.hero-pipeline
    export REPLICATE_API_TOKEN='r8_your_token_here'
    python3 render_pilot.py

Requirements:
    pip3 install replicate requests
"""

import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import replicate
except ImportError:
    print("ERROR: replicate not installed. Run:")
    print("  pip3 install replicate requests")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run:")
    print("  pip3 install replicate requests")
    sys.exit(1)

# ---- Config ----
HERE = Path(__file__).parent
MANIFEST = HERE / "render_manifest.csv"
RENDERS_DIR = HERE / "renders"
PILOT_LOG = HERE / "pilot_log.csv"

# Flux 1.1 Pro on Replicate
# Ref: https://replicate.com/black-forest-labs/flux-1.1-pro
MODEL = "black-forest-labs/flux-1.1-pro"

# 1200x630 aspect ratio (~1.9:1) is closest to Replicate's 16:9 preset
FLUX_INPUT = {
    "aspect_ratio": "16:9",
    "output_format": "webp",
    "output_quality": 90,
    "safety_tolerance": 2,     # least restrictive; hero images have no people/hands
    "prompt_upsampling": False, # keep Kimi's exact wording
}

PILOT_COUNT = 8
COST_PER_IMAGE_USD = 0.04  # Flux 1.1 Pro pricing (2026)

# ---- Preflight ----

def preflight():
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print("ERROR: REPLICATE_API_TOKEN not set.")
        print("  Get token at: https://replicate.com/account/api-tokens")
        print("  Then: export REPLICATE_API_TOKEN='r8_...'")
        sys.exit(1)

    if not MANIFEST.exists():
        print(f"ERROR: Manifest not found at {MANIFEST}")
        sys.exit(1)

    RENDERS_DIR.mkdir(exist_ok=True)
    print(f"[preflight] Token set ({token[:6]}...{token[-4:]})")
    print(f"[preflight] Manifest: {MANIFEST}")
    print(f"[preflight] Renders will save to: {RENDERS_DIR}")
    print(f"[preflight] Log will save to: {PILOT_LOG}")

# ---- Load manifest ----

def load_pilot_rows():
    with open(MANIFEST, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    pile_a = [r for r in rows if r["pile"] == "A_REPLACE_PRIORITY"]
    pilot = pile_a[:PILOT_COUNT]

    print(f"[load] Total manifest rows: {len(rows)}")
    print(f"[load] Pile A rows: {len(pile_a)}")
    print(f"[load] Pilot batch: {len(pilot)} rows")
    return pilot

# ---- Render one ----

def render_one(row, idx, total):
    slug = row["slug"]
    filename = row["working_filename"]
    render_prompt = row["render_prompt"]
    negative_prompt = row["negative_prompt"]
    output_path = RENDERS_DIR / filename

    print(f"\n[{idx}/{total}] {slug}")
    print(f"  filename: {filename}")
    print(f"  prompt:   {render_prompt[:80]}...")

    if output_path.exists():
        print(f"  SKIP: already exists at {output_path}")
        return {"status": "skipped", "elapsed_s": 0, "cost_usd": 0.0}

    payload = {
        **FLUX_INPUT,
        "prompt": render_prompt,
    }

    t0 = time.time()
    try:
        # replicate.run returns a FileOutput object (Replicate SDK >= 0.35)
        output = replicate.run(MODEL, input=payload)

        # Extract URL — SDK returns FileOutput or str depending on version
        if hasattr(output, "url"):
            image_url = output.url
        elif isinstance(output, str):
            image_url = output
        elif isinstance(output, list) and len(output) > 0:
            image_url = output[0].url if hasattr(output[0], "url") else output[0]
        else:
            raise ValueError(f"Unexpected output shape: {type(output)}: {output}")

        # Download the image
        resp = requests.get(image_url, timeout=60)
        resp.raise_for_status()
        output_path.write_bytes(resp.content)

        elapsed = time.time() - t0
        size_kb = output_path.stat().st_size / 1024
        print(f"  OK: {size_kb:.1f} KB in {elapsed:.1f}s → {output_path.name}")

        return {
            "status": "rendered",
            "elapsed_s": round(elapsed, 1),
            "cost_usd": COST_PER_IMAGE_USD,
            "size_kb": round(size_kb, 1),
            "image_url": image_url,
        }
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  FAIL after {elapsed:.1f}s: {e}")
        return {
            "status": "failed",
            "elapsed_s": round(elapsed, 1),
            "cost_usd": 0.0,
            "error": str(e),
        }

# ---- Main ----

def main():
    print("=" * 60)
    print(f"Phase 2 Pilot — {PILOT_COUNT} images via Flux 1.1 Pro")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    preflight()
    rows = load_pilot_rows()

    log_rows = []
    total_cost = 0.0
    total_elapsed = 0.0

    for i, row in enumerate(rows, 1):
        result = render_one(row, i, len(rows))
        log_rows.append({
            "slug": row["slug"],
            "working_filename": row["working_filename"],
            "status": result["status"],
            "elapsed_s": result["elapsed_s"],
            "cost_usd": result["cost_usd"],
            "size_kb": result.get("size_kb", ""),
            "error": result.get("error", ""),
        })
        total_cost += result["cost_usd"]
        total_elapsed += result["elapsed_s"]

    # Write pilot log
    with open(PILOT_LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=log_rows[0].keys())
        w.writeheader()
        w.writerows(log_rows)

    # Summary
    n_ok = sum(1 for r in log_rows if r["status"] == "rendered")
    n_skip = sum(1 for r in log_rows if r["status"] == "skipped")
    n_fail = sum(1 for r in log_rows if r["status"] == "failed")

    print("\n" + "=" * 60)
    print(f"PILOT COMPLETE — {datetime.now().isoformat()}")
    print(f"  Rendered: {n_ok}")
    print(f"  Skipped:  {n_skip}")
    print(f"  Failed:   {n_fail}")
    print(f"  Total wall time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    print(f"  Est cost: ${total_cost:.2f}")
    print(f"  Log:      {PILOT_LOG}")
    print(f"  Renders:  {RENDERS_DIR}")
    print("=" * 60)

    if n_fail:
        print("\nFAILURES:")
        for r in log_rows:
            if r["status"] == "failed":
                print(f"  {r['slug']}: {r['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
