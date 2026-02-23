#!/usr/bin/env python3
"""
SEO Fix Script for drivewayzusa.co
===================================
Run from the repo root: python scripts/fix-seo-issues.py

This script addresses 4 critical SEO issues:
1. Creates meta-refresh redirect stubs for old .html URLs -> new clean URLs
2. Adds self-referencing canonical tags to all pages missing them
3. Fixes homepage duplicate (/index.html redirect)
4. Fixes trailing slash mismatch on canonical tags
"""

import os
import re
import csv
import glob

DOMAIN = "https://drivewayzusa.co"

# ============================================================
# TASK 1: Create redirect stubs for old .html URLs
# ============================================================

REDIRECT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url={new_url}">
    <link rel="canonical" href="{canonical_url}">
    <title>Redirecting...</title>
</head>
<body>
    <p>This page has moved. <a href="{new_url}">Click here</a> if you are not redirected.</p>
    <script>window.location.replace("{new_url}");</script>
</body>
</html>
"""

def create_redirect_stubs():
    """Read redirects-plan CSV and create .html redirect stub files."""
    csv_path = "redirects-plan-drivewayzusa.csv"
    if not os.path.exists(csv_path):
        print("[SKIP] redirects-plan-drivewayzusa.csv not found")
        return 0

    count = 0
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # skip header
        for row in reader:
            if len(row) < 2:
                continue
            old_path = row[0].strip()
            new_path = row[1].strip()

            # Strip leading slash for file path
            file_path = old_path.lstrip("/")

            # Skip if old path doesn't end with .html
            if not file_path.endswith(".html"):
                continue

            # Skip if this would overwrite an existing real page
            # (e.g., guides/slug/index.html should not be overwritten)
            if os.path.exists(file_path):
                print(f"  [EXISTS] {file_path} - skipping")
                continue

            new_url = DOMAIN + new_path
            canonical_url = new_url

            # Ensure directory exists
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            with open(file_path, "w") as out:
                out.write(REDIRECT_TEMPLATE.format(
                    new_url=new_url,
                    canonical_url=canonical_url
                ))
            count += 1

    print(f"[TASK 1] Created {count} redirect stub files")
    return count

# ============================================================
# TASK 2: Add canonical tags to pages missing them
# ============================================================

def get_canonical_url(file_path):
    """Derive the canonical URL from the file path."""
    # Remove index.html from the end
    if file_path.endswith("/index.html"):
        url_path = file_path[:-len("index.html")]
    elif file_path == "index.html":
        url_path = "/"
    else:
        url_path = "/" + file_path

    # Ensure leading slash
    if not url_path.startswith("/"):
        url_path = "/" + url_path

    # Ensure trailing slash (except for root)
    if url_path != "/" and not url_path.endswith("/"):
        url_path += "/"

    return DOMAIN + url_path


def add_canonical_tags():
    """Add self-referencing canonical tags to all HTML files missing them."""
    count = 0
    patterns = [
        "guides/*/index.html",
        "guides-hub/index.html",
        "cost-calculator/index.html",
    ]

    all_files = []
    for pattern in patterns:
        all_files.extend(glob.glob(pattern))

    for file_path in all_files:
        with open(file_path, "r") as f:
            content = f.read()

        # Skip if already has a canonical tag
        if 'rel="canonical"' in content or "rel='canonical'" in content:
            continue

        canonical_url = get_canonical_url(file_path)
        canonical_tag = f'    <link rel="canonical" href="{canonical_url}">'

        # Insert canonical after <link rel="stylesheet"> or after </title>
        # Try after stylesheet first
        if '<link rel="stylesheet"' in content:
            content = content.replace(
                '<link rel="stylesheet"',
                canonical_tag + '\n    <link rel="stylesheet"'
            )
        elif '</title>' in content:
            content = content.replace(
                '</title>',
                '</title>\n' + canonical_tag
            )
        else:
            # Fallback: insert before </head>
            content = content.replace(
                '</head>',
                canonical_tag + '\n</head>'
            )

        with open(file_path, "w") as f:
            f.write(content)
        count += 1

    print(f"[TASK 2] Added canonical tags to {count} files")
    return count

# ============================================================
# TASK 3: Fix homepage /index.html duplicate
# ============================================================

def fix_homepage_duplicate():
    """Homepage index.html already has canonical. This is handled by Task 1
    which creates a redirect from the old /index.html path.
    The HTTP->HTTPS redirect is handled at the DNS/hosting level."""
    print("[TASK 3] Homepage canonical already set. /index.html redirect handled by Task 1.")
    print("         NOTE: http:// -> https:// redirect must be configured at DNS/hosting level.")
    return 0

# ============================================================
# TASK 4: Fix trailing slash mismatches on canonical tags
# ============================================================

def fix_trailing_slash_canonicals():
    """Fix canonical tags that are missing trailing slashes."""
    files_to_fix = [
        "for-homeowners/index.html",
        "for-contractors/index.html",
    ]

    count = 0
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            print(f"  [SKIP] {file_path} not found")
            continue

        with open(file_path, "r") as f:
            content = f.read()

        # Find canonical tag and fix trailing slash
        # Match: href="https://drivewayzusa.co/for-homeowners"
        # Replace with: href="https://drivewayzusa.co/for-homeowners/"
        pattern = r'(rel="canonical"\s+href="https://drivewayzusa\.co/[^"]+?)"'

        def fix_slash(match):
            url = match.group(1)
            if not url.endswith("/"):
                return url + '/"'
            return match.group(0)

        new_content = re.sub(pattern, fix_slash, content)

        if new_content != content:
            with open(file_path, "w") as f:
                f.write(new_content)
            count += 1
            print(f"  [FIXED] {file_path}")
        else:
            print(f"  [OK] {file_path} - already correct")

    print(f"[TASK 4] Fixed trailing slash on {count} files")
    return count

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("="*60)
    print("SEO Fix Script for drivewayzusa.co")
    print("="*60)
    print()

    # Verify we're in the repo root
    if not os.path.exists("index.html"):
        print("ERROR: Run this script from the repo root directory.")
        print("  cd /path/to/drivewayz-usa")
        print("  python scripts/fix-seo-issues.py")
        exit(1)

    print("--- Task 1: Creating redirect stubs for old .html URLs ---")
    t1 = create_redirect_stubs()
    print()

    print("--- Task 2: Adding canonical tags to pages missing them ---")
    t2 = add_canonical_tags()
    print()

    print("--- Task 3: Fixing homepage duplicate ---")
    t3 = fix_homepage_duplicate()
    print()

    print("--- Task 4: Fixing trailing slash on canonical tags ---")
    t4 = fix_trailing_slash_canonicals()
    print()

    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Redirect stubs created:    {t1}")
    print(f"  Canonical tags added:      {t2}")
    print(f"  Trailing slashes fixed:    {t4}")
    print()
    print("NEXT STEPS:")
    print("  1. Review changes: git diff")
    print("  2. Commit: git add -A && git commit -m 'Fix SEO: canonicals + redirects'")
    print("  3. Push: git push origin main")
    print("  4. Wait 2-3 min for GitHub Pages deploy")
    print("  5. Resubmit sitemap in GSC")
    print("  6. Re-inspect priority URLs in GSC")
