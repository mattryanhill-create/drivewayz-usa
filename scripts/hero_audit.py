#!/usr/bin/env python3
"""
Audit hero sections across guides and location pages.

Outputs hero-audit.json with:
{
  "has_photo": [...],
  "gradient_only": [...],
  "locations_gradient_only": [...],
  "other_missing": [...]
}
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
LOCATIONS_DIR = ROOT / "locations"
OUTPUT_PATH = ROOT / "hero-audit.json"


IMAGE_URL_RE = re.compile(r"url\(\s*['\"]?(?:\.\./)?/images/[^)'\"]+['\"]?\s*\)", re.IGNORECASE)


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def extract_css_block(html: str, selector: str) -> str:
    # Good enough for this codebase where hero CSS blocks are single-level.
    match = re.search(rf"{re.escape(selector)}\s*\{{([^{{}}]*)\}}", html, re.IGNORECASE | re.DOTALL)
    return match.group(1) if match else ""


def has_images_in_block(block: str) -> bool:
    return bool(IMAGE_URL_RE.search(block))


def has_gradient_in_block(block: str) -> bool:
    return "linear-gradient" in block.lower()


def guide_has_photo(html: str) -> bool:
    css_block = extract_css_block(html, ".guide-hero")
    if has_images_in_block(css_block):
        return True
    section_style = re.search(
        r'<section[^>]*class=["\']guide-hero["\'][^>]*style=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    return bool(section_style and has_images_in_block(section_style.group(1)))


def guide_gradient_only(html: str) -> bool:
    css_block = extract_css_block(html, ".guide-hero")
    section_present = bool(re.search(r'class=["\']guide-hero["\']', html, re.IGNORECASE))
    if not section_present:
        return False
    if guide_has_photo(html):
        return False
    if has_gradient_in_block(css_block):
        return True
    section_style = re.search(
        r'<section[^>]*class=["\']guide-hero["\'][^>]*style=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    return bool(section_style and "linear-gradient" in section_style.group(1).lower())


def location_gradient_only(path: Path, html: str) -> bool:
    # locations/index.html uses .hero, state pages use .state-hero with section inline style.
    if path == LOCATIONS_DIR / "index.html":
        hero_block = extract_css_block(html, ".hero")
        if has_images_in_block(hero_block):
            return False
        return has_gradient_in_block(hero_block)

    state_block = extract_css_block(html, ".state-hero")
    section_style = re.search(
        r'<section[^>]*class=["\']state-hero["\'][^>]*style=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    style_value = section_style.group(1) if section_style else ""
    has_photo = has_images_in_block(state_block) or has_images_in_block(style_value)
    if has_photo:
        return False
    return has_gradient_in_block(state_block) or ("linear-gradient" in style_value.lower())


def guides_hub_missing_photo(html: str) -> bool:
    block = extract_css_block(html, ".guides-hero")
    if not block:
        return False
    return has_gradient_in_block(block) and not has_images_in_block(block)


def main() -> None:
    has_photo: list[str] = []
    gradient_only: list[str] = []
    locations_gradient_only: list[str] = []
    other_missing: list[str] = []

    guide_files = sorted(GUIDES_DIR.glob("*/index.html"))
    for path in guide_files:
        html = path.read_text(encoding="utf-8", errors="ignore")
        if guide_has_photo(html):
            has_photo.append(relpath(path))
        elif guide_gradient_only(html):
            gradient_only.append(relpath(path))

    location_files = sorted(LOCATIONS_DIR.glob("*/index.html"))
    # Include locations hub at locations/index.html
    all_location_candidates = [LOCATIONS_DIR / "index.html"] + location_files
    for path in all_location_candidates:
        if path.name != "index.html" and path.parent.name == "state-page":
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        if location_gradient_only(path, html):
            locations_gradient_only.append(relpath(path))

    guides_hub = ROOT / "guides-hub" / "index.html"
    if guides_hub.exists():
        gh_html = guides_hub.read_text(encoding="utf-8", errors="ignore")
        if guides_hub_missing_photo(gh_html):
            other_missing.append(relpath(guides_hub))

    payload = {
        "has_photo": sorted(has_photo),
        "gradient_only": sorted(gradient_only),
        "locations_gradient_only": sorted(locations_gradient_only),
        "other_missing": sorted(other_missing),
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Guides with hero photos: {len(payload['has_photo'])}")
    print(f"Guides gradient-only: {len(payload['gradient_only'])}")
    print(f"Location pages needing photos: {len(payload['locations_gradient_only'])}")
    print(f"Other missing hero photos: {len(payload['other_missing'])}")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
