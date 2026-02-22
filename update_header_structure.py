#!/usr/bin/env python3
"""
Update header/nav structure to site-header, main-nav, main-nav__list, nav-toggle.
Run from repo root.
"""
import os
import re
import glob

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Skip if already updated
    if 'site-header navbar' in content and 'main-nav__list' in content:
        return False
    
    # Skip if no navbar
    if '<nav class="navbar"' not in content:
        return False
    
    # 1. Change <nav class="navbar" to <header class="site-header navbar"
    content = content.replace('<nav class="navbar" id="navbar">', '<header class="site-header navbar" id="navbar">')
    content = content.replace('<nav class="navbar">', '<header class="site-header navbar" id="navbar">')
    
    # 2. Wrap ul.nav-links in nav.main-nav and add id to ul
    content = re.sub(
        r'<ul class="nav-links">',
        '<nav class="main-nav" aria-label="Main navigation">\n                <ul class="main-nav__list nav-links" id="main-nav-menu">',
        content,
        count=1
    )
    
    # 3. Add </nav> after </ul> (before cta or hamburger or closing div)
    content = re.sub(
        r'(</ul>)\s*(<button class="cta-button-small")',
        r'\1\n                </nav>\n                \2',
        content,
        count=1
    )
    if '</nav>' not in content or content.count('</nav>') == 1:  # Only navbar close
        content = re.sub(
            r'(</ul>)\s*(<button class="hamburger")',
            r'\1\n                </nav>\n                \2',
            content,
            count=1
        )
    if '</nav>' not in content or (content.count('</nav>') == 1 and '</header>' not in content):
        content = re.sub(
            r'(</ul>)\s*(\n\s*</div>\s*\n\s*</(?:nav|header)>)',
            r'\1\n                </nav>\n            \2',
            content,
            count=1
        )
    
    # 4. Update hamburger to nav-toggle with aria (if present)
    content = content.replace(
        '<button class="hamburger" id="hamburger" aria-label="Toggle menu">',
        '<button class="nav-toggle hamburger" id="hamburger" type="button" aria-label="Toggle navigation" aria-expanded="false" aria-controls="main-nav-menu">'
    )
    
    # 5. Change closing </nav> of navbar to </header>
    content = re.sub(
        r'</div>\s*\n(\s*)</nav>\s*\n(\s*)<div class="nav-overlay"',
        r'</div>\n\1</header>\n\2<div class="nav-overlay"',
        content,
        count=1
    )
    # For pages without nav-overlay
    if '<header class="site-header' in content and '</header>' not in content:
        content = re.sub(
            r'(</div>\s*\n\s*)</nav>(\s*\n\s*<!-- )',
            r'\1</header>\2',
            content,
            count=1
        )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    patterns = [
        'index.html',
        'cost-calculator/index.html',
        'cost-calculator.html',
        'for-homeowners/index.html',
        'for-contractors/index.html',
        'for-homeowners-quiz/index.html',
        'guides-hub/index.html',
        'thank-you-homeowner/index.html',
        'thank-you-contractor/index.html',
        'locations/index.html',
        'locations/**/index.html',
        'guides/**/index.html',
    ]
    
    updated = 0
    for p in patterns:
        for fp in glob.glob(os.path.join(root, p)):
            if os.path.isfile(fp):
                if update_file(fp):
                    updated += 1
                    print(f'Updated: {os.path.relpath(fp, root)}')
    
    print(f'\nDone. Updated {updated} files.')

if __name__ == '__main__':
    main()
