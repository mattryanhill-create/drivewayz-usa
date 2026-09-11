#!/usr/bin/env python3
"""Revalidate llms.txt against the llmstxt.org spec and local canonical pages.

Catches a missing H1, extra H1s, duplicate/parameterized URLs, redirect stubs,
and guide pages that were moved or deleted so a content migration cannot
silently leave stale agent links.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LLMS_PATH = REPO_ROOT / "llms.txt"
DOMAIN = "https://drivewayzusa.co"
CANONICAL_URL_RE = re.compile(
    r"^https://drivewayzusa\.co/guides/[a-z0-9-]+/$"
)
LINK_RE = re.compile(
    r"^- \[([^\]]+)\]\((https://[^)]+)\): (.+)$"
)
H1_RE = re.compile(r"^# (.+)$")
H2_RE = re.compile(r"^## (.+)$")
ANY_HEADING_RE = re.compile(r"^#{1,6} ")
DATE_RE = re.compile(r"Last reviewed:\s*(\d{4}-\d{2}-\d{2})")
CANONICAL_TAG_RE = re.compile(
    r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
    re.I,
)

REQUIRED_H1 = "Drivewayz USA"
REQUIRED_SECTIONS = (
    "Cost guides",
    "Materials",
    "Installation",
    "Repair",
    "Sealing",
    "Regional",
    "Permits",
)
MIN_LINKS = 30
MAX_LINKS = 40
MIN_PER_SECTION = 5
MAX_PER_SECTION = 10
MAX_REVIEW_AGE_DAYS = 180


def fail(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"{len(errors)} validation error(s) in llms.txt", file=sys.stderr)
    return 1


def is_redirect_stub(content: str) -> bool:
    return 'http-equiv="refresh"' in content or "http-equiv='refresh'" in content


def main() -> int:
    errors: list[str] = []

    if not LLMS_PATH.is_file():
        return fail([f"Missing {LLMS_PATH.relative_to(REPO_ROOT)}"])

    text = LLMS_PATH.read_text(encoding="utf-8-sig")
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    lines = text.splitlines()

    h1_lines = [i for i, line in enumerate(lines) if H1_RE.match(line)]
    if len(h1_lines) == 0:
        errors.append("File has no H1; llmstxt.org requires exactly one H1")
    elif len(h1_lines) > 1:
        errors.append(
            f"File has {len(h1_lines)} H1s; llmstxt.org requires exactly one"
        )
    else:
        h1_text = H1_RE.match(lines[h1_lines[0]]).group(1).strip()
        if h1_text != REQUIRED_H1:
            errors.append(f'H1 must be "{REQUIRED_H1}", got "{h1_text}"')
        if h1_lines[0] != 0:
            errors.append("H1 must be the first line of the file")

    if len(lines) < 3:
        errors.append("File is too short to include H1, blank line, and blockquote")
    elif lines[1].strip():
        errors.append("Blank line required after H1")
    elif not lines[2].startswith("> "):
        errors.append("A blockquote site description must follow the H1")
    elif not lines[2][2:].strip():
        errors.append("Blockquote must contain a one-sentence site description")

    date_match = DATE_RE.search(text)
    if not date_match:
        errors.append('Missing "Last reviewed: YYYY-MM-DD" date stamp')
    else:
        try:
            reviewed = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"Invalid Last reviewed date: {date_match.group(1)}")
        else:
            today = datetime.now(timezone.utc).date()
            if reviewed > today + timedelta(days=1):
                errors.append(f"Last reviewed date is in the future: {reviewed}")
            age = (today - reviewed).days
            if age > MAX_REVIEW_AGE_DAYS:
                errors.append(
                    f"Last reviewed {reviewed} is {age} days old; "
                    f"revalidate links and update the date "
                    f"(max {MAX_REVIEW_AGE_DAYS} days)"
                )

    sections: dict[str, list[tuple[str, str, str]]] = {}
    current: str | None = None
    seen_h2: list[str] = []
    in_preamble = True

    for i, line in enumerate(lines, start=1):
        if i <= 3:
            continue
        h2 = H2_RE.match(line)
        if h2:
            in_preamble = False
            name = h2.group(1).strip()
            if name in sections:
                errors.append(f"Duplicate H2 section: {name}")
            current = name
            seen_h2.append(name)
            sections.setdefault(name, [])
            continue
        if in_preamble and ANY_HEADING_RE.match(line):
            errors.append(
                f"Line {i}: preamble may not contain headings besides the H1"
            )
            continue
        if not line.strip():
            continue
        if current is None:
            continue
        if line.startswith("- "):
            link = LINK_RE.match(line)
            if not link:
                errors.append(
                    f"Line {i}: expected "
                    f"'- [Title](https://drivewayzusa.co/guides/{{slug}}/): summary'"
                )
                continue
            title, url, summary = link.groups()
            sections[current].append((title, url, summary))
        elif ANY_HEADING_RE.match(line):
            errors.append(
                f"Line {i}: only H2 headings are allowed in file-list sections"
            )
        else:
            errors.append(
                f"Line {i}: unexpected content in section {current!r}"
            )

    if seen_h2 != list(REQUIRED_SECTIONS):
        errors.append(
            "H2 sections must be exactly "
            f"{list(REQUIRED_SECTIONS)} in that order; got {seen_h2}"
        )

    all_urls: list[str] = []
    for name in REQUIRED_SECTIONS:
        links = sections.get(name, [])
        count = len(links)
        if count < MIN_PER_SECTION or count > MAX_PER_SECTION:
            errors.append(
                f"Section {name!r} has {count} links; "
                f"need {MIN_PER_SECTION}-{MAX_PER_SECTION}"
            )
        for title, url, summary in links:
            all_urls.append(url)
            if not title.strip():
                errors.append(f"Empty link title in section {name!r}")
            if not summary.strip():
                errors.append(f"Empty summary for {url}")
            if "?" in url or "#" in url:
                errors.append(f"Parameterized or fragment URL is not canonical: {url}")
            if url.rstrip("/") + "/" != url:
                errors.append(f"URL must use a trailing slash: {url}")
            if not CANONICAL_URL_RE.match(url):
                errors.append(
                    f"URL must be {DOMAIN}/guides/{{slug}}/ with no variants: {url}"
                )
                continue
            slug = url[len(f"{DOMAIN}/guides/") :].rstrip("/")
            page = REPO_ROOT / "guides" / slug / "index.html"
            if not page.is_file():
                errors.append(f"Missing local page for {url} ({page.relative_to(REPO_ROOT)})")
                continue
            html = page.read_text(encoding="utf-8", errors="replace")
            if is_redirect_stub(html):
                errors.append(
                    f"{url} is a redirect stub; list the canonical destination instead"
                )
                continue
            canonical = CANONICAL_TAG_RE.search(html)
            if not canonical:
                errors.append(f"No canonical tag on {page.relative_to(REPO_ROOT)}")
            elif canonical.group(1) != url:
                errors.append(
                    f"Canonical mismatch for {url}: page canonical is {canonical.group(1)}"
                )

    total = len(all_urls)
    if total < MIN_LINKS or total > MAX_LINKS:
        errors.append(f"Expected {MIN_LINKS}-{MAX_LINKS} curated links, found {total}")

    duplicates = sorted({u for u in all_urls if all_urls.count(u) > 1})
    for url in duplicates:
        errors.append(f"Duplicate URL listed more than once: {url}")

    if errors:
        return fail(errors)

    print(
        f"llms.txt OK: 1 H1, {len(REQUIRED_SECTIONS)} sections, "
        f"{total} canonical links, last reviewed {date_match.group(1)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
