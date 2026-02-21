#!/usr/bin/env python3
"""
Add breadcrumb navigation and BreadcrumbList JSON-LD schema to all state pages.
"""

import json
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_DIR = os.path.join(PROJECT_ROOT, "locations")
BASE_URL = "https://drivewayzusa.co"

STATE_DISPLAY_NAMES = {
    "washington-dc": "Washington DC",
    "us-virgin-islands": "US Virgin Islands",
    "puerto-rico": "Puerto Rico",
    "northern-mariana-islands": "Northern Mariana Islands",
    "american-samoa": "American Samoa",
    "new-york": "New York",
    "new-jersey": "New Jersey",
    "new-mexico": "New Mexico",
    "new-hampshire": "New Hampshire",
    "north-carolina": "North Carolina",
    "north-dakota": "North Dakota",
    "south-carolina": "South Carolina",
    "south-dakota": "South Dakota",
    "west-virginia": "West Virginia",
    "rhode-island": "Rhode Island",
}


def slug_to_display_name(slug: str) -> str:
    if slug in STATE_DISPLAY_NAMES:
        return STATE_DISPLAY_NAMES[slug]
    return slug.replace("-", " ").title()


# Guide-style breadcrumb: white text inside hero, / separators (matches /guides/concrete-repair/)
STATE_BREADCRUMB_CSS = """
        /* Breadcrumb - matches guide pages */
        .state-breadcrumb { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; font-size: 0.9rem; }
        .state-breadcrumb a { color: rgba(255,255,255,0.8); text-decoration: none; }
        .state-breadcrumb a:hover { color: white; }
"""


def build_breadcrumb_html(state_name: str) -> str:
    return f'''                <div class="state-breadcrumb">
                    <a href="/">Home</a><span>/</span><a href="/locations/">Locations</a><span>/</span><span>{state_name}</span>
                </div>
'''


def build_breadcrumb_schema(state_name: str, slug: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Locations", "item": f"{BASE_URL}/locations/"},
            {"@type": "ListItem", "position": 3, "name": state_name}
        ]
    }
    return f'    <script type="application/ld+json">\n    {json.dumps(data, indent=4)}\n    </script>\n'


# Old breadcrumb-bar HTML pattern to remove (gray bar above hero)
OLD_BREADCRUMB_BAR_PATTERN = re.compile(
    r'\s*<nav class="breadcrumb-bar"[^>]*>.*?</nav>\s*',
    re.DOTALL
)

# Old breadcrumb-bar CSS block to remove
OLD_BREADCRUMB_CSS_PATTERN = re.compile(
    r'\s*/\* Breadcrumb \*/\s*'
    r'\.breadcrumb-bar\s*\{[^}]*\}[\s\S]*?'
    r'\.breadcrumb-bar \+ section\.state-hero\s*\{[^}]*\}\s*',
    re.MULTILINE
)


def inject_breadcrumbs(html: str, slug: str) -> str:
    state_name = slug_to_display_name(slug)
    breadcrumb_html = build_breadcrumb_html(state_name)
    schema_html = build_breadcrumb_schema(state_name, slug)

    # 1. Remove old gray breadcrumb-bar above hero
    html = OLD_BREADCRUMB_BAR_PATTERN.sub("\n        ", html)

    # 2. Remove old breadcrumb-bar CSS
    html = OLD_BREADCRUMB_CSS_PATTERN.sub("\n", html)

    # 3. Add guide-style breadcrumb inside state-hero-content (before state-badge)
    if "state-breadcrumb" not in html:
        html = re.sub(
            r'(<div class="state-hero-content">)\s*(<span class="state-badge">)',
            r'\1\n' + breadcrumb_html.rstrip() + '\n                \2',
            html,
            count=1
        )

    # 4. Add state-breadcrumb CSS (guide-style)
    if ".state-breadcrumb" not in html:
        if "        /* Hero Section */" in html:
            html = html.replace(
                "        /* Hero Section */",
                STATE_BREADCRUMB_CSS.rstrip() + "\n\n        /* Hero Section */",
                1
            )
        elif "        /* Navigation */" in html:
            html = html.replace(
                "        /* Navigation */",
                STATE_BREADCRUMB_CSS.rstrip() + "\n\n        /* Navigation */",
                1
            )

    # 5. Ensure JSON-LD in head
    if '"@type": "BreadcrumbList"' not in html:
        html = html.replace("</head>", schema_html + "</head>", 1)

    return html


def main():
    state_dirs = [d for d in os.listdir(LOCATIONS_DIR)
                  if os.path.isdir(os.path.join(LOCATIONS_DIR, d))
                  and os.path.isfile(os.path.join(LOCATIONS_DIR, d, "index.html"))]
    # Exclude state-page template
    state_dirs = [d for d in state_dirs if d != "state-page"]

    updated = 0
    for slug in sorted(state_dirs):
        path = os.path.join(LOCATIONS_DIR, slug, "index.html")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        new_html = inject_breadcrumbs(html, slug)
        if new_html != html:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_html)
            updated += 1
            print(f"Updated: {slug}")

    print(f"\nUpdated {updated} pages")


if __name__ == "__main__":
    main()
