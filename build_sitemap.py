#!/usr/bin/env python3
"""
build_sitemap.py

Generates sitemap.xml for drivewayzusa.co covering:
  - Core pages (index, guides-hub, locations)
  - All /guides/*.html pages
  - All /locations/*.html pages

Run from Cursor Terminal: python3 build_sitemap.py
Then: git add sitemap.xml robots.txt && git commit -m "Add sitemap.xml and robots.txt" && git push origin main
"""

from datetime import date
from pathlib import Path

BASE_URL = "https://www.drivewayzusa.com"
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = PROJECT_ROOT / "sitemap.xml"
ROBOTS_FILE = PROJECT_ROOT / "robots.txt"
TODAY = date.today().isoformat()

# Core pages: (path, priority, changefreq)
CORE_PAGES = [
    ("/",              "1.0", "weekly"),
    ("/guides-hub.html", "0.9", "daily"),
    ("/locations.html",  "0.9", "monthly"),
    ("/index.html#contact", "0.7", "monthly"),
]


def build_url_entry(loc: str, priority: str, changefreq: str, lastmod: str = TODAY) -> str:
    return f"""  <url>
    <loc>{BASE_URL}{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""


def collect_pages() -> list:
    entries = []

    # Core pages
    for path, priority, changefreq in CORE_PAGES:
        entries.append(build_url_entry(path, priority, changefreq))

    # Guides
    guides_dir = PROJECT_ROOT / "guides"
    if guides_dir.exists():
        guide_files = sorted(guides_dir.glob("*.html"))
        print(f"Found {len(guide_files)} guide pages")
        for f in guide_files:
            loc = f"/guides/{f.name}"
            entries.append(build_url_entry(loc, "0.8", "monthly"))
    else:
        print("WARNING: guides/ directory not found")

    # Location pages
    locations_dir = PROJECT_ROOT / "locations"
    if locations_dir.exists():
        loc_files = sorted(locations_dir.glob("*.html"))
        print(f"Found {len(loc_files)} location pages")
        for f in loc_files:
            loc = f"/locations/{f.name}"
            entries.append(build_url_entry(loc, "0.7", "monthly"))
    else:
        print("WARNING: locations/ directory not found")

    return entries


def build_sitemap(entries: list) -> str:
    urls_xml = "\n".join(entries)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_xml}
</urlset>
"""


def build_robots() -> str:
    return f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""


def main():
    print("Collecting pages...")
    entries = collect_pages()
    print(f"Total URLs: {len(entries)}")

    sitemap_xml = build_sitemap(entries)
    OUTPUT_FILE.write_text(sitemap_xml, encoding="utf-8")
    print(f"Written sitemap.xml ({len(entries)} URLs) to {OUTPUT_FILE}")

    robots_txt = build_robots()
    ROBOTS_FILE.write_text(robots_txt, encoding="utf-8")
    print(f"Written robots.txt to {ROBOTS_FILE}")

    print(f"\nNext steps:")
    print(f"  git add sitemap.xml robots.txt")
    print(f"  git commit -m 'Add sitemap.xml with {len(entries)} URLs and robots.txt'")
    print(f"  git push origin main")
    print(f"\nAfter pushing, submit to Google Search Console:")
    print(f"  {BASE_URL}/sitemap.xml")


if __name__ == "__main__":
    main()
