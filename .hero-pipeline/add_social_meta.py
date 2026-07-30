#!/usr/bin/env python3
"""
Phase 5c — Add Open Graph + Twitter Card meta tags to guide pages.

For every page with a hero <img class="guide-hero-img">, injects:
  og:title, og:description, og:image, og:url,
  twitter:card, twitter:image

into <head> immediately after the existing <meta name="description">.

Idempotent: pages that already have og:image are skipped.
Pages without a hero img (gradient heroes, logo-only hubs) are skipped.

Usage (from repo root):
    python3 .hero-pipeline/add_social_meta.py --dry-run
    python3 .hero-pipeline/add_social_meta.py --dry-run --slug some-guide-slug
    python3 .hero-pipeline/add_social_meta.py --limit 25
    python3 .hero-pipeline/add_social_meta.py
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
MANIFEST = HERE / "render_manifest.csv"
LOG = HERE / "social_meta_log.csv"
SITE_ORIGIN = "https://drivewayzusa.co"
PROGRESS_EVERY = 50

# Primary hero marker used on guide pages (Phase 3b corpus + a few
# pre-migration pages that still have the class with a non-/heroes/ src).
HERO_IMG_RE = re.compile(
    r'<img src="([^"]*)" alt="([^"]*)" class="guide-hero-img"[^>]*>'
)

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

# Strip branded suffixes so og:title stays short for social previews.
BRAND_SUFFIX_RE = re.compile(
    r"\s*(?:[|—–-]\s*)Drivewayz\s*USA?\s*$",
    re.I,
)

# Top-level pages to consider in addition to guides/. Most already have
# og:image (homepage, for-homeowners, …) or lack a natural hero
# (guides-hub, privacy-policy) and will be skipped by the idempotent /
# no-hero paths.
EXTRA_PAGES = [
    ("", REPO / "index.html"),                          # homepage
    ("guides-hub", REPO / "guides-hub" / "index.html"),
    ("for-homeowners", REPO / "for-homeowners" / "index.html"),
    ("for-contractors", REPO / "for-contractors" / "index.html"),
    ("locations", REPO / "locations" / "index.html"),
    ("cost-calculator", REPO / "cost-calculator" / "index.html"),
    ("niches", REPO / "niches" / "index.html"),
    ("privacy-policy", REPO / "privacy-policy" / "index.html"),
]

LOG_FIELDS = [
    "timestamp", "slug", "html_path", "status",
    "og_title", "og_image", "og_url", "notes",
]


def parse_args():
    p = argparse.ArgumentParser(description="Add og/twitter social meta tags.")
    p.add_argument("--dry-run", action="store_true",
                   help="Report what would change; write nothing.")
    p.add_argument("--limit", type=int, default=None,
                   help="Only process the first N pages.")
    p.add_argument("--slug", default=None,
                   help="Only process this one slug (guide slug or '' for homepage).")
    return p.parse_args()


def discover_pages(args):
    """All guides/*/index.html plus a short list of top-level candidates."""
    pages = []
    for path in sorted((REPO / "guides").glob("*/index.html")):
        pages.append((path.parent.name, path))
    for slug, path in EXTRA_PAGES:
        if path.exists():
            pages.append((slug, path))

    if args.slug is not None:
        pages = [p for p in pages if p[0] == args.slug]
        if not pages:
            sys.exit(f"ERROR: slug not found among discoverable pages: {args.slug!r}")
    if args.limit:
        pages = pages[: args.limit]
    return pages


def strip_brand(title):
    title = html_mod.unescape((title or "").strip())
    return BRAND_SUFFIX_RE.sub("", title).strip()


def absolutize(src):
    """Turn a site-relative /images/... path into an absolute URL."""
    src = (src or "").strip()
    if src.startswith("http://") or src.startswith("https://"):
        return src
    if not src.startswith("/"):
        src = "/" + src
    return SITE_ORIGIN + src


def shorten(text, width=70):
    text = text or ""
    return text if len(text) <= width else text[: width - 1] + "\u2026"


def og_type_for(path):
    """Guides get article; homepage / hubs / top-level pages get website."""
    try:
        rel = path.relative_to(REPO)
    except ValueError:
        rel = path
    parts = rel.parts
    if parts and parts[0] == "guides":
        return "article"
    return "website"


def build_meta_block(og_title, og_description, og_image, og_url, og_type="article"):
    # Escape attribute values. Descriptions already contain entities like
    # &amp; in the source HTML — unescape then re-escape so we don't
    # double-encode (&amp;amp;).
    def esc(s):
        return html_mod.escape(html_mod.unescape(s), quote=True)

    lines = [
        f'  <meta property="og:title" content="{esc(og_title)}">',
        f'  <meta property="og:description" content="{esc(og_description)}">',
        f'  <meta property="og:image" content="{esc(og_image)}">',
        f'  <meta property="og:url" content="{esc(og_url)}">',
        f'  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:image" content="{esc(og_image)}">',
        f'  <meta property="og:type" content="{esc(og_type)}">',
    ]
    return "\n".join(lines)


def process_page(slug, path, dry_run):
    rel_path = str(path.relative_to(REPO))

    def done(status, **extra):
        return {
            "timestamp": datetime.now().isoformat(),
            "slug": slug or "(homepage)",
            "html_path": rel_path,
            "status": status,
            "og_title": "",
            "og_image": "",
            "og_url": "",
            "notes": "",
            "meta_block": "",
            **extra,
        }

    if not path.exists():
        return done("skipped", notes="html_not_found")

    original = path.read_text(encoding="utf-8")

    if OG_IMAGE_RE.search(original):
        return done("already_present", notes="og:image already in <head>")

    hero = HERO_IMG_RE.search(original)
    if not hero:
        return done("skipped", notes="hero_img_not_found")

    img_src, img_alt = hero.group(1), hero.group(2)

    title_m = TITLE_RE.search(original)
    if not title_m:
        return done("skipped", notes="title_not_found")

    desc_m = DESC_RE.search(original)
    if not desc_m:
        return done("skipped", notes="description_not_found")

    canon_m = CANONICAL_RE.search(original)
    if not canon_m:
        return done("skipped", notes="canonical_not_found")

    og_title = strip_brand(title_m.group(1))
    og_description = html_mod.unescape(desc_m.group(2))
    og_image = absolutize(img_src)
    og_url = canon_m.group(1).strip()
    og_type = og_type_for(path)

    meta_block = build_meta_block(
        og_title, og_description, og_image, og_url, og_type=og_type,
    )

    # Insert immediately after the full <meta name="description" ...> match.
    insert_at = desc_m.end()
    updated = original[:insert_at] + "\n" + meta_block + original[insert_at:]

    if not dry_run:
        path.write_text(updated, encoding="utf-8")

    return done(
        "injected",
        og_title=og_title,
        og_image=og_image,
        og_url=og_url,
        notes=f"alt={shorten(img_alt, 50)}",
        meta_block=meta_block,
    )


def print_dry_run(result, index, total):
    print(f"[{index}/{total}] {result['slug']}")
    if result["status"] == "skipped":
        print(f"    SKIP: {result['notes']}")
        return
    if result["status"] == "already_present":
        print(f"    already has og:image — no change")
        return
    print(f"    og:title = {shorten(result['og_title'])}")
    print(f"    og:image = {result['og_image']}")
    print(f"    og:url   = {result['og_url']}")
    if result.get("meta_block") and total <= 5:
        # Full block only when the run is tiny (single-slug / tiny limit).
        print("    --- tags that would be inserted ---")
        for line in result["meta_block"].splitlines():
            print(f"    {line}")


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
    pages = discover_pages(args)
    total = len(pages)

    # Manifest is loaded for provenance / future use; injection reads live HTML.
    if MANIFEST.exists():
        with open(MANIFEST, encoding="utf-8") as f:
            manifest_slugs = {r["slug"] for r in csv.DictReader(f)}
    else:
        manifest_slugs = set()

    mode = "DRY RUN (no files written)" if args.dry_run else "LIVE (files will be modified)"
    print("=" * 70)
    print("Phase 5c — social meta (og:image / twitter:image)")
    print(f"Mode:     {mode}")
    print(f"Started:  {datetime.now().isoformat()}")
    print(f"Pages:    {total}")
    print(f"Manifest: {len(manifest_slugs)} slugs on file")
    print("=" * 70)

    results = []
    for i, (slug, path) in enumerate(pages, 1):
        result = process_page(slug, path, args.dry_run)
        results.append(result)

        if args.dry_run:
            # Always print for single-slug; otherwise sample + progress.
            if args.slug is not None or total <= 5:
                print_dry_run(result, i, total)
            elif i <= 3 and result["status"] == "injected":
                print_dry_run(result, i, total)
            elif i % PROGRESS_EVERY == 0 or i == total:
                ok = sum(1 for r in results if r["status"] == "injected")
                skip = sum(1 for r in results if r["status"] == "skipped")
                already = sum(1 for r in results if r["status"] == "already_present")
                print(f"  [{i}/{total}] {ok} would-inject, {skip} skipped, {already} already")
        elif i % PROGRESS_EVERY == 0 or i == total:
            ok = sum(1 for r in results if r["status"] == "injected")
            skip = sum(1 for r in results if r["status"] == "skipped")
            already = sum(1 for r in results if r["status"] == "already_present")
            print(f"  [{i}/{total}] {ok} injected, {skip} skipped, {already} already")

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    print()
    print("=" * 70)
    print(f"{'DRY RUN' if args.dry_run else 'INJECT'} COMPLETE — {datetime.now().isoformat()}")
    print(f"  Pages scanned: {total}")
    for status, label in (
        ("injected", "Would inject" if args.dry_run else "Injected"),
        ("already_present", "Already present"),
        ("skipped", "Skipped"),
    ):
        if counts.get(status):
            print(f"  {label}: {counts[status]}")

    skipped = [r for r in results if r["status"] == "skipped"]
    if skipped:
        print(f"\n  Skipped breakdown ({len(skipped)}):")
        by_reason = {}
        for s in skipped:
            by_reason.setdefault(s["notes"], []).append(s["slug"])
        for reason, slugs in sorted(by_reason.items(), key=lambda kv: -len(kv[1])):
            print(f"    {reason}: {len(slugs)}")
            for s in slugs[:5]:
                print(f"      - {s}")
            if len(slugs) > 5:
                print(f"      ... and {len(slugs) - 5} more")

    samples = [r for r in results if r["status"] == "injected"][:3]
    if samples and not (args.slug is not None or total <= 5):
        print("\n  First 3 successful injections:")
        for r in samples:
            print(f"    [{r['slug']}]")
            print(f"      og:title = {shorten(r['og_title'])}")
            print(f"      og:image = {r['og_image']}")
            print(f"      og:url   = {r['og_url']}")

    if args.dry_run:
        print("\n  (dry run — no HTML and no log files were written)")
    else:
        written = write_log(results)
        print(f"\n  Log written: {LOG.name if written else 'none'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
