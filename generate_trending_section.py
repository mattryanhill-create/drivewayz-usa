#!/usr/bin/env python3
"""
Inject "Trending Driveway Topics" section into every state page.
Reads state-articles.json and inserts the section after Related Resources, before CTA.
"""

import json
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_DIR = os.path.join(PROJECT_ROOT, "locations")
STATE_ARTICLES_PATH = os.path.join(PROJECT_ROOT, "state-articles.json")

# Slug to display name for special cases
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
    """Convert slug to display name (e.g. new-york -> New York)."""
    if slug in STATE_DISPLAY_NAMES:
        return STATE_DISPLAY_NAMES[slug]
    return slug.replace("-", " ").title()


TRENDING_CSS = """
        /* Trending Driveway Topics Section */
        .trending-section {
            padding: 4rem 2rem;
            background: var(--bg-light);
            border-top: 1px solid #eee;
        }
        .trending-section h3 {
            font-size: 1.5rem;
            color: var(--text-dark);
            margin-bottom: 1.5rem;
        }
        .trending-cards {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .trending-card {
            display: flex;
            flex-direction: row;
            align-items: center;
            gap: 1rem;
            background: var(--white);
            border: 1px solid #eee;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: box-shadow 0.3s ease;
        }
        .trending-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .trending-card-thumb {
            flex-shrink: 0;
            width: 80px;
            height: 80px;
            border-radius: 8px;
            object-fit: cover;
            background: #f0f0f0;
        }
        .trending-card-body {
            flex: 1;
            min-width: 0;
        }
        .trending-card-badge {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            margin-bottom: 0.35rem;
            background: var(--primary);
            color: var(--white);
        }
        .trending-card-title {
            font-size: 1rem;
            font-weight: 600;
            margin: 0 0 0.25rem 0;
        }
        .trending-card-title a {
            color: var(--text-dark);
            text-decoration: none;
        }
        .trending-card-title a:hover {
            color: var(--primary-dark);
            text-decoration: underline;
        }
        .trending-card-meta {
            font-size: 0.85rem;
            color: var(--text-light);
        }
        .trending-empty {
            background: var(--white);
            border: 1px solid #eee;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            color: var(--text-light);
        }
        @media (min-width: 768px) {
            .trending-cards {
                flex-direction: column;
            }
        }
"""


def build_trending_html(slug: str, articles: list, state_name: str) -> str:
    """Build the trending section HTML (no CTA comment - caller adds it)."""
    lines = [
        '        <!-- Trending Driveway Topics -->',
        '        <section class="trending-section">',
        '            <div class="container">',
        f'                <h3>⭐ Trending Driveway Topics in {state_name}</h3>',
    ]
    if articles:
        lines.append('                <div class="trending-cards">')
        for art in articles[:3]:  # Max 3
            badge = art.get("category", "GUIDE")
            lines.extend([
                '                    <div class="trending-card">',
                f'                        <img class="trending-card-thumb" src="{art.get("thumbnail", "")}" alt="">',
                '                        <div class="trending-card-body">',
                f'                            <span class="trending-card-badge">{badge}</span>',
                f'                            <h4 class="trending-card-title"><a href="{art.get("url", "#")}">{art.get("title", "")}</a></h4>',
                f'                            <p class="trending-card-meta">{art.get("read_time", "")}</p>',
                '                        </div>',
                '                    </div>',
            ])
        lines.append('                </div>')
    else:
        lines.append(f'                <div class="trending-empty">New {state_name} driveway content coming soon. Check back for local tips and guides.</div>')
    lines.extend([
        '            </div>',
        '        </section>',
    ])
    return '\n'.join(lines)


def inject_trending(html: str, slug: str, articles: list) -> str:
    """Inject trending section and CSS into page HTML."""
    state_name = slug_to_display_name(slug)
    trending_block = build_trending_html(slug, articles, state_name)

    # Insert after resources-section </section>, before <!-- CTA Section -->
    insertion_marker = '        </section>\n\n        <!-- CTA Section -->'
    if insertion_marker not in html:
        # Try alternate whitespace
        pat = re.compile(r'        </section>\s*\n+\s*<!-- CTA Section -->')
        match = pat.search(html)
        if match:
            replacement = '        </section>\n\n        ' + trending_block + '\n\n        <!-- CTA Section -->'
            html = pat.sub(replacement, html, count=1)
        else:
            return html
    else:
        replacement = '        </section>\n\n        ' + trending_block + '\n\n        <!-- CTA Section -->'
        html = html.replace(insertion_marker, replacement, 1)

    # Add CSS if not present
    if '/* Trending Driveway Topics Section */' not in html:
        if '        /* CTA Section */' in html:
            html = html.replace(
                '        /* CTA Section */',
                TRENDING_CSS.rstrip() + '\n\n        /* CTA Section */',
                1
            )
        elif '</style>' in html:
            html = html.replace('</style>', TRENDING_CSS + '\n    </style>', 1)

    return html


def main():
    with open(STATE_ARTICLES_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    for slug, articles in data.items():
        path = os.path.join(LOCATIONS_DIR, slug, "index.html")
        if not os.path.isfile(path):
            print(f"Skip (no file): {slug}")
            continue

        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()

        # Skip if already has trending section
        if 'trending-section' in html:
            print(f"Skip (already has trending): {slug}")
            continue

        new_html = inject_trending(html, slug, articles)
        if new_html != html:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            updated += 1
            print(f"Updated: {slug}")

    print(f"\nUpdated {updated} pages")


if __name__ == "__main__":
    main()
