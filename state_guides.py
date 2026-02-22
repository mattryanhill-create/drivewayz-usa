#!/usr/bin/env python3
"""
State-to-guides mapping for internal linking.
Maps state slugs to relevant guide slugs and titles.
Used by generate_state_pages.py (Featured guides section) and add_guide_links.py (Back to state).
"""

import json
import os
import re
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent
GUIDES_DIR = PROJECT_ROOT / "guides"
HERO_IMAGE_MAP_PATH = PROJECT_ROOT / "hero-image-map.json"

# State slugs in priority order (longer first for regex matching, e.g. new-york before new)
_STATE_SLUGS = [
    "new-hampshire", "new-jersey", "new-mexico", "new-york",
    "north-carolina", "north-dakota", "northern-mariana-islands",
    "rhode-island", "south-carolina", "south-dakota",
    "us-virgin-islands", "washington-dc", "west-virginia",
    "american-samoa", "puerto-rico",
    "alabama", "alaska", "arizona", "arkansas", "california",
    "colorado", "connecticut", "delaware", "florida", "georgia",
    "guam", "hawaii", "idaho", "illinois", "indiana", "iowa",
    "kansas", "kentucky", "louisiana", "maine", "maryland",
    "massachusetts", "michigan", "minnesota", "mississippi",
    "missouri", "montana", "nebraska", "nevada", "ohio",
    "oklahoma", "oregon", "pennsylvania", "tennessee", "texas",
    "utah", "vermont", "virginia", "washington", "wisconsin", "wyoming",
]

# City suffix (e.g. -portland-or, -louisville-ky) -> state slug
_CITY_STATE_ABBR = {
    "or": "oregon", "ky": "kentucky", "ks": "kansas", "mo": "missouri",
    "ia": "iowa", "tx": "texas", "fl": "florida", "ca": "california",
    "wa": "washington", "co": "colorado", "az": "arizona", "nv": "nevada",
    "ut": "utah", "id": "idaho", "mn": "minnesota", "wi": "wisconsin",
    "il": "illinois", "mi": "michigan", "oh": "ohio", "in": "indiana",
    "tn": "tennessee", "ga": "georgia", "nc": "north-carolina",
    "sc": "south-carolina", "pa": "pennsylvania", "ny": "new-york",
    "ma": "massachusetts", "ct": "connecticut", "nj": "new-jersey",
    "va": "virginia", "md": "maryland", "dc": "washington-dc",
}


def _load_hero_map() -> dict:
    if HERO_IMAGE_MAP_PATH.exists():
        with open(HERO_IMAGE_MAP_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _get_guide_title(slug: str, hero_map: dict) -> str:
    key = f"guides/{slug}/index.html"
    if key in hero_map:
        return hero_map[key].get("title", "").strip()
    # Fallback: read <title> from index.html
    path = GUIDES_DIR / slug / "index.html"
    if path.exists():
        try:
            content = path.read_text(encoding="utf-8")
            m = re.search(r"<title>([^<]+)</title>", content)
            if m:
                t = m.group(1).strip()
                if "|" in t:
                    t = t.split("|")[0].strip()
                return t
        except Exception:
            pass
    # Slug to title fallback
    return slug.replace("-", " ").title()


def _extract_state_from_slug(slug: str) -> Optional[str]:
    """Extract state slug from guide slug. Returns None if not state-specific."""
    slug_lower = slug.lower()
    # City guides: contractors-in-portland-or, contractors-in-louisville-ky, contractors-in-kansas-city-mo
    m = re.search(r"in-[a-z\-]+-([a-z]{2})(?:\b|-)", slug_lower)
    if m:
        abbr = m.group(1).lower()
        if abbr in _CITY_STATE_ABBR:
            return _CITY_STATE_ABBR[abbr]
    # State patterns: -in-florida-, -for-florida-homes, -for-florida-heat, florida-local-pricing, florida-2026-price-guide
    for state in _STATE_SLUGS:
        if state in slug_lower:
            # Prefer patterns that clearly indicate state-specific content
            if (
                f"-in-{state}-" in slug_lower
                or f"-in-{state}" in slug_lower
                or f"-for-{state}-" in slug_lower
                or f"-for-{state}" in slug_lower
                or f"-{state}-local-pricing" in slug_lower
                or f"-{state}-2026" in slug_lower
                or f"-{state}-homes" in slug_lower
                or f"-{state}-heat" in slug_lower
                or f"-{state}-material" in slug_lower
                or f"regulations-in-{state}" in slug_lower
            ):
                return state
    return None


def build_state_guides_map(max_per_state: int = 5, sort_by_recent: bool = False) -> dict:
    """
    Build mapping state_slug -> [(guide_slug, title), ...].
    Each state gets up to max_per_state guides.
    If sort_by_recent: use most recently modified guides first; else prioritize cost/permits/material.
    """
    hero_map = _load_hero_map()
    by_state: dict[str, list[tuple[str, str, float]]] = {}  # (slug, title, mtime)

    if not GUIDES_DIR.exists():
        return by_state

    for sub in sorted(GUIDES_DIR.iterdir()):
        if not sub.is_dir():
            continue
        slug = sub.name
        index_path = sub / "index.html"
        if index_path.exists():
            state = _extract_state_from_slug(slug)
            if state:
                title = _get_guide_title(slug, hero_map)
                mtime = index_path.stat().st_mtime
                if state not in by_state:
                    by_state[state] = []
                by_state[state].append((slug, title, mtime))

    def priority(item: tuple[str, str, float]) -> int:
        s = item[0].lower()
        if "cost" in s or "pricing" in s:
            return 0
        if "permits" in s or "regulations" in s:
            return 1
        if "best-driveway" in s or "material" in s:
            return 2
        if "contractors" in s:
            return 3
        return 4

    result: dict[str, list[tuple[str, str]]] = {}
    for state in by_state:
        items = by_state[state]
        if sort_by_recent:
            items = sorted(items, key=lambda x: x[2], reverse=True)
        else:
            items = sorted(items, key=lambda x: priority(x))
        result[state] = [(slug, title) for slug, title, _ in items[:max_per_state]]
    return result


def get_state_for_guide(guide_slug: str) -> Optional[str]:
    """Return state slug for a guide, or None if not state-specific."""
    return _extract_state_from_slug(guide_slug)


def slug_to_display_name(slug: str) -> str:
    """Convert state slug to display name (e.g. 'new-york' -> 'New York')."""
    return slug.replace("-", " ").title()
