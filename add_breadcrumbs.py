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


BREADCRUMB_CSS = """
        /* Breadcrumb */
        .breadcrumb-bar {
            background: #f0f0f0;
            padding: 0.5rem 2rem;
            font-size: 0.9rem;
            color: var(--text-light);
            margin-top: 140px;
        }
        .breadcrumb-bar .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .breadcrumb-bar a {
            color: var(--text-light);
            text-decoration: none;
        }
        .breadcrumb-bar a:hover {
            color: var(--primary-dark);
            text-decoration: underline;
        }
        .breadcrumb-bar .sep {
            margin: 0 0.4rem;
            color: #999;
        }
        .breadcrumb-bar + section.state-hero {
            margin-top: 0.5rem;
        }
"""


def build_breadcrumb_html(state_name: str) -> str:
    return f'''    <nav class="breadcrumb-bar" aria-label="Breadcrumb">
        <div class="container">
            <a href="/">Home</a><span class="sep">›</span><a href="/locations/">Locations</a><span class="sep">›</span>{state_name}
        </div>
    </nav>
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


def inject_breadcrumbs(html: str, slug: str) -> str:
    state_name = slug_to_display_name(slug)
    breadcrumb_html = build_breadcrumb_html(state_name)
    schema_html = build_breadcrumb_schema(state_name, slug)

    # Skip if already has breadcrumbs
    if "breadcrumb-bar" in html:
        return html

    # 1. Add breadcrumb HTML: inside main, as first child (below nav, above hero)
    main_open = '    <!-- Main Content -->\n    <main id="content">'
    if main_open in html and 'breadcrumb-bar' not in html:
        html = html.replace(
            main_open + '\n        <!-- Hero Section -->',
            main_open + '\n' + breadcrumb_html + '        <!-- Hero Section -->',
            1
        )

    # 2. Add breadcrumb CSS: before /* Hero Section */ or similar early in style
    if "/* Breadcrumb */" not in html:
        if "        /* Hero Section */" in html:
            html = html.replace(
                "        /* Hero Section */",
                BREADCRUMB_CSS.rstrip() + "\n\n        /* Hero Section */",
                1
            )
        elif "        /* Navigation */" in html:
            html = html.replace(
                "        /* Navigation */",
                BREADCRUMB_CSS.rstrip() + "\n\n        /* Navigation */",
                1
            )
        elif "</style>" in html:
            html = html.replace("</style>", BREADCRUMB_CSS + "\n    </style>", 1)

    # 3. Add JSON-LD in head: before </head>
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
