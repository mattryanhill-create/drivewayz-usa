#!/usr/bin/env python3
"""Apply body-only internal links to high-impression target guides."""
import glob
import re
from typing import List, Optional, Tuple

TARGETS = {
    "/guides/gravel-pothole-repair/": [
        r"gravel pothole",
        r"potholes in gravel",
        r"fix potholes",
        r"pothole repair",
    ],
    "/guides/tar-and-chip-driveway-vs-asphalt-comparison/": [
        r"tar and chip",
        r"tar & chip",
    ],
    "/guides/percolation-test-for-driveway-drainage-planning/": [
        r"percolation test",
        r"perc test",
    ],
    "/guides/asphalt-rejuvenator-products-review/": [
        r"asphalt rejuvenator",
        r"rejuvenator product",
    ],
    "/guides/resurfacing-vs-replacement/": [
        r"resurfacing vs replacement",
        r"resurface or replace",
        r"resurfacing versus replacement",
    ],
    "/guides/concrete-vs-asphalt-driveway-the-ultimate-2026-comparison/": [
        r"concrete vs asphalt",
        r"asphalt vs concrete",
    ],
}

BODY_START = re.compile(
    r'(<div class="guide-main">|<article[^>]*>|<main[^>]*>)', re.I
)
BODY_END = re.compile(
    r'(<section class="related-guides"|<nav class="guide-internal-links"|<aside|<footer)', re.I
)


def slug_from_path(path: str) -> str:
    return path.replace("guides/", "").replace("/index.html", "")


def extract_body(html: str) -> Optional[Tuple[str, int, int]]:
    start_m = BODY_START.search(html)
    if not start_m:
        return None
    start = start_m.start()
    end_m = BODY_END.search(html, start_m.end())
    end = end_m.start() if end_m else len(html)
    return html, start, end


def already_linked(chunk: str, target: str) -> bool:
    return target in chunk or target.rstrip("/") + '"' in chunk


def linkify_chunk(chunk: str, target: str, patterns: List[str]) -> Tuple[str, Optional[str]]:
    for pat in patterns:
        m = re.search(pat, chunk, re.I)
        if not m:
            continue
        anchor = m.group(0)
        before = chunk[: m.start()]
        after = chunk[m.end() :]
        # skip if inside tag or existing link
        if re.search(r"<a[^>]*$", before, re.I | re.S):
            continue
        if re.search(r"<[^>]*$", before):
            continue
        linked = f'<a href="{target}">{anchor}</a>'
        return before + linked + after, anchor
    return chunk, None


def process_file(path: str, dry_run: bool = False) -> List[str]:
    source = f"/guides/{slug_from_path(path)}/"
    html = open(path, encoding="utf-8").read()
    if source in TARGETS:
        return []

    extracted = extract_body(html)
    if not extracted:
        return []
    full, start, end = extracted
    body = full[start:end]
    if already_linked(body, source):
        pass  # still may link TO targets

    applied = []
    new_body = body
    for target, patterns in TARGETS.items():
        if target == source:
            continue
        if already_linked(new_body, target):
            continue
        updated, anchor = linkify_chunk(new_body, target, patterns)
        if anchor:
            new_body = updated
            applied.append(f"{source} -> {target} ({anchor})")

    if not applied:
        return []

    new_html = full[:start] + new_body + full[end:]
    if not dry_run:
        open(path, "w", encoding="utf-8").write(new_html)
    return applied


def main():
    import sys

    dry_run = "--dry-run" in sys.argv
    total_links = 0
    files_changed = 0
    log = []
    for path in sorted(glob.glob("guides/*/index.html")):
        results = process_file(path, dry_run=dry_run)
        if results:
            files_changed += 1
            total_links += len(results)
            log.extend(results)

    print(f"Files changed: {files_changed}")
    print(f"Links added: {total_links}")
    for line in log[:40]:
        print(" ", line)
    if len(log) > 40:
        print(f"  ... and {len(log) - 40} more")


if __name__ == "__main__":
    main()
