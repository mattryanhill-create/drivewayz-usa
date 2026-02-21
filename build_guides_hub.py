#!/usr/bin/env python3
"""
build_guides_hub.py

Scans all /guides/*/index.html files, extracts title + meta description,
and rebuilds guides-hub/index.html with all guides listed as cards.
Also assigns categories based on keywords in the title.

Run from Cursor Terminal: python3 build_guides_hub.py
Then: git add guides-hub/index.html && git commit -m "Rebuild guides hub with all guides" && git push origin main
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
GUIDES_DIR = PROJECT_ROOT / "guides"
OUTPUT_FILE = PROJECT_ROOT / "guides-hub" / "index.html"

# ── Category mapping: keyword fragments → category slug + label ──────────────
CATEGORY_RULES = [
    (["repair", "fix", "crack", "pothole", "resurface", "resurfac"], "repair", "Repair"),
    (["maintenance", "sealing", "sealcoat", "clean", "stain", "winterize", "salt", "protect", "care", "seasonal", "spring", "fall", "summer", "winter"], "maintenance", "Maintenance"),
    (["cost", "price", "budget", "cheap", "afford", "expensive", "roi", "value"], "planning", "Planning"),
    (["permit", "code", "regulation", "easement", "right-of-way", "zoning", "setback", "hoa", "legal", "agreement"], "planning", "Planning"),
    (["plan", "design", "layout", "dimension", "size", "width", "length", "slope", "drainage", "grade", "grading", "excavat"], "planning", "Planning"),
    (["asphalt", "concrete", "gravel", "paver", "cobblestone", "basalt", "chip seal", "tar", "brick", "stone", "pebble", "turf", "shell", "glass", "material"], "materials", "Materials"),
    (["eco", "permeable", "green", "recycled", "sustainable", "solar", "rain", "wetland", "environm"], "eco-friendly", "Eco-Friendly"),
    (["basic", "beginner", "what is", "intro", "guide to", "overview", "types", "lifespan", "terminology", "glossary"], "beginner", "Beginner"),
    (["technical", "base", "subgrade", "reinforc", "rebar", "compaction", "joint", "expansion", "control joint", "thickness", "depth", "weight", "load", "engineer"], "technical", "Technical"),
]

BADGE_COLORS = {
    "repair":       "#dc2626",
    "maintenance":  "#f59e0b",
    "planning":     "#10b981",
    "materials":    "#8b5cf6",
    "eco-friendly": "#059669",
    "beginner":     "#1d4ed8",
    "technical":    "#374151",
    "general":      "#6b7280",
}


def extract_meta(filepath: Path) -> dict:
    """Parse <title> and <meta name="description"> from an HTML file."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}

    title_match = re.search(r"<title>(.+?)</title>", content, re.IGNORECASE | re.DOTALL)
    desc_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
        content, re.IGNORECASE
    ) or re.search(
        r'<meta\s+content=["\']([^"\']+)["\']\s+name=["\']description["\']',
        content, re.IGNORECASE
    )

    raw_title = title_match.group(1).strip() if title_match else filepath.stem.replace("-", " ").title()
    # Strip " | Drivewayz USA Guides" suffix if present
    clean_title = re.sub(r"\s*\|.*$", "", raw_title).strip()
    desc = desc_match.group(1).strip() if desc_match else f"Expert guide to {clean_title.lower()} from Drivewayz USA."

    return {"title": clean_title, "desc": desc}


def categorize(title: str) -> tuple:
    """Return (slug, label) for the best matching category."""
    lower = title.lower()
    for keywords, slug, label in CATEGORY_RULES:
        if any(kw in lower for kw in keywords):
            return slug, label
    return "general", "Guide"


def estimate_read_time(desc: str, title: str) -> int:
    """Rough read-time estimate: 12 min default, scaled by title length."""
    words = len(title.split()) + len(desc.split())
    return max(8, min(25, 10 + words // 20))


def build_card(guide: dict) -> str:
    slug, label = categorize(guide["title"])
    color = BADGE_COLORS.get(slug, "#6b7280")
    read_time = estimate_read_time(guide["desc"], guide["title"])
    href = f"/guides/{guide['slug']}/"
    return f"""
        <article class="guide-card" data-category="{slug}">
          <div class="guide-card-content">
            <span class="guide-card-badge" style="background:{color};color:#fff;display:inline-block;padding:.3rem .8rem;border-radius:20px;font-size:.75rem;font-weight:700;text-transform:uppercase;margin-bottom:.75rem;">{label}</span>
            <h3>{guide['title']}</h3>
            <p>{guide['desc']}</p>
            <div class="guide-meta">
              <span>&#x23F1; {read_time} min read</span>
            </div>
            <a href="{href}" class="read-more">Read Full Guide &rarr;</a>
          </div>
        </article>"""


def build_hub(guides: list) -> str:
    total = len(guides)
    cards_html = "\n".join(build_card(g) for g in guides)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Driveway Guides | Expert Tips &amp; How-To Guides | Drivewayz USA</title>
  <meta name="description" content="Browse {total}+ expert driveway guides covering installation, repair, maintenance, costs, and materials. Learn from Drivewayz USA's 15+ years of expertise.">
  <link rel="stylesheet" href="/main.css">
  <style>
    .guides-hero{{
      position:relative;height:40vh;min-height:300px;
      display:flex;align-items:center;justify-content:center;
      background:linear-gradient(135deg,var(--primary-dark) 0%,var(--primary-color) 100%);
      margin-top:100px;
    }}
    .guides-hero-content{{text-align:center;color:#fff;padding:2rem;}}
    .guides-hero h1{{font-size:2.5rem;font-weight:800;margin-bottom:1rem;}}
    .guides-hero p{{font-size:1.2rem;opacity:.95;}}
    .guides-section{{padding:4rem 0;background-color:var(--bg-light);}}
    .guides-grid{{
      display:grid;
      grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
      gap:1.5rem;margin-top:2rem;
    }}
    .guide-card{{
      background:#fff;border-radius:12px;
      box-shadow:0 2px 12px rgba(0,0,0,.08);
      transition:transform .3s,box-shadow .3s;
      padding:1.5rem;
    }}
    .guide-card:hover{{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.12);}}
    .guide-card h3{{font-size:1.05rem;margin:.5rem 0 .75rem;color:var(--text-dark);}}
    .guide-card p{{color:var(--text-light);font-size:.9rem;line-height:1.6;margin-bottom:1rem;}}
    .guide-meta{{font-size:.85rem;color:var(--text-light);margin-bottom:.75rem;}}
    .read-more{{color:var(--primary-color);font-weight:600;text-decoration:none;font-size:.9rem;}}
    .read-more:hover{{color:var(--primary-dark);}}
    @media(max-width:768px){{.guides-grid{{grid-template-columns:1fr;}}.guides-hero h1{{font-size:2rem;}}}}
  </style>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-V08M9YKRR7"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-V08M9YKRR7');
  </script>
</head>
<body>
  <!-- Navigation -->
  <nav class="navbar" id="navbar">
    <div class="container nav-container">
      <div class="logo">
        <a href="/"><img src="/images/logov3.png?v=3" alt="Drivewayz USA"></a>
      </div>
      <ul class="nav-links">
        <li><a href="/">Home</a></li>
        <li><a href="/#services">Services</a></li>
        <li><a href="/#why-choose">Why Us</a></li>
        <li><a href="/locations/">Locations</a></li>
        <li><a href="/guides-hub/" style="color:var(--primary-color);">Guides</a></li>
        <li><a href="/#contact">Contact</a></li>
      </ul>
      <button class="cta-button-small" onclick="window.location.href='/#contact'">Free Estimate</button>
    </div>
  </nav>

  <!-- Hero -->
  <section class="guides-hero">
    <div class="guides-hero-content">
      <h1>Driveway Guides &amp; Expert Tips</h1>
      <p>Learn from our 15+ years of American driveway expertise. {total} guides covering every topic.</p>
    </div>
  </section>

  <!-- Guides Section -->
  <section class="guides-section" id="all-guides">
    <div class="container">
      <div class="guides-grid">
{cards_html}
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section style="background:#fff;padding:4rem 0;text-align:center;">
    <div class="container">
      <h2 class="section-title">Need Professional Help?</h2>
      <p class="section-subtitle">Get a free estimate from our driveway experts. Serving all 50 states.</p>
      <button class="cta-button" onclick="window.location.href='/#contact'">Get Your Free Estimate</button>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <p>&copy; 2026 Drivewayz USA. Licensed &amp; Insured. Serving the United States with Pride.</p>
      <p class="footer-links">
        <a href="/#services">Services</a> &bull;
        <a href="/locations/">Locations</a> &bull;
        <a href="/guides-hub/">Guides</a> &bull;
        <a href="/#contact">Contact</a>
      </p>
    </div>
  </footer>

  <script src="/main.js" defer></script>
  <script src="/js/guides-enhancements.js" defer></script>
</body>
</html>
"""


def main():
    if not GUIDES_DIR.exists():
        print(f"ERROR: guides/ directory not found at {GUIDES_DIR}")
        return

    html_files = sorted(GUIDES_DIR.glob("*/index.html"))
    print(f"Found {len(html_files)} guide index files in guides/")

    guides = []
    for f in html_files:
        meta = extract_meta(f)
        if not meta:
            continue
        guides.append({
            "slug": f.parent.name,
            "title": meta["title"],
            "desc": meta["desc"],
        })

    # Sort alphabetically by title
    guides.sort(key=lambda g: g["title"].lower())

    print(f"Building guides-hub/index.html with {len(guides)} guides...")
    hub_html = build_hub(guides)
    OUTPUT_FILE.write_text(hub_html, encoding="utf-8")
    print(f"Done. Written to {OUTPUT_FILE}")
    print(f"\nNext steps:")
    print(f"  git add guides-hub/index.html")
    print(f"  git commit -m 'Rebuild guides hub: {len(guides)} guides listed'")
    print(f"  git push origin main")


if __name__ == "__main__":
    main()
