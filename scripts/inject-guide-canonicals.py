#!/usr/bin/env python3
"""
Inject canonical tags into all guide pages at guides/{slug}/index.html.
Inserts: <link rel="canonical" href="https://drivewayzusa.co/guides/{slug}/">
after the <meta name="description"> tag if not already present.
"""
import re
from pathlib import Path

GUIDES_DIR = Path(__file__).resolve().parent.parent / "guides"
BASE_URL = "https://drivewayzusa.co"

def inject_canonical(filepath: Path, slug: str) -> bool:
    """Inject canonical tag after meta description. Returns True if file was modified."""
    content = filepath.read_text(encoding="utf-8")
    canonical_url = f"{BASE_URL}/guides/{slug}/"
    canonical_tag = f'<link rel="canonical" href="{canonical_url}">'

    if "rel=\"canonical\"" in content or "rel='canonical'" in content:
        return False  # Already has canonical

    # Match meta description line (handles " or ' for attributes)
    pattern = r'(<\s*meta\s+name\s*=\s*["\']description["\']\s+content\s*=\s*["\'][^"\']*["\']\s*>\s*\n)'
    match = re.search(pattern, content, re.IGNORECASE)
    if not match:
        return False
    indent = "  "  # consistent 2-space indent
    insert = f'{indent}<link rel="canonical" href="{canonical_url}">\n'
    new_content = content[:match.end()] + insert + content[match.end():]
    filepath.write_text(new_content, encoding="utf-8")
    return True

def main():
    modified = 0
    for index_path in sorted(GUIDES_DIR.rglob("index.html")):
        if "index.html" not in str(index_path.relative_to(GUIDES_DIR)):
            continue
        rel = index_path.relative_to(GUIDES_DIR)
        if rel.name != "index.html":
            continue
        slug = rel.parent.as_posix()
        if inject_canonical(index_path, slug):
            modified += 1
    print(f"Modified {modified} guide files")

if __name__ == "__main__":
    main()
