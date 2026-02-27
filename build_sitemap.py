#!/usr/bin/env python3
"""
Build sitemap.xml for septicsystemshq.com
TODO: Ensure BASE_URL and paths reflect septic site structure.
"""

from datetime import date
from pathlib import Path

BASE_URL = "https://drivewayzusa.co"
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = PROJECT_ROOT / "sitemap.xml"
ROBOTS_FILE = PROJECT_ROOT / "robots.txt"
TODAY = date.today().isoformat()

# Core pages
CORE_PAGES = [
    ("/",                    "1.0", "weekly"),
    ("/guides-hub/",         "0.9", "daily"),
    ("/locations/",          "0.9", "monthly"),
    ("/for-homeowners/",     "0.9", "monthly"),
    ("/for-contractors/",     "0.9", "monthly"),
    ("/cost-calculator/",     "0.8", "monthly"),
    ("/for-homeowners-quiz/", "0.8", "monthly"),
]

def build_url_entry(loc: str, priority: str, changefreq: str, lastmod: str = TODAY) -> str:
    return f"""  <url>
    <loc>{BASE_URL}{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""

def main():
    entries = []
    for path, priority, changefreq in CORE_PAGES:
        entries.append(build_url_entry(path, priority, changefreq))
    guides_dir = PROJECT_ROOT / "guides"
    if guides_dir.exists():
        for f in sorted(guides_dir.glob("*/index.html")):
            entries.append(build_url_entry(f"/guides/{f.parent.name}/", "0.8", "monthly"))
    urls = "\n".join(entries)
    output = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>'
    OUTPUT_FILE.write_text(output, encoding="utf-8")
    ROBOTS_FILE.write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
