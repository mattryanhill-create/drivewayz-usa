#!/usr/bin/env python3
"""
Ensure every HTML page has exactly one self-referencing canonical tag.
Run from repo root: python scripts/ensure-canonicals.py

Convention: https://drivewayzusa.co{NORMALIZED_PATH}
- Root: https://drivewayzusa.co/
- All other paths: trailing slash (matches sitemap.xml)
"""
import re
from pathlib import Path
from typing import Optional

DOMAIN = "https://drivewayzusa.co"
REPO_ROOT = Path(__file__).resolve().parent.parent


def get_canonical_path(file_path: Path) -> str:
    """Derive canonical URL path from file path (relative to repo root)."""
    try:
        rel = file_path.relative_to(REPO_ROOT)
    except ValueError:
        return ""
    parts = rel.parts
    if not parts:
        return "/"
    if parts[-1] == "index.html":
        # Directory-style: guides/slug/index.html → /guides/slug/
        path = "/" + "/".join(parts[:-1]) + "/"
    elif parts[-1].endswith(".html"):
        # Standalone .html: locations/state.html → /locations/state/
        path = "/" + "/".join(parts[:-1]) + "/" + parts[-1][:-5] + "/"
    else:
        return ""
    return path if path != "//" else "/"


def get_canonical_url(file_path: Path) -> Optional[str]:
    """Return canonical URL for this file, or None if not a content page."""
    try:
        rel = str(file_path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return None
    if "state-page" in rel:
        return None
    path = get_canonical_path(file_path)
    if not path:
        return None
    return DOMAIN + path


def is_redirect_stub(content: str) -> bool:
    """True if this is a meta-refresh redirect stub."""
    return 'http-equiv="refresh"' in content or "http-equiv='refresh'" in content


def extract_existing_canonical(content: str) -> Optional[str]:
    """Extract href value from existing canonical tag, or None."""
    m = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', content, re.I)
    return m.group(1) if m else None


def fix_canonical(content: str, canonical_url: str, file_path: Path) -> str:
    """
    Ensure exactly one self-referencing canonical. If canonical exists but wrong, fix it.
    If missing, insert after meta description.
    """
    existing = extract_existing_canonical(content)
    tag = f'<link rel="canonical" href="{canonical_url}">'

    # Already correct (exact match)
    if existing and existing == canonical_url:
        return content

    # Remove duplicate or wrong canonicals (keep first occurrence to replace)
    if "rel=\"canonical\"" in content or "rel='canonical'" in content:
        content = re.sub(
            r'\s*<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']+["\']\s*>\s*\n?',
            "\n",
            content,
            flags=re.I,
        )

    # Insert after meta description
    pattern = r'(<meta\s+name=["\']description["\']\s+content=["\'][^"\']*["\']\s*>)'
    match = re.search(pattern, content, re.I)
    if match:
        insert = f'\n    {tag}'
        content = content[: match.end()] + insert + content[match.end() :]
    else:
        # Fallback: after </title>
        match = re.search(r"</title>", content, re.I)
        if match:
            insert = f"\n    {tag}"
            content = content[: match.end()] + insert + content[match.end() :]
        else:
            # Last resort: before </head>
            content = content.replace("</head>", f"    {tag}\n</head>")
    return content


def process_file(file_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Process one HTML file. Returns (modified, message)."""
    content = file_path.read_text(encoding="utf-8")
    canonical_url = get_canonical_url(file_path)
    if not canonical_url:
        return False, "skip"
    if is_redirect_stub(content):
        return False, "skip (redirect stub)"
    new_content = fix_canonical(content, canonical_url, file_path)
    if new_content != content:
        if not dry_run:
            file_path.write_text(new_content, encoding="utf-8")
        return True, "updated"
    return False, "ok"


def main():
    import sys
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    if dry_run:
        print("DRY RUN (no files will be modified)\n")
    modified = 0
    skipped = 0
    ok = 0
    for html_path in sorted(REPO_ROOT.rglob("*.html")):
        if "node_modules" in str(html_path):
            continue
        changed, msg = process_file(html_path, dry_run=dry_run)
        if changed:
            modified += 1
            print(f"  [UPDATED] {html_path.relative_to(REPO_ROOT)}")
        elif msg == "skip" or msg.startswith("skip"):
            skipped += 1
        else:
            ok += 1
    print(f"\nDone: {modified} updated, {ok} already correct, {skipped} skipped")
    if dry_run and modified:
        print("Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
