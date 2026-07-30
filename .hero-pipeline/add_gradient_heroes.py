#!/usr/bin/env python3
"""
Phase 5d — Insert hero <img> markup on the 19 gradient-hero guide pages.

Unlike Phase 3b (swap), these pages have no <img class="guide-hero-img">.
This script inserts one as the first child of <section class="guide-hero">,
then updates JSON-LD image, optional inline CSS url(), and adds the same
7 og/twitter meta tags Phase 5c applied to the other guides.

Assignments live in gradient_hero_assignments.csv (reuses existing
/images/heroes/ renders — zero API cost).

Usage (from repo root):
    python3 .hero-pipeline/add_gradient_heroes.py --dry-run
    python3 .hero-pipeline/add_gradient_heroes.py --dry-run --slug concrete-repair
    python3 .hero-pipeline/add_gradient_heroes.py
"""

import argparse
import csv
import html as html_mod
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent
ASSIGNMENTS = HERE / "gradient_hero_assignments.csv"
LOG = HERE / "gradient_heroes_log.csv"
HEROES_DIR = REPO / "images" / "heroes"
SITE_ORIGIN = "https://drivewayzusa.co"
HERO_URL_BASE = "/images/heroes/"

SECTION_OPEN_RE = re.compile(r'<section class="guide-hero">')
HERO_IMG_RE = re.compile(
    r'<img src="([^"]*)" alt="([^"]*)" class="guide-hero-img"[^>]*>'
)

JSONLD_PATTERNS = [
    ("string", re.compile(r'("image"\s*:\s*")([^"]+)(")')),
    ("array", re.compile(r'("image"\s*:\s*\[\s*")([^"]+)(")')),
    ("object", re.compile(r'("image"\s*:\s*\{[^}]*?"url"\s*:\s*")([^"]+)(")', re.S)),
]

GUIDE_HERO_RULE_RE = re.compile(r"\.guide-hero\s*\{[^}]*\}")
CSS_IMG_URL_RE = re.compile(r"""url\((['"]?)(/images/[^'")]+)(['"]?)\)""")

TITLE_RE = re.compile(r"<title>([^<]*)</title>", re.I)
DESC_RE = re.compile(
    r'(<meta\s+name="description"\s+content="([^"]*)"\s*/?>)',
    re.I,
)
CANONICAL_RE = re.compile(
    r'<link\s+rel="canonical"\s+href="([^"]*)"\s*/?>',
    re.I,
)
OG_IMAGE_RE = re.compile(r'property=["\']og:image["\']', re.I)
BRAND_SUFFIX_RE = re.compile(
    r"\s*(?:[|—–-]\s*)Drivewayz\s*USA?\s*$",
    re.I,
)

LOG_FIELDS = [
    "timestamp", "slug", "status",
    "img_inserted", "jsonld_updated", "css_updated", "meta_added", "notes",
]


def parse_args():
    p = argparse.ArgumentParser(description="Insert heroes on gradient pages.")
    p.add_argument("--dry-run", action="store_true",
                   help="Report what would change; write nothing.")
    p.add_argument("--slug", default=None,
                   help="Only process this one slug.")
    return p.parse_args()


def load_assignments(slug_filter=None):
    if not ASSIGNMENTS.exists():
        sys.exit(f"ERROR: assignments not found at {ASSIGNMENTS}")
    with open(ASSIGNMENTS, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if slug_filter:
        rows = [r for r in rows if r["slug"] == slug_filter]
        if not rows:
            sys.exit(f"ERROR: slug not in assignments: {slug_filter}")
    return rows


def strip_brand(title):
    title = html_mod.unescape((title or "").strip())
    return BRAND_SUFFIX_RE.sub("", title).strip()


def build_meta_block(og_title, og_description, og_image, og_url):
    def esc(s):
        return html_mod.escape(html_mod.unescape(s), quote=True)

    lines = [
        f'  <meta property="og:title" content="{esc(og_title)}">',
        f'  <meta property="og:description" content="{esc(og_description)}">',
        f'  <meta property="og:image" content="{esc(og_image)}">',
        f'  <meta property="og:url" content="{esc(og_url)}">',
        f'  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:image" content="{esc(og_image)}">',
        f'  <meta property="og:type" content="article">',
    ]
    return "\n".join(lines)


def update_inline_css(text, new_src):
    """Replace url() inside a .guide-hero rule. Returns (text, found, old_url)."""
    for rule_match in GUIDE_HERO_RULE_RE.finditer(text):
        rule = rule_match.group(0)
        url_match = CSS_IMG_URL_RE.search(rule)
        if not url_match:
            continue
        old_url = url_match.group(2)
        if old_url == new_src:
            return text, True, old_url
        new_rule = (
            rule[: url_match.start()]
            + f"url('{new_src}')"
            + rule[url_match.end() :]
        )
        return (
            text[: rule_match.start()] + new_rule + text[rule_match.end() :],
            True,
            old_url,
        )
    return text, False, ""


def detect_child_indent(html, section_end):
    """Indent of the first non-empty line after <section class="guide-hero">."""
    rest = html[section_end:]
    m = re.match(r"\n([ \t]*)\S", rest)
    if m:
        return m.group(1)
    return "  "


def process_row(row, dry_run):
    slug = row["slug"]
    hero = row["assigned_hero"]
    alt = (row["alt"] or "").strip()
    new_src = HERO_URL_BASE + hero
    new_jsonld = f"{SITE_ORIGIN}{new_src}"
    rel_path = f"guides/{slug}/index.html"
    path = REPO / rel_path

    result = {
        "timestamp": datetime.now().isoformat(),
        "slug": slug,
        "status": "",
        "img_inserted": "false",
        "jsonld_updated": "false",
        "css_updated": "false",
        "meta_added": "false",
        "notes": "",
        "html_path": rel_path,
        "diff_preview": "",
        "warnings": [],
    }

    if not path.exists():
        result["status"] = "skipped"
        result["notes"] = "html_not_found"
        return result

    hero_file = HEROES_DIR / hero
    if not hero_file.exists():
        result["status"] = "skipped"
        result["notes"] = f"hero_file_missing:{hero}"
        return result

    original = path.read_text(encoding="utf-8")
    updated = original
    notes = []

    # --- section ---
    sections = list(SECTION_OPEN_RE.finditer(updated))
    if len(sections) == 0:
        result["status"] = "skipped"
        result["notes"] = "section_not_found"
        return result
    if len(sections) > 1:
        result["status"] = "skipped"
        result["notes"] = f"multiple_sections:{len(sections)}"
        return result

    # --- already has hero img? ---
    if HERO_IMG_RE.search(updated):
        result["status"] = "already_has_hero_img"
        result["notes"] = "idempotent skip"
        return result

    # --- insert <img> as first child of section ---
    sec = sections[0]
    indent = detect_child_indent(updated, sec.end())
    img_tag = (
        f'<img src="{new_src}" '
        f'alt="{html_mod.escape(alt, quote=True)}" '
        f'class="guide-hero-img" width="1200" height="630" '
        f'loading="eager" fetchpriority="high">'
    )
    insertion = f"\n{indent}{img_tag}"
    updated = updated[: sec.end()] + insertion + updated[sec.end() :]
    result["img_inserted"] = "true"
    notes.append(f"img→{hero}")

    # --- JSON-LD ---
    jsonld_ok = False
    for shape, pattern in JSONLD_PATTERNS:
        jm = pattern.search(updated)
        if jm:
            updated = (
                updated[: jm.start()]
                + jm.group(1)
                + new_jsonld
                + jm.group(3)
                + updated[jm.end() :]
            )
            result["jsonld_updated"] = "true"
            notes.append(f"jsonld={shape}")
            jsonld_ok = True
            break
    if not jsonld_ok:
        result["warnings"].append("jsonld_image_missing")
        notes.append("jsonld_image_missing")

    # --- inline CSS ---
    # Most of these 19 pages are pure-gradient (no url() at all). A miss is
    # expected and recorded in notes only — not a warning.
    updated, css_found, css_old = update_inline_css(updated, new_src)
    if css_found:
        result["css_updated"] = "true"
        notes.append(f"css:{Path(css_old).name}→{hero}")
    else:
        notes.append("inline_css_url_not_found")

    # --- social meta (same 7 tags as Phase 5c) ---
    if OG_IMAGE_RE.search(updated):
        notes.append("meta_already_present")
    else:
        title_m = TITLE_RE.search(updated)
        desc_m = DESC_RE.search(updated)
        canon_m = CANONICAL_RE.search(updated)
        if not (title_m and desc_m and canon_m):
            result["warnings"].append("meta_fields_incomplete")
            notes.append("meta_fields_incomplete")
        else:
            meta_block = build_meta_block(
                strip_brand(title_m.group(1)),
                html_mod.unescape(desc_m.group(2)),
                new_jsonld,
                canon_m.group(1).strip(),
            )
            insert_at = desc_m.end()
            updated = updated[:insert_at] + "\n" + meta_block + updated[insert_at:]
            result["meta_added"] = "true"
            notes.append("meta_added")

    if not dry_run:
        path.write_text(updated, encoding="utf-8")

    result["status"] = "updated"
    result["notes"] = "; ".join(notes)
    result["diff_preview"] = updated  # caller may diff against original
    result["original"] = original
    return result


def make_unified_diff(original, updated, path_label):
    import difflib
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=f"a/{path_label}",
            tofile=f"b/{path_label}",
            n=3,
        )
    )


def write_log(rows):
    if not rows:
        return False
    with open(LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in LOG_FIELDS})
    return True


def main():
    args = parse_args()
    rows = load_assignments(args.slug)
    total = len(rows)

    mode = "DRY RUN (no files written)" if args.dry_run else "LIVE (files will be modified)"
    print("=" * 70)
    print("Phase 5d — gradient hero insertion")
    print(f"Mode:    {mode}")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Pages:   {total}")
    print("=" * 70)

    results = []
    for i, row in enumerate(rows, 1):
        result = process_row(row, args.dry_run)
        results.append(result)

        print(f"[{i}/{total}] {result['slug']} — {result['status']}")
        print(f"    img={result['img_inserted']} jsonld={result['jsonld_updated']} "
              f"css={result['css_updated']} meta={result['meta_added']}")
        if result["notes"]:
            print(f"    notes: {result['notes']}")

        if args.dry_run and args.slug and result.get("original") is not None:
            diff = make_unified_diff(
                result["original"], result["diff_preview"], result["html_path"]
            )
            print()
            print("--- FULL DIFF ---")
            print(diff)
            print("--- END DIFF ---")

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    print()
    print("=" * 70)
    print(f"{'DRY RUN' if args.dry_run else 'UPDATE'} COMPLETE — {datetime.now().isoformat()}")
    print(f"  Pages processed: {total}")
    for status, n in sorted(counts.items()):
        print(f"  {status}: {n}")

    warn_count = sum(len(r.get("warnings", [])) for r in results)
    if warn_count:
        print(f"  warnings (non-fatal): {warn_count}")
        by = {}
        for r in results:
            for w in r.get("warnings", []):
                by.setdefault(w, []).append(r["slug"])
        for reason, slugs in sorted(by.items()):
            print(f"    {reason}: {len(slugs)}")
            for s in slugs[:5]:
                print(f"      - {s}")

    if args.dry_run:
        print("\n  (dry run — no HTML and no log files were written)")
    else:
        written = write_log(results)
        print(f"\n  Log written: {LOG.name if written else 'none'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
