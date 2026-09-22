#!/usr/bin/env python3
"""Rebalance the "Related Guides" blocks across the guide library.

Problem this solves: 736 guides carry a generated 3-link block that ignores
topic. 321 of them point at the same three pages, and other variants are just
the alphabetically-first guides. The result is that 683 of 1021 guides have
/guides-hub/ as their only inbound link while a handful of pages absorb
hundreds.

This script leaves the 265 hand-curated geo blocks (the ones carrying a
/locations/ link) untouched and regenerates only the generic blocks, choosing
topically-related targets under a global constraint that every guide ends up
with a floor of inbound links and no single page re-concentrates them.

Read-only unless --write is passed.
"""
from __future__ import annotations

import argparse
import collections
import html
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"

LINKS_PER_BLOCK = 6
MIN_LINKS_PER_BLOCK = 3
INBOUND_FLOOR = 4
INBOUND_CAP = 10

# Editing these is out of scope for content work; linking to them is fine.
PROTECTED = {
    "best-asphalt-driveway-sealer-top-products-for-2026",
    "pressure-washing-your-driveway-best-practices",
    "driveway-crack-filler-best-products-reviewed-for-2026",
    "best-concrete-driveway-sealer-penetrating-vs-film-forming",
}

STOP = set(
    """a an the for and or of to in on at by from with your you it is are was
    be can do does how what when why which that this these those not no vs
    into over under about after before more most best good complete practical
    guide guides complete- explained""".split()
)

# Generic modifiers. These are rare enough to earn a high IDF, which made
# "high-gloss" match "high water table" and "water-based" match "water main".
# They stay in the token set for tie-breaking but never make a pair eligible
# and contribute nothing to the score.
WEAK = set(
    """high low long short full light deep fast slow small large big top wide
    narrow thin thick new old real actual own per out off one two three four
    five more less same right left front back main side total average basic
    simple easy hard common general standard special custom modern classic
    natural clear dark bright soft hard-  option options type types kind way
    ways thing things part parts area areas level rate size amount number
    process step steps method methods technique techniques approach system
    systems much many matter matters need needs know knowing handle help make
    making take taking use using work working choose choosing consider
    consideration understanding difference start starting before after
    during better worse worth matter- factor factors tip tips""".split()
)

STATES = {
    "alabama","alaska","arizona","arkansas","california","colorado","connecticut",
    "delaware","florida","georgia","hawaii","idaho","illinois","indiana","iowa",
    "kansas","kentucky","louisiana","maine","maryland","massachusetts","michigan",
    "minnesota","mississippi","missouri","montana","nebraska","nevada","hampshire",
    "jersey","mexico","york","carolina","dakota","ohio","oklahoma","oregon",
    "pennsylvania","rhode","island","tennessee","texas","utah","vermont","virginia",
    "washington","wisconsin","wyoming","columbia","puerto","rico","guam",
}

MATERIAL = {
    "asphalt","concrete","gravel","paver","pavers","resin","cobblestone","chip",
    "seal","brick","stone","permeable","tarmac","shell","glass","dirt","grass",
    "crushed","limestone","bluestone","exposed","stamped","pervious",
}

INTENT = {
    "cost","costs","price","pricing","repair","repairs","crack","cracking",
    "pothole","potholes","install","installation","maintenance","maintain",
    "sealing","sealer","sealcoating","drainage","drain","permit","permits",
    "snow","winter","ice","freeze","diy","contractor","contractors","warranty",
    "lifespan","thickness","base","subgrade","resurfacing","overlay","cleaning",
    "clean","weeds","sand","joint","joints","slope","grading","excavation",
    "inspection","replacement","curb","apron","width","dimensions","lighting",
    "heated","edge","edges","staining","color","sample","samples","template",
}


def tokens(*parts: str) -> set[str]:
    text = " ".join(parts).lower()
    # Fold "X-based" compounds into one token. Otherwise "water-based sealer"
    # scores against drainage pages on a bare "water", and "solvent-based"
    # against solvent cleanup.
    text = re.sub(r"\b([a-z]+)[- ]based\b", r"\1based", text)
    raw = re.split(r"[^a-z0-9]+", text)
    out = set()
    for w in raw:
        if not w or w in STOP or len(w) < 3 or w.isdigit():
            continue
        out.add(w[:-1] if w.endswith("s") and len(w) > 4 else w)
    return out


def load_guides() -> dict:
    guides = {}
    for f in sorted(GUIDES.glob("*/index.html")):
        slug = f.parent.name
        t = f.read_text(encoding="utf-8", errors="ignore")
        h1m = re.search(r"<h1>([^<]*)</h1>", t)
        blk = re.search(r'<section class="related-guides">.*?</section>', t, re.S)
        links = (
            re.findall(r'<li><a href="([^"]+)">([^<]*)</a></li>', blk.group(0))
            if blk
            else []
        )
        guides[slug] = {
            "path": f,
            "h1": h1m.group(1) if h1m else slug.replace("-", " ").title(),
            "block": blk.group(0) if blk else None,
            "links": links,
            "geo": any(h.startswith("/locations/") for h, _ in links),
            "tok": tokens(slug.replace("-", " "), h1m.group(1) if h1m else ""),
        }
    return guides


GENERIC_TAIL = re.compile(
    r"^(a|an|the)\s+(complete|practical|simple|quick|full|ultimate|definitive|"
    r"smart|detailed|thorough|straightforward)\b.*$",
    re.I,
)


def encode(text: str) -> str:
    """Normalise entity encoding.

    Some existing anchors are double-encoded ("What&amp;#x27;s"), which renders
    the entity as literal text. Decode until stable, then re-encode only the
    characters that actually need it in element content.
    """
    prev = None
    while prev != text:
        prev = text
        text = html.unescape(text)
    return html.escape(text, quote=False)


def anchor_text(slug: str, guides: dict, canonical: dict) -> str:
    """Reuse the site's existing anchor for a target, else derive from its H1."""
    if slug in canonical:
        return encode(canonical[slug])
    h1 = guides[slug]["h1"]
    if ":" in h1:
        head, tail = h1.split(":", 1)
        if GENERIC_TAIL.match(tail.strip()) or len(h1) > 72:
            return encode(head.strip())
    if " - " in h1 and len(h1) > 72:
        return encode(h1.split(" - ", 1)[0].strip())
    return encode(h1)


MIN_SIM = 0.12


def similarity(a: dict, b: dict, idf: dict) -> float:
    ta, tb = a["tok"], b["tok"]
    inter = (ta & tb) - WEAK
    if not inter:
        return 0.0
    num = sum(idf.get(w, 0.0) ** 2 for w in inter)
    na = math.sqrt(sum(idf.get(w, 0.0) ** 2 for w in ta - WEAK))
    nb = math.sqrt(sum(idf.get(w, 0.0) ** 2 for w in tb - WEAK))
    if not na or not nb:
        return 0.0
    score = num / (na * nb)
    if inter & STATES:
        score += 0.55
    score += min(0.30, 0.15 * len(inter & MATERIAL))
    score += min(0.30, 0.10 * len(inter & INTENT))
    return score


def build(guides: dict) -> tuple[dict, dict]:
    n = len(guides)
    df = collections.Counter()
    for g in guides.values():
        df.update(g["tok"])
    idf = {w: math.log(n / c) for w, c in df.items()}

    canonical = {}
    for g in guides.values():
        for href, txt in g["links"]:
            m = re.match(r"/guides/([^/]+)/$", href)
            if m and txt.strip():
                canonical[m.group(1)] = txt.strip()

    slugs = list(guides)
    sources = [
        s
        for s in slugs
        if guides[s]["block"] and not guides[s]["geo"] and s not in PROTECTED
    ]

    # Inbound we are keeping: curated geo blocks stay exactly as they are.
    inbound = collections.Counter()
    for s in slugs:
        if guides[s]["geo"] or not guides[s]["block"]:
            for href, _ in guides[s]["links"]:
                m = re.match(r"/guides/([^/]+)/$", href)
                if m and m.group(1) in guides:
                    inbound[m.group(1)] += 1

    # Most curated geo pages already receive 4-6 inbound links from their state
    # siblings, and they make poor topical matches for non-geo guides (a
    # tack-coat page does not want "Asphalt Driveway Cost in Arizona"). Exclude
    # those - but only the ones that are genuinely already covered. Some geo
    # pages carry a /locations/ link without belonging to a reciprocal cluster,
    # and those still need inbound links.
    eligible = [
        t
        for t in slugs
        if not (guides[t]["geo"] and inbound[t] >= INBOUND_FLOOR)
    ]

    cand = {}
    backup = {}
    for s in sources:
        scored = [
            (similarity(guides[s], guides[t], idf), t) for t in eligible if t != s
        ]
        scored.sort(key=lambda x: (-x[0], x[1]))
        cand[s] = [t for sc, t in scored[:60] if sc >= MIN_SIM]
        # Ranked but below threshold; used only to avoid emitting a short block.
        backup[s] = [t for sc, t in scored[:60] if sc < MIN_SIM]

    assigned = {s: [] for s in sources}

    # Phase A - coverage. Give every under-floor target its most similar
    # sources first, so nothing is left dependent on guides-hub alone.
    need = sorted(
        (t for t in eligible if inbound[t] < INBOUND_FLOOR),
        key=lambda t: (inbound[t], t),
    )
    rev = collections.defaultdict(list)
    for s in sources:
        for rank, t in enumerate(cand[s]):
            rev[t].append((rank, s))
    for t in need:
        for _, s in sorted(rev[t]):
            if inbound[t] >= INBOUND_FLOOR:
                break
            if len(assigned[s]) < LINKS_PER_BLOCK and t not in assigned[s]:
                assigned[s].append(t)
                inbound[t] += 1

    # Phase B - relevance fill for leftover slots, respecting the cap.
    for s in sources:
        for t in cand[s]:
            if len(assigned[s]) >= LINKS_PER_BLOCK:
                break
            if t in assigned[s] or inbound[t] >= INBOUND_CAP:
                continue
            assigned[s].append(t)
            inbound[t] += 1
        # Graded fallback, so a thin-topic page never ends up with a stub
        # block: first relax the inbound cap, then the similarity threshold.
        for pool in (cand[s], backup[s]):
            for t in pool:
                if len(assigned[s]) >= MIN_LINKS_PER_BLOCK:
                    break
                if t not in assigned[s]:
                    assigned[s].append(t)
                    inbound[t] += 1

    # Repair pass. A handful of pages are so topically isolated that they land
    # in nobody's candidate list. Place them by displacing the weakest link on
    # their best-matching source, provided that link's target stays above the
    # floor.
    stranded = [t for t in eligible if inbound[t] == 0]
    for t in stranded:
        ranked = sorted(
            (
                (similarity(guides[s], guides[t], idf), s)
                for s in sources
                if s != t
            ),
            key=lambda x: (-x[0], x[1]),
        )
        for _, s in ranked[:25]:
            if inbound[t] > 0:
                break
            if t in assigned[s]:
                continue
            if len(assigned[s]) < LINKS_PER_BLOCK:
                assigned[s].append(t)
                inbound[t] += 1
                break
            drop = min(
                (x for x in assigned[s] if inbound[x] > INBOUND_FLOOR),
                key=lambda x: inbound[x] * -1,
                default=None,
            )
            if drop is not None:
                assigned[s][assigned[s].index(drop)] = t
                inbound[drop] -= 1
                inbound[t] += 1
                break

    # Order each block most-similar-first for a sensible reading order.
    for s in sources:
        assigned[s].sort(key=lambda t: -similarity(guides[s], guides[t], idf))
    return assigned, canonical


def render_block(old: str, targets: list[str], guides: dict, canonical: dict) -> str:
    """Rebuild the <li> list, preserving the block's exact surrounding markup."""
    items = "".join(
        f'<li><a href="/guides/{t}/">{anchor_text(t, guides, canonical)}</a></li>'
        for t in targets
    )
    m = re.search(r"(<ul>)(.*?)(</ul>)", old, re.S)
    if not m:
        raise SystemExit("block has no <ul>")
    # Reuse the whitespace pattern already used between the existing items.
    lis = re.findall(r"(\s*)<li>", m.group(2))
    sep = lis[0] if lis else "\n"
    tail = re.search(r"</li>(\s*)</ul>", old, re.S)
    inner = "".join(
        f"{sep}<li>"
        f'<a href="/guides/{t}/">{anchor_text(t, guides, canonical)}</a></li>'
        for t in targets
    ) + (tail.group(1) if tail else "\n")
    return old[: m.start(2)] + inner + old[m.end(2) :]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--sample", type=int, default=6)
    args = ap.parse_args()

    guides = load_guides()
    assigned, canonical = build(guides)

    # ---- reporting -------------------------------------------------------
    inbound = collections.Counter()
    for s, g in guides.items():
        if g["geo"] or not g["block"]:
            for href, _ in g["links"]:
                m = re.match(r"/guides/([^/]+)/$", href)
                if m and m.group(1) in guides:
                    inbound[m.group(1)] += 1
    for s, ts in assigned.items():
        for t in ts:
            inbound[t] += 1

    before = collections.Counter()
    for s, g in guides.items():
        for href, _ in g["links"]:
            m = re.match(r"/guides/([^/]+)/$", href)
            if m and m.group(1) in guides:
                before[m.group(1)] += 1

    n = len(guides)
    print(f"guides={n}  blocks rewritten={len(assigned)}")
    print(f"  protected skipped: {sorted(PROTECTED & set(guides))}")
    print("\ninbound links per guide (from Related Guides blocks):")
    for label, c in (("before", before), ("after", inbound)):
        zero = sum(1 for t in guides if c[t] == 0)
        lo = sum(1 for t in guides if c[t] < INBOUND_FLOOR)
        top = c.most_common(3)
        print(
            f"  {label:6} covered={n - zero:4}/{n}  zero={zero:4}  "
            f"under{INBOUND_FLOOR}={lo:4}  max={top[0][1]:3}  total={sum(c.values())}"
        )
        print(f"         most-linked: {top}")

    if args.sample:
        print("\n--- sample rewritten blocks ---")
        picks = [s for s in list(assigned)[:: max(1, len(assigned) // args.sample)]]
        for s in picks[: args.sample]:
            print(f"\n  {s}")
            print(f"    was: {[re.sub(r'^/guides/|/$','',h) for h,_ in guides[s]['links']]}")
            for t in assigned[s]:
                print(f"    ->  {anchor_text(t, guides, canonical)}  [{t}]")

    if not args.write:
        print("\n(dry run - pass --write to apply)")
        return

    changed = 0
    for s, ts in assigned.items():
        g = guides[s]
        new_block = render_block(g["block"], ts, guides, canonical)
        t = g["path"].read_text(encoding="utf-8")
        if g["block"] not in t:
            raise SystemExit(f"{s}: block not found for replacement")
        out = t.replace(g["block"], new_block, 1)
        # Nothing outside the block may move.
        if len(out) - len(t) != len(new_block) - len(g["block"]):
            raise SystemExit(f"{s}: unexpected edit outside block")
        g["path"].write_text(out, encoding="utf-8")
        changed += 1
    print(f"\nwrote {changed} files")


if __name__ == "__main__":
    main()
