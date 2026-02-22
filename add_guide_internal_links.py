#!/usr/bin/env python3
"""
Add internal linking blocks to all guide pages:
- "Back to [State] driveways" link (for state-specific guides)
- "View all driveway guides" link (always)

Run after generating guides. Idempotent: updates existing blocks when state is detected.
"""

import html
import re
from pathlib import Path

from state_guides import get_state_for_guide, slug_to_display_name

PROJECT_ROOT = Path(__file__).resolve().parent
GUIDES_DIR = PROJECT_ROOT / "guides"

# Pattern to match the guide-internal-links nav block
NAV_PATTERN = re.compile(
    r'<nav\s+class="guide-internal-links"[^>]*>.*?</nav>',
    re.DOTALL,
)


def build_internal_links_html(guide_slug: str) -> str:
    """Build the internal links nav HTML for a guide."""
    state_slug = get_state_for_guide(guide_slug)
    links = []

    if state_slug:
        state_name = slug_to_display_name(state_slug)
        links.append(
            f'<li><a href="/locations/{html.escape(state_slug)}/">Back to {html.escape(state_name)} driveways</a></li>'
        )
    links.append('<li><a href="/guides-hub/">View all driveway guides</a></li>')

    items = "\n    ".join(links)
    return f'''<nav class="guide-internal-links" aria-label="Related pages" style="max-width:1400px;margin:0 auto 2rem;padding:0 2rem;">
  <ul style="list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:1rem;justify-content:center;font-size:.95rem;">
    {items}
  </ul>
</nav>'''


def process_guide(guide_path: Path) -> bool:
    """Add or update internal links in a guide. Returns True if changed."""
    slug = guide_path.name
    index_path = guide_path / "index.html"
    if not index_path.exists():
        return False

    content = index_path.read_text(encoding="utf-8")
    new_nav = build_internal_links_html(slug)

    if NAV_PATTERN.search(content):
        new_content = NAV_PATTERN.sub(new_nav, content, count=1)
    else:
        # Insert before footer
        footer_match = re.search(r"(\s*)<footer", content)
        if footer_match:
            indent = footer_match.group(1)
            new_content = content.replace(
                f"{indent}<footer",
                f"{indent}{new_nav}\n\n{indent}<footer",
                1,
            )
        else:
            return False

    if new_content != content:
        index_path.write_text(new_content, encoding="utf-8")
        return True
    return False


def main():
    count = 0
    for sub in sorted(GUIDES_DIR.iterdir()):
        if sub.is_dir() and (sub / "index.html").exists():
            if process_guide(sub):
                count += 1
    print(f"Updated {count} guide(s) with internal links.")


if __name__ == "__main__":
    main()
