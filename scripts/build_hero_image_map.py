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


SCENE_WORDS = ("home", "residential", "front", "yard", "suburban", "rural")


CLUSTER_KEYWORDS = {
    # 3-5 words, always includes "driveway", and scene-oriented phrasing.
    "gravel": [
        "gravel driveway rural home",
        "residential gravel driveway front",
        "long gravel driveway home",
        "graded gravel driveway suburban",
        "fresh gravel driveway yard",
        "country gravel driveway home",
        "stone gravel driveway front",
        "gravel driveway home entrance",
    ],
    "asphalt": [
        "asphalt driveway suburban home",
        "blacktop driveway residential front",
        "new asphalt driveway home",
        "smooth asphalt driveway yard",
        "fresh blacktop driveway home",
        "asphalt driveway front entrance",
        "asphalt driveway curb appeal",
        "residential asphalt driveway front",
    ],
    "concrete": [
        "residential concrete driveway front",
        "new concrete driveway home",
        "finished concrete driveway yard",
        "concrete driveway suburban home",
        "clean concrete driveway front",
        "modern concrete driveway entrance",
        "concrete driveway home exterior",
        "concrete driveway front yard",
    ],
    "pavers": [
        "paver driveway front yard",
        "stone paver driveway home",
        "brick paver driveway front",
        "interlocking paver driveway home",
        "paver driveway suburban entrance",
        "patterned paver driveway yard",
        "residential paver driveway front",
        "paver driveway home exterior",
    ],
    "materials": [
        "natural stone driveway home",
        "decorative driveway surface home",
        "premium stone driveway front",
        "custom driveway material yard",
        "luxury driveway surface home",
        "textured driveway stone front",
        "hardscape driveway surface home",
        "modern stone driveway entrance",
    ],
    "drainage": [
        "driveway drainage residential home",
        "driveway culvert front yard",
        "driveway runoff suburban home",
        "sloped driveway drainage home",
        "driveway channel drain front",
        "wet driveway drainage yard",
        "permeable driveway drainage home",
        "stormwater driveway drainage home",
    ],
    "repair": [
        "driveway crack repair home",
        "pothole driveway repair front",
        "driveway resurfacing residential home",
        "damaged driveway repair yard",
        "driveway patch repair home",
        "driveway surface repair front",
        "driveway restoration suburban home",
        "driveway crack repair yard",
    ],
    "maintenance": [
        "driveway sealing residential home",
        "driveway cleaning suburban home",
        "winter driveway care home",
        "sealed driveway surface front",
        "driveway upkeep front yard",
        "driveway maintenance home exterior",
        "clean driveway surface home",
        "maintained driveway front yard",
    ],
    "cost": [
        "driveway project residential home",
        "new driveway residential front",
        "driveway estimate home exterior",
        "residential driveway front yard",
        "budget driveway suburban home",
        "driveway replacement home front",
        "driveway install residential home",
        "driveway remodel front yard",
    ],
    "permits": [
        "residential driveway permit home",
        "driveway code compliance home",
        "home driveway permit front",
        "driveway permit suburban home",
        "city driveway permit home",
        "driveway zoning residential home",
        "approved driveway plan home",
        "legal driveway access home",
    ],
    "eco": [
        "eco driveway residential home",
        "permeable driveway pavers home",
        "recycled driveway surface home",
        "sustainable driveway front yard",
        "green driveway surface home",
        "low runoff driveway home",
        "porous driveway residential home",
        "environmental driveway home exterior",
    ],
    "contractor": [
        "driveway contractor residential home",
        "driveway project crew home",
        "professional driveway crew front",
        "licensed driveway contractor home",
        "residential driveway team front",
        "driveway site inspection home",
        "driveway contractor visit home",
        "driveway paving crew suburban",
    ],
    "general": [
        "residential driveway front yard",
        "suburban driveway home exterior",
        "modern driveway front home",
        "new driveway residential home",
        "front yard driveway home",
        "driveway curb appeal home",
        "american driveway suburban home",
        "clean driveway entrance home",
    ],
}


def infer_cluster(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["asphalt", "blacktop", "tar"]):
        return "asphalt"
    if any(k in t for k in ["gravel", "rural", "chip seal"]):
        return "gravel"
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


def enforce_keyword_rules(keyword: str, cluster: str) -> str:
    words = keyword.lower().split()
    if "driveway" not in words:
        words.insert(0, "driveway")

    if cluster.startswith("state") and not any(w in SCENE_WORDS for w in words):
        words.append("home")

    if len(words) < 3:
        words.extend(["residential", "home"])
    if len(words) > 5:
        words = words[:5]
    return " ".join(words)


def general_keyword_from_title(title: str) -> str:
    t = title.lower()
    mapping = [
        ("base", "driveway base layer residential"),
        ("subgrade", "driveway subgrade issue residential"),
        ("excavation", "driveway excavation site residential"),
        ("grading", "driveway grading slope residential"),
        ("thickness", "driveway thickness issue residential"),
        ("weight", "driveway load limit residential"),
        ("joint", "driveway control joints residential"),
        ("dimension", "driveway dimensions residential front"),
        ("curing", "driveway curing surface residential"),
        ("resurfacing", "driveway resurfacing issue residential"),
        ("replacement", "driveway replacement project residential"),
    ]
    for needle, keyword in mapping:
        if needle in t:
            return keyword
    return "driveway surface issue residential"


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
            search_keyword = f"{state_name.lower()} residential driveway home"
            cluster = "state-location"
        elif rel == "locations/index.html":
            search_keyword = "american home driveway exterior"
            cluster = "locations-hub"
        elif rel == "guides-hub/index.html":
            search_keyword = "driveway tools residential garage"
            cluster = "guides-hub"
        elif rel.startswith("guides/"):
            cluster = infer_cluster(clean_title)
            if cluster == "general":
                search_keyword = general_keyword_from_title(clean_title)
            else:
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

        search_keyword = enforce_keyword_rules(search_keyword, cluster)
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
