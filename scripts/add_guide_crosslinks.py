#!/usr/bin/env python3
"""
Add contextual cross-links to guide pages. Inserts a "Related Guides" section
before </main> in each guide index.html. Dry-run by default; use --apply to write.
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Paths (relative to script's parent)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
GUIDES_DIR = PROJECT_ROOT / "guides"

# State slugs used in locations/ and in guide filenames (full names, hyphenated)
STATE_SLUGS = [
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi",
    "missouri", "montana", "nebraska", "nevada", "new-hampshire", "new-jersey",
    "new-mexico", "new-york", "north-carolina", "north-dakota", "ohio",
    "oklahoma", "oregon", "pennsylvania", "rhode-island", "south-carolina",
    "south-dakota", "tennessee", "texas", "utah", "vermont", "virginia",
    "washington", "west-virginia", "wisconsin", "wyoming", "washington-dc",
]

# 2-letter state abbreviation -> location slug (for contractor guides: phoenix-az, etc.)
STATE_ABBREV_TO_SLUG: Dict[str, str] = {
    "al": "alabama", "ak": "alaska", "az": "arizona", "ar": "arkansas",
    "ca": "california", "co": "colorado", "ct": "connecticut", "de": "delaware",
    "fl": "florida", "ga": "georgia", "hi": "hawaii", "id": "idaho",
    "il": "illinois", "in": "indiana", "ia": "iowa", "ks": "kansas",
    "ky": "kentucky", "la": "louisiana", "me": "maine", "md": "maryland",
    "ma": "massachusetts", "mi": "michigan", "mn": "minnesota", "ms": "mississippi",
    "mo": "missouri", "mt": "montana", "ne": "nebraska", "nv": "nevada",
    "nh": "new-hampshire", "nj": "new-jersey", "nm": "new-mexico", "ny": "new-york",
    "nc": "north-carolina", "nd": "north-dakota", "oh": "ohio", "ok": "oklahoma",
    "or": "oregon", "pa": "pennsylvania", "ri": "rhode-island", "sc": "south-carolina",
    "sd": "south-dakota", "tn": "tennessee", "tx": "texas", "ut": "utah",
    "vt": "vermont", "va": "virginia", "wa": "washington", "wv": "west-virginia",
    "wi": "wisconsin", "wy": "wyoming", "dc": "washington-dc",
}

# General topical anchors for state guides
COST_GUIDE_SLUG = "driveway-cost-breakdown-labor-materials-and-equipment"
MATERIALS_GUIDE_SLUG = "concrete-vs-asphalt-vs-gravel"
PERMITS_GUIDE_SLUG = "driveway-permits-how-much-do-they-cost"
CONTRACTOR_VET_GUIDE_SLUG = "how-to-vet-a-driveway-contractor-questions-to-ask"

# Keywords for matching general guides (slug substring -> priority for topical matching)
TOPICAL_KEYWORDS = {
    "cost": ["cost", "price", "pricing", "budget", "breakdown"],
    "material": ["material", "asphalt", "concrete", "gravel", "paver", "paving"],
    "repair": ["repair", "fix", "crack", "resurface", "overlay"],
    "permit": ["permit", "regulation", "code"],
    "contractor": ["contractor", "hire", "vet", "choose", "bid"],
    "maintenance": ["maintenance", "seal", "sealcoat", "clean"],
    "drainage": ["drainage", "drain", "water", "flood"],
    "design": ["design", "style", "aesthetic"],
    "climate": ["climate", "weather", "hot", "cold", "rainy", "coastal"],
}


def find_state_in_slug(slug: str) -> Optional[str]:
    """Return location slug if slug contains a state name, else None."""
    lower = slug.lower()
    for s in sorted(STATE_SLUGS, key=len, reverse=True):
        # Match state as a distinct segment (before -homes, -local, etc.)
        if f"-{s}-" in lower or lower.startswith(s + "-") or lower.endswith("-" + s):
            return s
    return None


def categorize_guide(slug: str) -> Tuple[str, Optional[str]]:
    """
    Return (category, state_slug). Categories: state_cost, state_material, state_permit,
    state_contractor, climate, general.
    """
    lower = slug.lower()

    # State contractor: driveway-contractors-in-{city}-{abbrev}-how-to-choose or -local-guide
    m = re.match(
        r"driveway-contractors-in-[a-z0-9\-]+-([a-z]{2})-(?:how-to-choose|local-guide)",
        lower,
    )
    if m:
        abbr = m.group(1).lower()
        state = STATE_ABBREV_TO_SLUG.get(abbr)
        if state:
            return ("state_contractor", state)

    # State cost: asphalt-driveway-cost-in-{state}-local-pricing
    m = re.match(r"asphalt-driveway-cost-in-([a-z\-]+)-local-pricing", lower)
    if m:
        state = _normalize_state_from_match(m.group(1))
        if state:
            return ("state_cost_asphalt", state)

    # State cost: concrete-driveway-cost-in-{state}-2026-price-guide
    m = re.match(r"concrete-driveway-cost-in-([a-z\-]+)-2026-price-guide", lower)
    if m:
        state = _normalize_state_from_match(m.group(1))
        if state:
            return ("state_cost_concrete", state)

    # State material: best-driveway-material-for-{state}-homes
    m = re.match(r"best-driveway-material-for-([a-z\-]+)-homes", lower)
    if m:
        state = _normalize_state_from_match(m.group(1))
        if state and state in STATE_SLUGS:
            return ("state_material", state)

    # State permit: driveway-permits-and-regulations-in-{state}
    m = re.match(r"driveway-permits-and-regulations-in-([a-z\-]+)(?:$|[-\"])", lower)
    if m:
        state = _normalize_state_from_match(m.group(1))
        if state:
            return ("state_permit", state)

    # Climate: hot-climates-, cold-climates-, rainy-climates-, coastal-regions-
    if any(
        prefix in lower
        for prefix in ("hot-climates-", "cold-climates-", "rainy-climates-", "coastal-regions-")
    ):
        state = find_state_in_slug(slug)
        return ("climate", state)

    # driveway-for-climate-zone-
    if "driveway-for-climate-zone-" in lower:
        return ("climate", None)

    return ("general", None)


def _normalize_state_from_match(seg: str) -> Optional[str]:
    """Convert extracted segment to a valid STATE_SLUGS entry."""
    s = seg.lower().strip()
    if s in STATE_SLUGS:
        return s
    # Try with hyphens for multi-word states
    normalized = s.replace(" ", "-")
    if normalized in STATE_SLUGS:
        return normalized
    return None


def extract_title_and_h1(html: str) -> Tuple[str, str]:
    """Extract <title> and <h1> content. Returns (title_text, h1_text)."""
    title = ""
    h1 = ""

    title_m = re.search(r"<title>\s*([^<]+?)\s*\|", html, re.IGNORECASE | re.DOTALL)
    if title_m:
        title = re.sub(r"\s+", " ", title_m.group(1).strip())

    h1_m = re.search(r"<h1[^>]*>([^<]+)</h1>", html, re.IGNORECASE | re.DOTALL)
    if h1_m:
        h1 = re.sub(r"\s+", " ", h1_m.group(1).strip())

    return (title or h1, h1 or title)


def get_guide_title(html: str, slug: str) -> str:
    """Derive a display title from title/h1 or slug."""
    title, h1 = extract_title_and_h1(html)
    if title:
        return title
    return slug.replace("-", " ").title()


def discover_all_guides() -> Dict[str, dict]:
    """Scan guides/ and return {slug: {path, title, category, state}}. titles filled later."""
    guides = {}
    if not GUIDES_DIR.exists():
        return guides
    for subdir in sorted(GUIDES_DIR.iterdir()):
        if not subdir.is_dir():
            continue
        idx = subdir / "index.html"
        if not idx.exists():
            continue
        slug = subdir.name
        cat, state = categorize_guide(slug)
        guides[slug] = {
            "path": idx,
            "slug": slug,
            "category": cat,
            "state": state,
        }
    return guides


def enrich_titles(guides: Dict[str, dict]) -> None:
    """Read each guide and fill title."""
    for slug, g in guides.items():
        try:
            html = g["path"].read_text(encoding="utf-8", errors="replace")
            g["title"] = get_guide_title(html, slug)
        except Exception:
            g["title"] = slug.replace("-", " ").title()


def links_for_state_guide(
    slug: str,
    category: str,
    state: str,
    guides: Dict[str, dict],
) -> List[Tuple[str, str]]:
    """Build list of (href, title) for state-specific guides."""
    out: List[Tuple[str, str]] = []
    seen: Set[str] = set()

    # 1. State location page
    loc_href = f"/locations/{state}/"
    if loc_href not in seen:
        out.append((loc_href, f"Driveway services in {state.replace('-', ' ').title()}"))
        seen.add(loc_href)

    # 2. Other guides for same state
    state_patterns = [
        ("asphalt-driveway-cost-in-" + state + "-local-pricing", "state_cost_asphalt"),
        ("concrete-driveway-cost-in-" + state + "-2026-price-guide", "state_cost_concrete"),
        ("best-driveway-material-for-" + state + "-homes", "state_material"),
        ("driveway-permits-and-regulations-in-" + state, "state_permit"),
    ]
    for pattern, _ in state_patterns:
        if pattern in guides and pattern != slug:
            href = f"/guides/{pattern}/"
            if href not in seen:
                out.append((href, guides[pattern]["title"]))
                seen.add(href)

    # Contractor guides for this state (state is full name; contractor slugs use abbrev)
    abbr = next((a for a, s in STATE_ABBREV_TO_SLUG.items() if s == state), None)
    if abbr:
        for gslug, g in guides.items():
            if g["category"] == "state_contractor" and g["state"] == state and gslug != slug:
                href = f"/guides/{gslug}/"
                if href not in seen:
                    out.append((href, g["title"]))
                    seen.add(href)

    # 3. One general topical guide
    if "cost" in category:
        general_href = f"/guides/{COST_GUIDE_SLUG}/"
        if general_href not in seen and COST_GUIDE_SLUG in guides:
            out.append((general_href, guides[COST_GUIDE_SLUG]["title"]))
            seen.add(general_href)
    elif "material" in category:
        general_href = f"/guides/{MATERIALS_GUIDE_SLUG}/"
        if general_href not in seen and MATERIALS_GUIDE_SLUG in guides:
            out.append((general_href, guides[MATERIALS_GUIDE_SLUG]["title"]))
            seen.add(general_href)
    elif "permit" in category:
        general_href = f"/guides/{PERMITS_GUIDE_SLUG}/"
        if general_href not in seen and PERMITS_GUIDE_SLUG in guides:
            out.append((general_href, guides[PERMITS_GUIDE_SLUG]["title"]))
            seen.add(general_href)
    elif "contractor" in category:
        general_href = f"/guides/{CONTRACTOR_VET_GUIDE_SLUG}/"
        if general_href not in seen and CONTRACTOR_VET_GUIDE_SLUG in guides:
            out.append((general_href, guides[CONTRACTOR_VET_GUIDE_SLUG]["title"]))
            seen.add(general_href)
    else:
        general_href = f"/guides/{MATERIALS_GUIDE_SLUG}/"
        if general_href not in seen and MATERIALS_GUIDE_SLUG in guides:
            out.append((general_href, guides[MATERIALS_GUIDE_SLUG]["title"]))
            seen.add(general_href)

    return out


def links_for_general_guide(slug: str, guides: Dict[str, dict]) -> List[Tuple[str, str]]:
    """Build 2-3 thematically related links for general/topical guides using keyword matching."""
    lower = slug.lower()
    scores: List[Tuple[int, str]] = []

    for gslug, g in guides.items():
        if gslug == slug:
            continue
        if g["category"] not in ("general", "climate"):
            continue
        g_lower = gslug.lower()
        score = 0
        for topic, keywords in TOPICAL_KEYWORDS.items():
            slug_has = any(k in lower for k in keywords)
            guide_has = any(k in g_lower for k in keywords)
            if slug_has and guide_has:
                score += 10
        if score > 0:
            scores.append((score, gslug))

    scores.sort(key=lambda x: (-x[0], x[1]))
    out: List[Tuple[str, str]] = []
    seen: Set[str] = set()
    for _, gslug in scores[:3]:
        href = f"/guides/{gslug}/"
        if href not in seen:
            out.append((href, guides[gslug]["title"]))
            seen.add(href)

    # Fallback: add popular guides if no keyword matches
    if len(out) < 2:
        fallbacks = [COST_GUIDE_SLUG, MATERIALS_GUIDE_SLUG, "gravel-pothole-repair"]
        for fs in fallbacks:
            if fs in guides and fs != slug and len(out) < 3:
                href = f"/guides/{fs}/"
                if href not in seen:
                    out.append((href, guides[fs]["title"]))
                    seen.add(href)

    return out[:3]


def links_for_climate_guide(slug: str, state: Optional[str], guides: Dict[str, dict]) -> List[Tuple[str, str]]:
    """Links for climate guides: state location if state, plus 2 topical."""
    out: List[Tuple[str, str]] = []
    seen: Set[str] = set()

    if state:
        loc_href = f"/locations/{state}/"
        out.append((loc_href, f"Driveway services in {state.replace('-', ' ').title()}"))
        seen.add(loc_href)

    topical = links_for_general_guide(slug, guides)
    for href, title in topical:
        if href not in seen and len(out) < 4:
            out.append((href, title))
            seen.add(href)

    return out


def build_related_section(links: List[Tuple[str, str]]) -> str:
    """Build the Related Guides HTML section."""
    lines = [
        '',
        '<section class="related-guides">',
        '  <h2>Related Guides</h2>',
        '  <ul>',
    ]
    for href, title in links:
        # Escape HTML in title
        safe_title = (
            title.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        lines.append(f'    <li><a href="{href}">{safe_title}</a></li>')
    lines.extend(["  </ul>", "</section>", ""])
    return "\n".join(lines)


def has_existing_related_section(html: str) -> bool:
    """Return True if a <section class=\"related-guides\"> already exists."""
    return 'class="related-guides"' in html or "class='related-guides'" in html


def run(dry_run: bool) -> int:
    """Main entry. Returns number of files modified."""
    guides = discover_all_guides()
    if not guides:
        print("No guides found.", file=sys.stderr)
        return 0

    enrich_titles(guides)
    modified = 0

    for slug, g in sorted(guides.items()):
        path = g["path"]
        try:
            html = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"SKIP {path}: read error: {e}", file=sys.stderr)
            continue

        if has_existing_related_section(html):
            continue

        category = g["category"]
        state = g.get("state")

        if category.startswith("state_"):
            links = links_for_state_guide(slug, category, state, guides)
        elif category == "climate":
            links = links_for_climate_guide(slug, state, guides)
        else:
            links = links_for_general_guide(slug, guides)

        if not links:
            continue

        section_html = build_related_section(links)
        # Insert section just before </main>
        main_close = re.search(r"(\n\s*)</main>", html)
        if not main_close:
            continue
        indent = main_close.group(1)
        # We want: section before \n  </main>, with section items indented one more
        insertion = (
            "\n"
            + indent
            + '<section class="related-guides">\n'
            + indent
            + "  <h2>Related Guides</h2>\n"
            + indent
            + "  <ul>\n"
        )
        for href, title in links:
            safe_title = (
                title.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
            insertion += indent + f'    <li><a href="{href}">{safe_title}</a></li>\n'
        insertion += indent + "  </ul>\n" + indent + "</section>\n" + indent + "</main>"

        new_html = re.sub(r"\n\s*</main>", insertion, html, count=1)
        if new_html == html:
            continue

        print(f"MODIFY {path}")
        for href, title in links:
            print(f"  + {href} -> {title}")

        if not dry_run:
            path.write_text(new_html, encoding="utf-8")
        modified += 1

    return modified


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add Related Guides cross-links to guide pages. Dry-run by default."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes to files",
    )
    args = parser.parse_args()
    n = run(dry_run=not args.apply)
    mode = "DRY-RUN" if not args.apply else "APPLIED"
    print(f"\n{mode}: {n} guide(s) would be / were modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
