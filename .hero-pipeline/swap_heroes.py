#!/usr/bin/env python3
"""
Phase 3b — Swap guide hero images to the Phase 2 renders.

For every row in render_manifest.csv, rewrites guides/{slug}/index.html:
  - hero <img>: src -> /images/heroes/{working_filename}, alt -> manifest alt
  - Article JSON-LD: "image" -> https://drivewayzusa.co/images/heroes/{working_filename}

Everything else on the img tag (class, width, height, loading, fetchpriority)
is preserved verbatim by capturing the attribute tail rather than rebuilding it.

A page is swapped atomically: if the hero img can't be identified, the page is
skipped entirely and its JSON-LD is left alone too.

Usage (from repo root):
    python3 .hero-pipeline/swap_heroes.py --dry-run
    python3 .hero-pipeline/swap_heroes.py --dry-run --slug some-guide-slug
    python3 .hero-pipeline/swap_heroes.py --limit 25
    python3 .hero-pipeline/swap_heroes.py

--dry-run writes nothing at all: no HTML, no logs.
"""

import argparse
import csv
import html as html_mod
import re
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent
MANIFEST = HERE / "render_manifest.csv"
SWAP_LOG = HERE / "swap_log.csv"
SKIPPED_LOG = HERE / "skipped_pages.csv"
WARNINGS_LOG = HERE / "warnings.csv"

ALT_COL = "intended_alt_CONSTRAINT_NOT_FINAL"
HERO_URL_BASE = "/images/heroes/"
SITE_ORIGIN = "https://drivewayzusa.co"
PROGRESS_EVERY = 25

# Hero img. Group 3 captures the attribute tail verbatim so attribute order and
# spacing survive untouched.
HERO_IMG_RE = re.compile(
    r'<img src="([^"]*)" alt="([^"]*)" class="guide-hero-img"([^>]*)>'
)

# Article JSON-LD image, three accepted shapes. Only the string form occurs in
# the current corpus; the other two are here so an upstream schema change fails
# loudly as a warning rather than silently skipping.
JSONLD_PATTERNS = [
    ("string", re.compile(r'("image"\s*:\s*")([^"]+)(")')),
    ("array", re.compile(r'("image"\s*:\s*\[\s*")([^"]+)(")')),
    ("object", re.compile(r'("image"\s*:\s*\{[^}]*?"url"\s*:\s*")([^"]+)(")', re.S)),
]

SWAP_FIELDS = [
    "timestamp", "slug", "html_path", "status", "elapsed_ms",
    "old_src", "new_src", "old_alt", "new_alt",
    "jsonld_shape", "jsonld_old", "jsonld_new", "notes",
]
SKIP_FIELDS = ["timestamp", "slug", "html_path", "reason", "detail"]
WARN_FIELDS = ["timestamp", "slug", "html_path", "reason", "detail"]


def parse_args():
    p = argparse.ArgumentParser(description="Swap guide hero images.")
    p.add_argument("--dry-run", action="store_true",
                   help="Report what would change; write nothing.")
    p.add_argument("--limit", type=int, default=None,
                   help="Only process the first N manifest rows.")
    p.add_argument("--slug", default=None,
                   help="Only process this one slug.")
    return p.parse_args()


def load_rows(args):
    if not MANIFEST.exists():
        sys.exit(f"ERROR: manifest not found at {MANIFEST}")
    with open(MANIFEST, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if args.slug:
        rows = [r for r in rows if r["slug"] == args.slug]
        if not rows:
            sys.exit(f"ERROR: slug not found in manifest: {args.slug}")
    if args.limit:
        rows = rows[:args.limit]
    return rows


def shorten(text, width=60):
    text = text or ""
    return text if len(text) <= width else text[:width - 1] + "\u2026"


def basename(url):
    return (url or "").rstrip("/").split("/")[-1]


def process_row(row, index, total, dry_run):
    """Inspect (and optionally rewrite) one page. Returns a result dict."""
    t0 = time.time()
    slug = row["slug"]
    filename = row["working_filename"]
    new_src = HERO_URL_BASE + filename
    new_alt = row[ALT_COL].strip()
    new_jsonld = f"{SITE_ORIGIN}{HERO_URL_BASE}{filename}"
    rel_path = f"guides/{slug}/index.html"
    path = REPO / rel_path

    def done(status, **extra):
        return {
            "timestamp": datetime.now().isoformat(),
            "slug": slug,
            "html_path": rel_path,
            "status": status,
            "elapsed_ms": int((time.time() - t0) * 1000),
            "old_src": "", "new_src": "", "old_alt": "", "new_alt": "",
            "jsonld_shape": "", "jsonld_old": "", "jsonld_new": "",
            "notes": "", "warning": None, "skip_detail": "",
            **extra,
        }

    if not path.exists():
        return done("skipped", notes="html_not_found", skip_detail=str(rel_path))

    original = path.read_text(encoding="utf-8")

    matches = list(HERO_IMG_RE.finditer(original))
    if len(matches) == 0:
        return done("skipped", notes="hero_img_not_found")
    if len(matches) > 1:
        return done("skipped", notes="multiple_hero_matches",
                    skip_detail=f"{len(matches)} matches")

    m = matches[0]
    old_src, old_alt, attr_tail = m.group(1), m.group(2), m.group(3)

    if old_src == new_src:
        return done("already_swapped", old_src=old_src, new_src=new_src)

    new_tag = (
        f'<img src="{new_src}" '
        f'alt="{html_mod.escape(new_alt, quote=True)}" '
        f'class="guide-hero-img"{attr_tail}>'
    )
    updated = original[:m.start()] + new_tag + original[m.end():]

    # Article JSON-LD image
    jsonld_shape = jsonld_old = ""
    warning = None
    for shape, pattern in JSONLD_PATTERNS:
        jm = pattern.search(updated)
        if jm:
            jsonld_shape = shape
            jsonld_old = jm.group(2)
            updated = updated[:jm.start()] + jm.group(1) + new_jsonld + jm.group(3) + updated[jm.end():]
            break
    else:
        warning = "jsonld_image_missing"

    if not dry_run:
        path.write_text(updated, encoding="utf-8")

    return done(
        "swapped",
        old_src=old_src, new_src=new_src,
        old_alt=old_alt, new_alt=new_alt,
        jsonld_shape=jsonld_shape, jsonld_old=jsonld_old,
        jsonld_new=new_jsonld if jsonld_shape else "",
        warning=warning,
    )


def print_dry_run(result, index, total):
    print(f"[{index}/{total}] {result['slug']}")
    if result["status"] == "skipped":
        print(f"    SKIP: {result['notes']} {result['skip_detail']}".rstrip())
        return
    if result["status"] == "already_swapped":
        print(f"    already points at {result['new_src']} — no change")
        return
    print(f"    IMG src: {basename(result['old_src'])} \u2192 {basename(result['new_src'])}")
    print(f'    IMG alt: "{shorten(result["old_alt"])}" \u2192 "{shorten(result["new_alt"])}"')
    if result["jsonld_shape"]:
        print(f"    JSON-LD: {basename(result['jsonld_old'])} \u2192 {basename(result['jsonld_new'])}")
    else:
        print("    JSON-LD: WARNING image field not found")


def write_log(path, fields, rows):
    if not rows:
        return False
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    return True


def main():
    args = parse_args()
    rows = load_rows(args)
    total = len(rows)

    mode = "DRY RUN (no files written)" if args.dry_run else "LIVE (files will be modified)"
    print("=" * 70)
    print("Phase 3b — hero swap")
    print(f"Mode:    {mode}")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Pages:   {total}")
    print("=" * 70)

    results, skipped, warnings = [], [], []

    for i, row in enumerate(rows, 1):
        result = process_row(row, i, total, args.dry_run)
        results.append(result)

        if result["status"] == "skipped":
            skipped.append({
                "timestamp": result["timestamp"], "slug": result["slug"],
                "html_path": result["html_path"], "reason": result["notes"],
                "detail": result["skip_detail"],
            })
        if result.get("warning"):
            warnings.append({
                "timestamp": result["timestamp"], "slug": result["slug"],
                "html_path": result["html_path"], "reason": result["warning"],
                "detail": "",
            })

        if args.dry_run:
            print_dry_run(result, i, total)
        elif i % PROGRESS_EVERY == 0 or i == total:
            ok = sum(1 for r in results if r["status"] == "swapped")
            print(f"  [{i}/{total}] {ok} swapped, {len(skipped)} skipped, {len(warnings)} warnings")

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    print()
    print("=" * 70)
    print(f"{'DRY RUN' if args.dry_run else 'SWAP'} COMPLETE — {datetime.now().isoformat()}")
    print(f"  Pages processed: {total}")
    for status in ("swapped", "already_swapped", "skipped"):
        if counts.get(status):
            label = "Would swap" if (args.dry_run and status == "swapped") else status.replace("_", " ").capitalize()
            print(f"  {label}: {counts[status]}")

    if skipped:
        print(f"\n  Skipped breakdown ({len(skipped)}):")
        by_reason = {}
        for s in skipped:
            by_reason.setdefault(s["reason"], []).append(s["slug"])
        for reason, slugs in sorted(by_reason.items()):
            print(f"    {reason}: {len(slugs)}")
            for s in slugs[:5]:
                print(f"      - {s}")
            if len(slugs) > 5:
                print(f"      ... and {len(slugs) - 5} more")

    if warnings:
        print(f"\n  Warnings breakdown ({len(warnings)}):")
        by_reason = {}
        for w in warnings:
            by_reason.setdefault(w["reason"], []).append(w["slug"])
        for reason, slugs in sorted(by_reason.items()):
            print(f"    {reason}: {len(slugs)}")
            for s in slugs[:5]:
                print(f"      - {s}")

    if args.dry_run:
        print("\n  (dry run — no HTML and no log files were written)")
    else:
        written = [SWAP_LOG.name] if write_log(SWAP_LOG, SWAP_FIELDS, results) else []
        if write_log(SKIPPED_LOG, SKIP_FIELDS, skipped):
            written.append(SKIPPED_LOG.name)
        if write_log(WARNINGS_LOG, WARN_FIELDS, warnings):
            written.append(WARNINGS_LOG.name)
        print(f"\n  Logs written: {', '.join(written) if written else 'none'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
