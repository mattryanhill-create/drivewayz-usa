#!/usr/bin/env python3
"""
Add 'For Contractors' nav link and footer link to all guide and location HTML files.
Run from the repo root: python3 add_for_contractors_nav.py
"""

import os
import glob

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# The nav insertion: add For Contractors after For Homeowners
NAV_OLD = '<li><a href="/for-homeowners">For Homeowners</a></li>'
NAV_NEW = '<li><a href="/for-homeowners">For Homeowners</a></li>\n                    <li><a href="/for-contractors">For Contractors</a></li>'

# Footer patterns for guides (simple footer)
GUIDE_FOOTER_OLD = '<a href="/#contact">Contact</a>'
GUIDE_FOOTER_NEW = '<a href="/#contact">Contact</a> &bull; <a href="/for-contractors">For Contractors</a>'

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changed = False

    # Add For Contractors nav link after For Homeowners (if not already present)
    if NAV_OLD in content and 'href="/for-contractors"' not in content:
        content = content.replace(NAV_OLD, NAV_NEW, 1)
        changed = True

    # Add For Contractors footer link in guide footer (if not already present)
    if GUIDE_FOOTER_OLD in content and 'for-contractors' not in content:
        content = content.replace(GUIDE_FOOTER_OLD, GUIDE_FOOTER_NEW, 1)
        changed = True

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated: {filepath}')
    
    return changed

def main():
    updated = 0
    skipped = 0

    # Process guides folder
    guide_pattern = os.path.join(PROJECT_ROOT, 'guides', '**', 'index.html')
    for filepath in glob.glob(guide_pattern, recursive=True):
        if process_file(filepath):
            updated += 1
        else:
            skipped += 1

    # Process locations folder
    location_pattern = os.path.join(PROJECT_ROOT, 'locations', '**', 'index.html')
    for filepath in glob.glob(location_pattern, recursive=True):
        if process_file(filepath):
            updated += 1
        else:
            skipped += 1

    print(f'\nDone! Updated: {updated}, Skipped (already done or no match): {skipped}')

if __name__ == '__main__':
    main()
