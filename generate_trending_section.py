#!/usr/bin/env python3
"""
Inject "Trending Driveway Topics" as a sticky sidebar widget on every state page.
Reads state-articles.json. Wraps intro through Why Choose in a two-column layout
with the sidebar on the right. Removes any existing full-width trending section.
"""

import json
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_DIR = os.path.join(PROJECT_ROOT, "locations")
STATE_ARTICLES_PATH = os.path.join(PROJECT_ROOT, "state-articles.json")

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


SIDEBAR_CSS = """
        /* Content with Sidebar Layout */
        .content-with-sidebar {
            display: grid;
            grid-template-columns: 1fr 320px;
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1.5rem;
        }
        .main-content-col {
            min-width: 0;
        }
        .trending-sidebar {
            position: sticky;
            top: 100px;
            align-self: start;
        }
        .trending-widget {
            background: var(--white);
            border-radius: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border: 1px solid #eee;
            padding: 1.25rem;
        }
        .trending-widget h3 {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-dark);
            margin: 0 0 1rem 0;
        }
        .trending-widget-item {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            padding: 1rem 0;
            border-bottom: 1px solid #eee;
        }
        .trending-widget-item:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }
        .trending-widget-item:first-child {
            padding-top: 0;
        }
        .trending-widget-thumb {
            flex-shrink: 0;
            width: 80px;
            height: 80px;
            border-radius: 8px;
            object-fit: cover;
            background: #f0f0f0;
        }
        .trending-widget-body {
            flex: 1;
            min-width: 0;
        }
        .trending-widget-badge {
            display: inline-block;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            padding: 0.2rem 0.5rem;
            border-radius: 999px;
            margin-bottom: 0.3rem;
            background: var(--primary);
            color: var(--white);
        }
        .trending-widget-title {
            font-size: 0.95rem;
            font-weight: 600;
            margin: 0 0 0.2rem 0;
            line-height: 1.3;
        }
        .trending-widget-title a {
            color: var(--text-dark);
            text-decoration: none;
        }
        .trending-widget-title a:hover {
            color: var(--primary-dark);
            text-decoration: underline;
        }
        .trending-widget-meta {
            font-size: 0.8rem;
            color: var(--text-light);
        }
        .trending-widget-empty {
            font-size: 0.95rem;
            color: var(--text-light);
            line-height: 1.5;
        }
        @media (max-width: 768px) {
            .content-with-sidebar {
                grid-template-columns: 1fr;
                padding: 0 1rem;
            }
            .trending-sidebar {
                position: static;
                order: 2;
            }
        }
"""


def build_widget_html(slug: str, articles: list, state_name: str) -> str:
    """Build the trending widget card HTML."""
    lines = [
        '        <aside class="trending-sidebar">',
        '            <div class="trending-widget">',
        f'                <h3>⭐ Trending Driveway Topics in {state_name}</h3>',
    ]
    if articles:
        for i, art in enumerate(articles[:3]):
            badge = art.get("category", "GUIDE")
            lines.extend([
                f'                <div class="trending-widget-item">',
                f'                    <img class="trending-widget-thumb" src="{art.get("thumbnail", "")}" alt="">',
                '                    <div class="trending-widget-body">',
                f'                        <span class="trending-widget-badge">{badge}</span>',
                f'                        <h4 class="trending-widget-title"><a href="{art.get("url", "#")}">{art.get("title", "")}</a></h4>',
                f'                        <p class="trending-widget-meta">{art.get("read_time", "")}</p>',
                '                    </div>',
                '                </div>',
            ])
    else:
        lines.append(f'                <p class="trending-widget-empty">New {state_name} content coming soon. Check back for local tips and guides.</p>')
    lines.extend([
        '            </div>',
        '        </aside>',
    ])
    return '\n'.join(lines)


def inject_sidebar_layout(html: str, slug: str, articles: list) -> str:
    """Convert to sidebar layout: remove old trending, add two-column wrapper + widget."""
    state_name = slug_to_display_name(slug)
    widget_html = build_widget_html(slug, articles, state_name)

    # 1. Remove old full-width trending section (between resources and CTA)
    old_trending_pat = re.compile(
        r'\s*<!-- Trending Driveway Topics -->\s*<section class="trending-section">.*?</section>\s*\n\s*(?=<!-- CTA Section -->)',
        re.DOTALL
    )
    html = old_trending_pat.sub('\n\n        ', html)

    # 2. Remove old trending CSS (full-width section styles)
    old_css_pat = re.compile(
        r'\n        /\* Trending Driveway Topics Section \*/.*?        @media \(min-width: 768px\) \{\s*\.trending-cards \{\s*flex-direction: column;\s*\}\s*\}\s*',
        re.DOTALL
    )
    html = old_css_pat.sub('', html)
    # Also remove the older CSS block if it exists in different form
    if '.trending-section ' in html and 'content-with-sidebar' not in html:
        old_css_alt = re.compile(
            r'\n        /\* Trending Driveway Topics Section \*/.*?(?=\n        /\* [A-Z]|\n    </style>)',
            re.DOTALL
        )
        html = old_css_alt.sub('', html)

    # 3. Skip if already has sidebar layout
    if 'content-with-sidebar' in html:
        return html

    # 4. Wrap intro through why-section in two-column layout
    # Insert opening wrapper before <!-- Intro Section -->
    intro_marker = '        <!-- Intro Section -->'
    if intro_marker not in html:
        return html
    html = html.replace(
        intro_marker,
        '        <div class="content-with-sidebar">\n            <div class="main-content-col">\n        ' + intro_marker,
        1
    )

    # 5. Insert sidebar + close wrapper after why-section's </section>
    # Pattern: </section> (why) followed by newlines and <section class="local-facts-section">
    local_facts_marker = '<section class="local-facts-section">'
    if local_facts_marker in html:
        pat = re.compile(
            r'(        </section>)\s*\n\s*(' + re.escape(local_facts_marker) + r')',
            re.DOTALL
        )
        sidebar_insert = (
            '\n            </div>\n            ' +
            widget_html.replace('\n', '\n            ') +
            '\n        </div>\n\n        '
        )
        replacement = r'\1' + sidebar_insert + r'\2'
        html = pat.sub(replacement, html, count=1)

    # 6. Add sidebar CSS
    if 'content-with-sidebar' in html and '/* Content with Sidebar Layout */' not in html:
        if '        /* CTA Section */' in html:
            html = html.replace(
                '        /* CTA Section */',
                SIDEBAR_CSS.rstrip() + '\n\n        /* CTA Section */',
                1
            )
        elif '</style>' in html:
            html = html.replace('</style>', SIDEBAR_CSS + '\n    </style>', 1)

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

        new_html = inject_sidebar_layout(html, slug, articles)
        if new_html != html:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            updated += 1
            print(f"Updated: {slug}")

    print(f"\nUpdated {updated} pages")


if __name__ == "__main__":
    main()
