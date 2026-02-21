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

# Slug to abbreviation (for fixing corrupted badge markup)
STATE_ABBREVIATIONS = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT",
    "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
    "maryland": "MD", "massachusetts": "MA", "michigan": "MI",
    "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
    "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new-hampshire": "NH", "new-jersey": "NJ", "new-mexico": "NM",
    "new-york": "NY", "north-carolina": "NC", "north-dakota": "ND",
    "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode-island": "RI", "south-carolina": "SC", "south-dakota": "SD",
    "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west-virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY",
    "washington-dc": "DC", "puerto-rico": "PR", "us-virgin-islands": "VI",
    "guam": "GU", "american-samoa": "AS", "northern-mariana-islands": "MP",
}


def slug_to_display_name(slug: str) -> str:
    if slug in STATE_DISPLAY_NAMES:
        return STATE_DISPLAY_NAMES[slug]
    return slug.replace("-", " ").title()


# Breadcrumb: absolutely positioned in top-left of hero (position: absolute; top: 1rem; left: 2rem)
STATE_BREADCRUMB_CSS = """
        /* Breadcrumb - top-left of hero */
        .state-breadcrumb { position: absolute; top: 1rem; left: 2rem; z-index: 3; padding: 1rem 2rem; display: flex; gap: 0.5rem; font-size: 0.9rem; text-align: left; }
        .state-breadcrumb a { color: rgba(255,255,255,0.8); text-decoration: none; }
        .state-breadcrumb a:hover { color: white; }
"""


def build_breadcrumb_html(state_name: str) -> str:
    # Placed inside .state-hero but outside .state-hero-content (first child)
    return f'''            <div class="state-breadcrumb">
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

    # 2b. Fix corrupted state-badge markup (missing <span> open tag, may have stray control chars)
    abbr = STATE_ABBREVIATIONS.get(slug, slug[:2].upper())
    html = re.sub(
        r'(<div class="state-breadcrumb">[\s\S]*?</div>\n)(\s+)[^\n<]*</span>',
        r'\1\2<span class="state-badge">' + abbr + r'</span>',
        html,
        count=1
    )

    # 3. Move breadcrumb to top-left of hero: outside state-hero-content, first child of state-hero
    hero_breadcrumb_pattern = re.compile(
        r'(<section class="state-hero" [^>]*>)\s*'
        r'<div class="state-hero-content">\s*'
        r'<div class="state-breadcrumb">[\s\S]*?</div>\s*'
        r'<span class="state-badge">([^<]*)</span>',
        re.MULTILINE
    )

    def move_breadcrumb(m):
        return (m.group(1) + "\n" + breadcrumb_html.rstrip() +
                "\n            <div class=\"state-hero-content\">\n                " +
                "<span class=\"state-badge\">" + m.group(2) + "</span>")

    if hero_breadcrumb_pattern.search(html):
        html = hero_breadcrumb_pattern.sub(move_breadcrumb, html, count=1)

    # 4. Add or update state-breadcrumb CSS (absolute top-left positioning)
    old_css_pattern = re.compile(
        r'/\* Breadcrumb[^*]*\*/\s*'
        r'\.state-breadcrumb\s*\{[^}]*\}\s*'
        r'\.state-breadcrumb a\s*\{[^}]*\}\s*'
        r'\.state-breadcrumb a:hover\s*\{[^}]*\}\s*',
        re.MULTILINE
    )
    if old_css_pattern.search(html):
        html = old_css_pattern.sub(STATE_BREADCRUMB_CSS.rstrip() + "\n\n        ", html, count=1)
    elif ".state-breadcrumb" not in html or "position: absolute" not in html:
        if "        /* Hero Section */" in html:
            html = html.replace(
                "        /* Hero Section */",
                STATE_BREADCRUMB_CSS.rstrip() + "\n\n        /* Hero Section */",
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
