#!/usr/bin/env python3
"""
Audit hero image uniqueness across all site pages.

Scans HTML for hero image references (guides, locations, marketing pages)
and reports duplicate image usage, missing heroes, and schema mismatches.

Outputs:
  - hero-uniqueness-audit.json  (machine-readable)
  - reports/hero-uniqueness-audit-YYYY-MM.md (human-readable summary)
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
JSON_OUTPUT = ROOT / "hero-uniqueness-audit.json"

# Directories to scan (relative paths → page type)
SCAN_ROOTS: dict[str, str] = {
    "guides": "guide",
    "locations": "location",
    "guides-hub": "hub",
    "for-homeowners": "marketing",
    "for-contractors": "marketing",
    "for-homeowners-quiz": "marketing",
    "cost-calculator": "marketing",
    "thank-you-contractor": "marketing",
    "thank-you-homeowner": "marketing",
    "privacy-policy": "marketing",
}

# Also scan root index.html
ROOT_INDEX = ROOT / "index.html"

IMAGE_URL_RE = re.compile(
    r"url\(\s*['\"]?(?:\.\./)?(/images/[^)'\"]+|/[^)'\"]+\.(?:webp|jpg|jpeg|png))['\"]?\s*\)",
    re.IGNORECASE,
)
GUIDE_HERO_IMG_RE = re.compile(
    r'<img[^>]+class=["\']guide-hero-img["\'][^>]+src=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
GUIDE_HERO_IMG_RE_ALT = re.compile(
    r'<img[^>]+src=["\']([^"\']+)["\'][^>]+class=["\']guide-hero-img["\']',
    re.IGNORECASE,
)
STATE_HERO_IMG_RE = re.compile(
    r'<img[^>]+class=["\']state-hero-img["\'][^>]+src=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
STATE_HERO_IMG_RE_ALT = re.compile(
    r'<img[^>]+src=["\']([^"\']+)["\'][^>]+class=["\']state-hero-img["\']',
    re.IGNORECASE,
)
HERO_BG_PICTURE_RE = re.compile(
    r'<picture[^>]+class=["\']hero-bg-picture["\'][^>]*>.*?<img[^>]+src=["\']([^"\']+)["\']',
    re.IGNORECASE | re.DOTALL,
)
SCHEMA_IMAGE_RE = re.compile(
    r'"image"\s*:\s*"(https?://[^"]+/images/[^"]+)"',
    re.IGNORECASE,
)
GUIDE_HERO_CSS_RE = re.compile(
    r"\.guide-hero\s*\{([^{}]*)\}",
    re.IGNORECASE | re.DOTALL,
)
STATE_HERO_CSS_RE = re.compile(
    r"\.state-hero\s*\{([^{}]*)\}",
    re.IGNORECASE | re.DOTALL,
)
GUIDES_HERO_CSS_RE = re.compile(
    r"\.guides-hero\s*\{([^{}]*)\}",
    re.IGNORECASE | re.DOTALL,
)
HERO_CSS_RE = re.compile(
    r"\.hero\s*\{([^{}]*)\}",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class PageHero:
    path: str
    page_type: str
    hero_image: str | None
    source: str  # img_tag | css_background | hero_picture | schema_only | none
    schema_image: str | None = None
    slug_mismatch: bool = False


def normalize_image(path: str) -> str:
    """Normalize to /images/filename or /root-filename for comparison."""
    path = path.strip()
    if path.startswith("http"):
        # Strip domain
        path = re.sub(r"^https?://[^/]+", "", path)
    if not path.startswith("/"):
        path = "/" + path
    return path


def extract_images_from_css_block(block: str) -> list[str]:
    return [normalize_image(m.group(1)) for m in IMAGE_URL_RE.finditer(block)]


def page_url_path(rel_path: str) -> str:
    """Convert file path to site URL path."""
    if rel_path == "index.html":
        return "/"
    parts = Path(rel_path).parts
    if parts[-1] == "index.html":
        return "/" + "/".join(parts[:-1]) + "/"
    return "/" + rel_path


def expected_guide_hero(slug: str) -> str:
    return f"/images/hero-{slug}.webp"


def extract_hero(rel_path: str, html: str, page_type: str) -> PageHero:
    slug = Path(rel_path).parent.name if rel_path.endswith("index.html") else Path(rel_path).stem

    # 1. Crawlable img tags (preferred source of truth)
    for pattern in (GUIDE_HERO_IMG_RE, GUIDE_HERO_IMG_RE_ALT):
        m = pattern.search(html)
        if m:
            hero = normalize_image(m.group(1))
            schema_m = SCHEMA_IMAGE_RE.search(html)
            schema_img = normalize_image(schema_m.group(1)) if schema_m else None
            return PageHero(rel_path, page_type, hero, "img_tag", schema_img)

    for pattern in (STATE_HERO_IMG_RE, STATE_HERO_IMG_RE_ALT):
        m = pattern.search(html)
        if m:
            hero = normalize_image(m.group(1))
            return PageHero(rel_path, page_type, hero, "img_tag")

    m = HERO_BG_PICTURE_RE.search(html)
    if m:
        return PageHero(rel_path, page_type, normalize_image(m.group(1)), "hero_picture")

    # 2. CSS background on hero selectors
    for css_re, source in (
        (GUIDE_HERO_CSS_RE, "css_background"),
        (STATE_HERO_CSS_RE, "css_background"),
        (GUIDES_HERO_CSS_RE, "css_background"),
        (HERO_CSS_RE, "css_background"),
    ):
        css_m = css_re.search(html)
        if css_m:
            imgs = extract_images_from_css_block(css_m.group(1))
            if imgs:
                schema_m = SCHEMA_IMAGE_RE.search(html)
                schema_img = normalize_image(schema_m.group(1)) if schema_m else None
                return PageHero(rel_path, page_type, imgs[-1], source, schema_img)

    # 3. Schema-only (Article image in JSON-LD)
    schema_m = SCHEMA_IMAGE_RE.search(html)
    if schema_m:
        return PageHero(rel_path, page_type, normalize_image(schema_m.group(1)), "schema_only")

    return PageHero(rel_path, page_type, None, "none")


def collect_pages() -> list[tuple[str, str]]:
    pages: list[tuple[str, str]] = []
    if ROOT_INDEX.exists():
        pages.append(("index.html", "home"))

    for dir_name, page_type in SCAN_ROOTS.items():
        base = ROOT / dir_name
        if not base.exists():
            continue
        for html_file in sorted(base.rglob("index.html")):
            if html_file.parent.name == "state-page":
                continue
            rel = html_file.relative_to(ROOT).as_posix()
            pages.append((rel, page_type))
    return pages


def main() -> None:
    pages_data: list[PageHero] = []
    by_image: dict[str, list[str]] = defaultdict(list)

    for rel_path, page_type in collect_pages():
        full = ROOT / rel_path
        html = full.read_text(encoding="utf-8", errors="ignore")
        entry = extract_hero(rel_path, html, page_type)

        # Flag guides where hero doesn't match slug-based convention
        if page_type == "guide" and entry.hero_image:
            slug = Path(rel_path).parent.name
            expected = expected_guide_hero(slug)
            entry.slug_mismatch = entry.hero_image != expected

        # Flag schema vs visible hero mismatch
        if entry.schema_image and entry.hero_image:
            if entry.schema_image != entry.hero_image:
                entry.slug_mismatch = True  # reuse flag for any mismatch

        pages_data.append(entry)
        if entry.hero_image:
            by_image[entry.hero_image].append(rel_path)

    duplicates = {
        img: sorted(paths)
        for img, paths in sorted(by_image.items(), key=lambda x: -len(x[1]))
        if len(paths) > 1
    }

    missing_hero = [p.path for p in pages_data if p.hero_image is None]
    gradient_or_missing = [
        p.path for p in pages_data if p.hero_image is None or p.source == "css_background"
    ]
    slug_mismatches = [
        {"path": p.path, "hero_image": p.hero_image, "expected": expected_guide_hero(Path(p.path).parent.name)}
        for p in pages_data
        if p.page_type == "guide" and p.slug_mismatch and p.hero_image
    ]

    # Pages sharing images with 3+ siblings are high priority
    high_priority_dupes = {img: paths for img, paths in duplicates.items() if len(paths) >= 3}

    summary = {
        "audit_date": date.today().isoformat(),
        "total_pages_scanned": len(pages_data),
        "pages_with_hero_image": sum(1 for p in pages_data if p.hero_image),
        "pages_missing_hero": len(missing_hero),
        "unique_hero_images": len(by_image),
        "duplicate_image_count": len(duplicates),
        "pages_affected_by_duplicates": sum(len(v) for v in duplicates.values()) - len(duplicates),
        "high_priority_duplicate_images": len(high_priority_dupes),
        "guide_slug_mismatches": len(slug_mismatches),
    }

    payload = {
        "summary": summary,
        "duplicates": duplicates,
        "high_priority_duplicates": high_priority_dupes,
        "missing_hero": sorted(missing_hero),
        "slug_mismatches": slug_mismatches[:100],  # cap for JSON size
        "slug_mismatch_total": len(slug_mismatches),
        "pages": [asdict(p) for p in pages_data],
    }

    JSON_OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    report_name = f"hero-uniqueness-audit-{date.today().strftime('%Y-%m')}.md"
    report_path = REPORTS_DIR / report_name
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path.write_text(build_markdown_report(summary, duplicates, high_priority_dupes, missing_hero, slug_mismatches), encoding="utf-8")

    print("=== Hero Image Uniqueness Audit ===")
    for key, val in summary.items():
        print(f"  {key}: {val}")
    print(f"\nWrote {JSON_OUTPUT.relative_to(ROOT)}")
    print(f"Wrote {report_path.relative_to(ROOT)}")


def build_markdown_report(
    summary: dict,
    duplicates: dict[str, list[str]],
    high_priority: dict[str, list[str]],
    missing_hero: list[str],
    slug_mismatches: list[dict],
) -> str:
    lines = [
        "# Hero Image Uniqueness Audit",
        "",
        f"**Audit date:** {summary['audit_date']}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|------:|",
    ]
    labels = {
        "total_pages_scanned": "Pages scanned",
        "pages_with_hero_image": "Pages with a hero image",
        "pages_missing_hero": "Pages missing hero image",
        "unique_hero_images": "Unique hero image files in use",
        "duplicate_image_count": "Images used on 2+ pages",
        "pages_affected_by_duplicates": "Extra page slots filled by reused images",
        "high_priority_duplicate_images": "Images reused on 3+ pages",
        "guide_slug_mismatches": "Guides not using slug-matched `hero-{slug}.webp`",
    }
    for key, label in labels.items():
        lines.append(f"| {label} | **{summary[key]}** |")

    lines.extend([
        "",
        "## How to read this audit",
        "",
        "- **Goal:** every indexable page should have a distinct hero image.",
        "- **Guide convention:** `/images/hero-{page-slug}.webp` (e.g. `guides/foo-bar/` → `hero-foo-bar.webp`).",
        "- **Location convention:** `/images/hero-{state-slug}.webp` (already slug-matched).",
        "- **Marketing pages:** shared stock images are acceptable only where intentional (e.g. thank-you pages).",
        "",
        "## High-priority duplicates (3+ pages)",
        "",
    ])

    if high_priority:
        for img, paths in sorted(high_priority.items(), key=lambda x: -len(x[1])):
            lines.append(f"### `{img}` — **{len(paths)} pages**")
            lines.append("")
            for p in paths[:15]:
                lines.append(f"- `{p}` → {page_url_path(p)}")
            if len(paths) > 15:
                lines.append(f"- … and {len(paths) - 15} more (see `hero-uniqueness-audit.json`)")
            lines.append("")
    else:
        lines.append("_None — no image is shared across 3 or more pages._")
        lines.append("")

    lines.extend(["## All duplicate images (2+ pages)", ""])

    if duplicates:
        shown = 0
        for img, paths in sorted(duplicates.items(), key=lambda x: -len(x[1])):
            if shown >= 25:
                lines.append(f"_… and {len(duplicates) - 25} more duplicate images in JSON output._")
                break
            lines.append(f"- `{img}` — {len(paths)} pages")
            shown += 1
    else:
        lines.append("_No duplicates found._")

    lines.extend(["", "## Pages missing hero images", ""])
    if missing_hero:
        for p in missing_hero[:30]:
            lines.append(f"- `{p}`")
        if len(missing_hero) > 30:
            lines.append(f"- … and {len(missing_hero) - 30} more")
    else:
        lines.append("_None._")

    lines.extend(["", "## Guide slug mismatches (sample)", ""])
    lines.append("Guides using a stock/shared image instead of a dedicated `hero-{slug}.webp` file.")
    lines.append("")
    if slug_mismatches:
        for item in slug_mismatches[:20]:
            lines.append(f"- `{item['path']}`")
            lines.append(f"  - Current: `{item['hero_image']}`")
            lines.append(f"  - Expected: `{item['expected']}`")
        if len(slug_mismatches) > 20:
            lines.append(f"- … and {len(slug_mismatches) - 20} more")
    else:
        lines.append("_All guides follow slug-matched naming._")

    lines.extend([
        "",
        "## Next steps",
        "",
        "1. Run `python3 scripts/audit_hero_uniqueness.py` after any hero image changes.",
        "2. For each high-priority duplicate cluster, source or generate a unique image per page.",
        "3. Name new guide images `hero-{slug}.webp` and place in `/images/`.",
        "4. Update `.guide-hero` CSS `background-image` and `<img class=\"guide-hero-img\">` together.",
        "5. Re-run until `duplicate_image_count` is limited to intentional shared pages only.",
        "",
        "## Related scripts",
        "",
        "- `scripts/hero_audit.py` — finds gradient-only heroes (no photo at all)",
        "- `scripts/build_hero_image_map.py` — keyword map for sourcing missing images",
        "- `scripts/add-hero-img.js` — inserts crawlable `<img>` tags into guide heroes",
        "",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
