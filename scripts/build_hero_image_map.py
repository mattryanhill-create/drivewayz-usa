#!/usr/bin/env python3
"""
Build hero-image-map.json from hero-audit.json.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "hero-audit.json"
OUTPUT_PATH = ROOT / "hero-image-map.json"


CLUSTER_KEYWORDS = {
    "gravel": ["rural gravel driveway", "gravel driveway home", "crushed stone driveway"],
    "asphalt": ["asphalt driveway residential", "blacktop driveway home", "asphalt paving crew"],
    "concrete": ["concrete driveway home", "concrete pour driveway", "finished concrete driveway"],
    "pavers": ["paver driveway installation", "stone paver driveway", "brick driveway home"],
    "materials": ["natural stone driveway", "modern driveway materials", "decorative driveway surface"],
    "drainage": ["driveway drainage system", "driveway culvert installation", "water runoff driveway"],
    "repair": ["driveway crack repair", "pothole driveway repair", "driveway resurfacing work"],
    "maintenance": ["driveway sealing maintenance", "driveway cleaning pressure wash", "winter driveway care"],
    "cost": ["new driveway project budget", "driveway installation estimate", "residential driveway planning"],
    "permits": ["residential driveway permit", "home driveway regulations", "driveway code compliance"],
    "eco": ["eco friendly driveway", "permeable driveway pavers", "recycled driveway materials"],
    "contractor": ["driveway contractor consultation", "home improvement contractor", "driveway project team"],
    "general": ["residential driveway installation", "suburban home driveway", "modern house driveway"],
}


def infer_cluster(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["gravel", "rural", "chip seal"]):
        return "gravel"
    if any(k in t for k in ["asphalt", "blacktop", "tar"]):
        return "asphalt"
    if any(k in t for k in ["concrete", "cement", "exposed aggregate"]):
        return "concrete"
    if any(k in t for k in ["paver", "pavestone", "cobblestone", "brick"]):
        return "pavers"
    if any(k in t for k in ["basalt", "oyster", "glass", "flagstone", "resin", "stone"]):
        return "materials"
    if any(k in t for k in ["drain", "drainage", "culvert", "flood", "runoff", "permeable"]):
        return "drainage"
    if any(k in t for k in ["repair", "fix", "crack", "pothole", "resurface", "overlay", "replacement"]):
        return "repair"
    if any(k in t for k in ["maintenance", "seal", "sealing", "clean", "washing", "winterize", "de-icer", "stain"]):
        return "maintenance"
    if any(k in t for k in ["cost", "price", "budget", "estimate", "value", "pricing"]):
        return "cost"
    if any(k in t for k in ["permit", "regulation", "code", "compliance", "hoa", "legal"]):
        return "permits"
    if any(k in t for k in ["eco", "sustainable", "recycled", "green", "carbon"]):
        return "eco"
    if any(k in t for k in ["contractor", "warranty", "insurance", "liability", "inspection", "safety"]):
        return "contractor"
    return "general"


def extract_title(path: Path) -> str:
    html = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    return match.group(1).strip() if match else path.stem


def humanize_slug(slug: str) -> str:
    return slug.replace("-", " ").title()


def main() -> None:
    data = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    targets = (
        data.get("gradient_only", [])
        + data.get("locations_gradient_only", [])
        + data.get("other_missing", [])
    )

    rotation = defaultdict(int)
    mapping: dict[str, dict[str, str]] = {}

    for rel in sorted(set(targets)):
        path = ROOT / rel
        title = extract_title(path)
        clean_title = title.split("|")[0].strip()

        if rel.startswith("locations/") and rel != "locations/index.html":
            state_slug = Path(rel).parts[1]
            state_name = humanize_slug(state_slug)
            search_keyword = f"{state_name.lower()} residential driveway"
            cluster = "state-location"
        elif rel == "locations/index.html":
            search_keyword = "american homes driveway"
            cluster = "locations-hub"
        elif rel == "guides-hub/index.html":
            search_keyword = "driveway installation tools"
            cluster = "guides-hub"
        elif rel.startswith("guides/"):
            cluster = infer_cluster(clean_title)
            options = CLUSTER_KEYWORDS.get(cluster, CLUSTER_KEYWORDS["general"])
            idx = rotation[cluster] % len(options)
            search_keyword = options[idx]
            rotation[cluster] += 1
        else:
            cluster = "general"
            options = CLUSTER_KEYWORDS["general"]
            idx = rotation[cluster] % len(options)
            search_keyword = options[idx]
            rotation[cluster] += 1

        mapping[rel] = {
            "title": clean_title,
            "search_keyword": search_keyword,
            "cluster": cluster,
        }

    OUTPUT_PATH.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    print(f"Mapped pages: {len(mapping)}")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
