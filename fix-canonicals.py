#!/usr/bin/env python3
"""
Fix canonical tags across the static HTML site.
Base URL: https://drivewayzusa.co
Run from repo root.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

BASE_URL = "https://drivewayzusa.co"
REPO_ROOT = Path(__file__).resolve().parent

# Fix 1: Files that need canonical replaced (wrong domain + trailing slash)
FIX1_FILES = {
    "for-homeowners/index.html": f"{BASE_URL}/for-homeowners/",
    "for-contractors/index.html": f"{BASE_URL}/for-contractors/",
    "for-homeowners-quiz/index.html": f"{BASE_URL}/for-homeowners-quiz/",
}

# Canonical link tag pattern
CANONICAL_PATTERN = re.compile(
    r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']*)["\']\s*/?>',
    re.IGNORECASE,
)


def get_existing_canonical(content: str) -> Optional[str]:
    """Extract existing canonical href if present."""
    match = CANONICAL_PATTERN.search(content)
    return match.group(1) if match else None


def replace_canonical(content: str, new_href: str) -> str:
    """Replace existing canonical tag with new href. Preserves tag format."""
    match = CANONICAL_PATTERN.search(content)
    if not match:
        return content
    old_tag = match.group(0)
    # Preserve quote style if possible, otherwise use double quotes
    new_tag = re.sub(r'href=["\'][^"\']*["\']', f'href="{new_href}"', old_tag, count=1)
    return content.replace(old_tag, new_tag, 1)


def set_canonical(content: str, canonical_url: str) -> tuple[str, bool]:
    """
    Set canonical to exact URL. Replaces if exists, adds if missing.
    Returns (new_content, was_modified).
    """
    existing = get_existing_canonical(content)
    correct_url = canonical_url if canonical_url.endswith("/") else canonical_url + "/"
    if existing and existing.rstrip("/") == correct_url.rstrip("/") and existing.endswith("/"):
        return content, False  # Already correct
    if existing:
        new_content = replace_canonical(content, correct_url)
    else:
        new_content = add_canonical(content, correct_url)
    return new_content, True


def add_canonical(content: str, canonical_url: str) -> str:
    """
    Add canonical tag to content. Inserts after viewport meta, before first link.
    """
    canonical_tag = f'  <link rel="canonical" href="{canonical_url}">'
    # Try to insert after viewport meta (common pattern in this site)
    viewport_pattern = re.compile(
        r'(<meta\s+name=["\']viewport["\']\s+content="[^"]*"\s*/?>\s*)',
        re.IGNORECASE,
    )
    match = viewport_pattern.search(content)
    if match:
        insert_after = match.end()
        return content[:insert_after] + "\n" + canonical_tag + "\n" + content[insert_after:]
    # Fallback: insert after </title>
    title_pattern = re.compile(r"(</title>\s*)", re.IGNORECASE)
    match = title_pattern.search(content)
    if match:
        insert_after = match.end()
        return content[:insert_after] + "\n" + canonical_tag + "\n" + content[insert_after:]
    # Last resort: insert at start of <head>
    head_pattern = re.compile(r"(<head[^>]*>\s*)", re.IGNORECASE)
    match = head_pattern.search(content)
    if match:
        insert_after = match.end()
        return content[:insert_after] + "\n" + canonical_tag + "\n" + content[insert_after:]
    raise ValueError("Could not find insertion point for canonical tag")


def process_file(
    filepath: Path,
    dry_run: bool,
    modified: list[str],
    skipped: list[str],
    errors: list[str],
) -> None:
    """Process a single HTML file."""
    rel_path = str(filepath.relative_to(REPO_ROOT))
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"{rel_path}: {e}")
        return

    original_content = content
    changed = False

    # Fix 1: Replace canonical in 3 specific files (force drivewayzusa.co + trailing slash)
    if rel_path in FIX1_FILES:
        correct_url = FIX1_FILES[rel_path]
        content, changed = set_canonical(content, correct_url)

    # Fix 2: Add/replace canonical in guides/*/index.html (always use drivewayzusa.co)
    elif rel_path.startswith("guides/") and rel_path.endswith("/index.html"):
        folder_name = rel_path[len("guides/"): -len("/index.html")]
        expected_canonical = f"{BASE_URL}/guides/{folder_name}/"
        content, changed = set_canonical(content, expected_canonical)

    # Fix 3: Add/replace canonical in guides-hub/index.html (always use drivewayzusa.co)
    elif rel_path == "guides-hub/index.html":
        expected_canonical = f"{BASE_URL}/guides-hub/"
        content, changed = set_canonical(content, expected_canonical)

    if changed:
        if dry_run:
            modified.append(rel_path)
        else:
            filepath.write_text(content, encoding="utf-8")
            modified.append(rel_path)
    elif rel_path in FIX1_FILES or (rel_path.startswith("guides/") and rel_path.endswith("/index.html")) or rel_path == "guides-hub/index.html":
        # We considered this file but didn't need to change it
        skipped.append(rel_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix canonical tags across static HTML site")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files",
    )
    args = parser.parse_args()
    dry_run = args.dry_run

    modified: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []

    # Fix 1: Process the 3 specific files
    for rel_path in FIX1_FILES:
        filepath = REPO_ROOT / rel_path
        if filepath.exists():
            process_file(filepath, dry_run, modified, skipped, errors)
        else:
            errors.append(f"{rel_path}: file not found")

    # Fix 2: Process all guides/*/index.html
    guides_dir = REPO_ROOT / "guides"
    if guides_dir.exists():
        for subdir in sorted(guides_dir.iterdir()):
            if subdir.is_dir():
                index_file = subdir / "index.html"
                if index_file.exists():
                    process_file(index_file, dry_run, modified, skipped, errors)

    # Fix 3: Process guides-hub/index.html
    guides_hub = REPO_ROOT / "guides-hub" / "index.html"
    if guides_hub.exists():
        process_file(guides_hub, dry_run, modified, skipped, errors)
    else:
        errors.append("guides-hub/index.html: file not found")

    # Print summary
    print("=" * 60)
    print("Canonical fix summary")
    print("=" * 60)
    if dry_run:
        print("(DRY RUN - no files were modified)")
        print()
    print(f"Files modified: {len(modified)}")
    for f in modified[:30]:
        print(f"  - {f}")
    if len(modified) > 30:
        print(f"  ... and {len(modified) - 30} more")
    print(f"\nFiles skipped (already correct): {len(skipped)}")
    for f in skipped[:20]:  # Limit output
        print(f"  - {f}")
    if len(skipped) > 20:
        print(f"  ... and {len(skipped) - 20} more")
    if errors:
        print(f"\nErrors: {len(errors)}")
        for e in errors:
            print(f"  - {e}")
    print("=" * 60)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
