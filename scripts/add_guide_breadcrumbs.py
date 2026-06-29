#!/usr/bin/env python3
"""Add BreadcrumbList JSON-LD to /guides/* pages. Lumar crawl 7508639 — 2026-06."""
import json
import re
import glob
import sys
from typing import Optional

SKIP_PATTERN = re.compile(r"betweenstays|between-stays", re.I)
GUIDES_GLOB = "guides/*/index.html"

BREADCRUMB_COMMENT = "  <!-- BreadcrumbList added 2026-06 — Lumar crawl 7508639 -->\n"


def clean_title(raw: str) -> str:
    for suffix in (" | Drivewayz USA", " - Drivewayzusa", " | Drivewayzusa"):
        if raw.endswith(suffix):
            return raw[: -len(suffix)].strip()
    return raw.strip()


def extract_canonical(text: str) -> Optional[str]:
    m = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', text, re.I)
    return m.group(1) if m else None


def extract_title(text: str) -> Optional[str]:
    m = re.search(r"<title>([^<]+)</title>", text, re.I)
    return clean_title(m.group(1)) if m else None


def build_breadcrumb(name: str, url: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://drivewayzusa.co/"},
            {"@type": "ListItem", "position": 2, "name": "Guides Hub", "item": "https://drivewayzusa.co/guides-hub/"},
            {"@type": "ListItem", "position": 3, "name": name, "item": url},
        ],
    }
    block = json.dumps(data, separators=(",", ":"))
    return (
        BREADCRUMB_COMMENT
        + '  <script type="application/ld+json">\n    '
        + block
        + "\n    </script>\n"
    )


def process_file(path: str, dry_run: bool = False) -> str:
    text = open(path, encoding="utf-8").read()
    if SKIP_PATTERN.search(text):
        return "skipped_betweenstays"
    if "BreadcrumbList" in text:
        return "already_has"
    if "</head>" not in text:
        return "no_head"

    canonical = extract_canonical(text)
    title = extract_title(text)
    if not canonical or not title:
        return "missing_meta"

    snippet = build_breadcrumb(title, canonical)
    new_text = text.replace("</head>", snippet + "</head>", 1)
    if not dry_run:
        open(path, "w", encoding="utf-8").write(new_text)
    return "updated"


def main():
    dry_run = "--dry-run" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("-")]

    paths = only if only else sorted(glob.glob(GUIDES_GLOB))
    counts: dict[str, int] = {}
    for path in paths:
        status = process_file(path, dry_run=dry_run)
        counts[status] = counts.get(status, 0) + 1

    print(json.dumps(counts, indent=2))
    print(f"Total files processed: {len(paths)}")


if __name__ == "__main__":
    main()
