#!/usr/bin/env python3
"""
Rebuild step: inject includes/clarity.html once before </head> on deployable pages.

Single source of truth is includes/clarity.html — do not hand-edit page HTML.
Skips redirect stubs, Draft_ files, and non-deployed folders.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTIAL = ROOT / "includes" / "clarity.html"

EXCLUDE_DIRS = {
    ".git",
    ".worktrees",
    ".drafts",
    ".cursor",
    ".github",
    "node_modules",
    ".hero-pipeline",
    "includes",
    "scripts",
}
EXCLUDE_PREFIXES = (".day-",)

# Existing Clarity blocks (placeholder ID, real ID, or commented variants)
CLARITY_BLOCK_RE = re.compile(
    r"(?:<!--\s*Microsoft Clarity\s*-->\s*)?"
    r"<script\b[^>]*>\s*"
    r"\(function\s*\(\s*c\s*,\s*l\s*,\s*a\s*,\s*r\s*,\s*i\s*,\s*t\s*,\s*y\s*\)\s*\{.*?"
    r"clarity\.ms/tag/.*?"
    r"\}\)\s*\(\s*window\s*,\s*document\s*,\s*[\"']clarity[\"']\s*,\s*[\"']script[\"']\s*,\s*[\"'][^\"']+[\"']\s*\)\s*;?\s*"
    r"</script>\s*",
    re.IGNORECASE | re.DOTALL,
)

HEAD_CLOSE_RE = re.compile(r"</head\s*>", re.IGNORECASE)


def skip_dir(name: str) -> bool:
    if name in EXCLUDE_DIRS:
        return True
    return any(name.startswith(p) for p in EXCLUDE_PREFIXES)


def is_redirect_stub(text: str) -> bool:
    """Flat redirect HTML (meta refresh / empty body) — leave untouched."""
    low = text.lower()
    if "http-equiv=\"refresh\"" in low or "http-equiv='refresh'" in low:
        # Tiny redirect files
        if len(text) < 500:
            return True
    return False


def inject(text: str, snippet: str) -> tuple[str, str]:
    """
    Returns (new_text, status) where status is inserted|updated|unchanged|skipped|no-head.
    """
    if is_redirect_stub(text):
        return text, "skipped-redirect"

    if not HEAD_CLOSE_RE.search(text):
        return text, "no-head"

    block = snippet.rstrip() + "\n"
    # Fast path: exact partial already present once, immediately before </head>
    if (
        text.count("zgam9w4xp5") == 1
        and text.count("clarity.ms/tag/") == 1
        and block + "</head>" in text.replace("</Head>", "</head>").replace("</HEAD>", "</head>")
    ):
        # Normalize only the common lowercase close tag case
        if block + "</head>" in text or re.search(
            re.escape(snippet.rstrip()) + r"\n</head\s*>", text, re.I
        ):
            return text, "unchanged"

    stripped, n = CLARITY_BLOCK_RE.subn("", text)
    # Remove any remaining old clarity blocks after partial strip edge cases
    stripped = CLARITY_BLOCK_RE.sub("", stripped)

    new_text, count = HEAD_CLOSE_RE.subn(block + "</head>", stripped, count=1)
    if count != 1:
        return text, "no-head"

    # Safety: exactly one project id in page
    if new_text.count("zgam9w4xp5") != 1:
        return text, "bad-count"

    if new_text == text:
        return text, "unchanged"

    status = "updated" if n else "inserted"
    return new_text, status


def iter_html() -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not skip_dir(d)]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            if name.startswith("Draft_") or name.startswith("Draft "):
                continue
            files.append(Path(dirpath) / name)
    return files


def main() -> int:
    if not PARTIAL.is_file():
        print(f"Missing partial: {PARTIAL}", file=sys.stderr)
        return 1

    snippet = PARTIAL.read_text(encoding="utf-8")
    if "zgam9w4xp5" not in snippet:
        print("Partial missing Clarity project ID", file=sys.stderr)
        return 1

    stats = {
        "inserted": 0,
        "updated": 0,
        "unchanged": 0,
        "skipped-redirect": 0,
        "no-head": 0,
        "bad-count": 0,
    }
    bad: list[str] = []

    for path in iter_html():
        text = path.read_text(encoding="utf-8", errors="replace")
        new_text, status = inject(text, snippet)
        stats[status] = stats.get(status, 0) + 1
        if status in ("inserted", "updated") and new_text != text:
            path.write_text(new_text, encoding="utf-8")
        if status == "bad-count":
            bad.append(str(path.relative_to(ROOT)))

    print("Clarity head inject rebuild")
    print(f"  partial: {PARTIAL.relative_to(ROOT)}")
    for key in ("inserted", "updated", "unchanged", "skipped-redirect", "no-head", "bad-count"):
        print(f"  {key}: {stats.get(key, 0)}")
    if bad:
        print("  bad-count files:")
        for b in bad:
            print(f"    {b}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
