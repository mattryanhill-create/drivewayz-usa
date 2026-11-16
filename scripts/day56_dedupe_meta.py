#!/usr/bin/env python3
"""Rewrite duplicate meta descriptions on 24 REWRITE pages.

Source: Lumar crawl 7831445, report pages_with_duplicate_descriptions
(24 pages, each sharing a description with one primary page). The primary
keeps its description; the 24 duplicates get the unique copy below.
Unlike day52, these pages carry og:description and (mostly)
twitter:description, so all three tags are rewritten, plus the Article
schema "description" when it exactly mirrors the old meta.

Usage: day56_dedupe_meta.py check | apply all | apply <slug> [<slug> ...]
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# slug -> new description (150-160 chars, Drivewayz USA exactly once)
NEW = {
    "guides/concrete-vs-asphalt-vs-gravel-which-driveway-is-best-for-your-home":
        "Concrete vs asphalt vs gravel driveways compared: up-front price, installation speed, lifespan & upkeep so you can pick the right surface. Drivewayz USA.",
    "guides/concrete-driveway-crack-repair-causes-and-solutions":
        "Concrete driveway crack repair: why slabs crack, how to inspect & classify cracks, step-by-step DIY fixes & when a crack needs a pro instead. Drivewayz USA.",
    "guides/eco-friendly-driveway-options-pros-cons-and-costs":
        "Eco-friendly driveway options compared: permeable pavers, porous asphalt, resin-bound aggregate & more, with honest pros, cons & real costs. Drivewayz USA.",
    "guides/when-to-hire-a-professional-for-driveway-repairs":
        "When to hire a pro for driveway repairs: warning signs that can't wait, what DIY kits can and can't fix & typical professional repair costs. Drivewayz USA.",
    "guides/driveway-demolition-permit-removing-existing-pavement":
        "Driveway demolition permits explained: when you need one, prep steps that speed approval, how to apply & what to expect when removing pavement. Drivewayz USA.",
    "guides/labor-shortage-impact-on-driveway-installation-costs":
        "How the labor shortage is raising driveway installation costs: where the extra dollars go, regional differences & ways to save on your project. Drivewayz USA.",
    "guides/how-to-fix-a-driveway-that-slopes-toward-your-house":
        "Driveway sloping toward your house? Diagnose the problem, try quick water-deflection fixes & compare mudjacking, regrading & replacement costs. Drivewayz USA.",
    "guides/driveway-cape-seal-combined-chip-and-slurry-treatment":
        "Driveway cape seal explained: how the two-step chip seal and slurry process works, key benefits, expected lifespan & typical project costs. Drivewayz USA.",
    "guides/driveway-weight-limits":
        "Driveway weight limits by material: how much load concrete, asphalt & pavers can handle, plus tips for parking RVs, trucks & heavy equipment. Drivewayz USA.",
    "guides/bonded-vs-unbonded-driveway-contractors-whats-the-difference":
        "Bonded vs unbonded driveway contractors: what a surety bond covers, the risks of hiring an unbonded crew & how to verify a bond in two minutes. Drivewayz USA.",
    "guides/driveway-material-price-forecast-2026-and-beyond":
        "Driveway material price forecast for 2026 and beyond: projected costs by material, market trends moving prices & when to sign your contract. Drivewayz USA.",
    "guides/driveway-grade-and-slope-regulations":
        "Driveway grade and slope regulations: typical code limits across the U.S., why the right grade matters & how to measure your driveway's slope. Drivewayz USA.",
    "guides/driveway-edge-crumbling-causes-and-repair-solutions":
        "Driveway edge crumbling: top causes, a 5-minute severity check, repair options for concrete & asphalt edges & how to stop it from coming back. Drivewayz USA.",
    "guides/best-driveway-material-for-west-virginia-homes":
        "Best driveway material for West Virginia homes: how freeze-thaw cycles, clay soils & steep rural lots shape the choice, compared side by side. Drivewayz USA.",
    "guides/driveway-contractor-website-must-haves-winning-online":
        "Driveway contractor website must-haves: mobile-first design, local SEO signals, project portfolios & trust features that win more jobs online. Drivewayz USA.",
    "guides/how-to-remove-ice-from-your-driveway-safely":
        "How to remove ice from your driveway safely: prep before storms, snow clearing tactics & de-icers that melt ice without damaging the surface. Drivewayz USA.",
    "guides/extending-a-driveway-planning-and-costs":
        "Extending a driveway: step-by-step planning checklist, permit and setback rules & real-world extension costs by material, size and layout. Drivewayz USA.",
    "guides/driveway-contractor-scheduling-app-coordinating-crews":
        "Driveway contractor scheduling apps: how crew coordination affects your timeline and cost, key app features & questions to ask your contractor. Drivewayz USA.",
    "guides/best-concrete-driveway-sealer-penetrating-vs-film-forming":
        "Best concrete driveway sealer: penetrating vs film-forming sealers compared on protection, appearance, lifespan & cost to pick the right one. Drivewayz USA.",
    "guides/how-google-reviews-impact-driveway-contractor-business":
        "How Google reviews impact driveway contractors: trust signals to look for, how the local algorithm uses reviews & red flags in review profiles. Drivewayz USA.",
    "guides/driveway-subcontractor-vs-general-contractor-who-to-hire":
        "Driveway subcontractor vs general contractor: what each pro does, when hiring a sub directly saves money & when a GC is the smarter call. Drivewayz USA.",
    "guides/heated-driveway-systems-cost-vs-benefit-analysis":
        "Heated driveway systems cost vs benefit: hydronic vs electric options, installation and operating costs & whether snow-melt systems pay off. Drivewayz USA.",
    "guides/driveway-surface-course-vs-base-course-understanding-layers":
        "Driveway surface course vs base course: what each layer does, materials, thickness & how the layers work together for a longer-lasting drive. Drivewayz USA.",
    "guides/asphalt-vs-concrete-in-hot-climates-heat-and-uv-resistance":
        "Asphalt vs concrete in hot climates: how heat and UV affect each surface, expected lifespan in sunny regions & up-front vs lifetime costs. Drivewayz USA.",
}

META_RE = re.compile(r'(<meta name="description" content=")([^"]*)(")')
SOCIAL_RES = (
    re.compile(r'(<meta property="og:description" content=")([^"]*)(")'),
    re.compile(r'(<meta name="twitter:description" content=")([^"]*)(")'),
)


def site_descriptions(exclude_slugs):
    """All current meta descriptions across the whole site."""
    descs = {}
    for f in list(ROOT.glob("guides/*/index.html")) + list(ROOT.glob("locations/*/index.html")) + [
            ROOT / "for-homeowners/index.html", ROOT / "for-contractors/index.html",
            ROOT / "index.html"]:
        slug = str(f.parent.relative_to(ROOT))
        if slug in exclude_slugs:
            continue
        m = META_RE.search(f.read_text(encoding="utf-8"))
        if m:
            descs.setdefault(html.unescape(m.group(2)), []).append(slug)
    return descs


def check():
    ok = True
    others = site_descriptions(set(NEW))
    seen = {}
    for slug, desc in NEW.items():
        errs = []
        n = len(desc)
        if not (150 <= n <= 160):
            errs.append(f"length {n}")
        if desc.count("Drivewayz USA") != 1:
            errs.append("brand count != 1")
        if desc in others:
            errs.append(f"duplicates existing page {others[desc][0]}")
        if desc in seen:
            errs.append(f"duplicates new desc for {seen[desc]}")
        if not (ROOT / slug / "index.html").exists():
            errs.append("page missing")
        seen[desc] = slug
        if errs:
            ok = False
            print(f"FAIL {slug}: {'; '.join(errs)}")
        else:
            print(f"ok   ({n}) {slug}")
    print("ALL CHECKS PASS" if ok else "CHECKS FAILED")
    return ok


def apply(slugs):
    for slug in slugs:
        desc = NEW[slug]
        path = ROOT / slug / "index.html"
        content = path.read_text(encoding="utf-8")
        old = html.unescape(META_RE.search(content).group(2))
        sub = lambda mm: mm.group(1) + html.escape(desc, quote=True) + mm.group(3)
        content, n = META_RE.subn(sub, content, count=1)
        assert n == 1, slug
        social = 0
        for rx in SOCIAL_RES:
            m = rx.search(content)
            if m and html.unescape(m.group(2)) == old:
                content = rx.sub(sub, content, count=1)
                social += 1
        # sync Article schema description if it mirrored the old meta
        synced = False
        for ascii_mode in (True, False):
            pat = f'"description": {json.dumps(old, ensure_ascii=ascii_mode)}'
            if pat in content:
                content = content.replace(pat, f'"description": {json.dumps(desc)}', 1)
                synced = True
                break
        path.write_text(content, encoding="utf-8")
        text = path.read_text(encoding="utf-8")
        for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
            json.loads(blk)
        print(f"OK ({len(desc)} chars, social={social}, schema-sync={synced}) {slug}")


if __name__ == "__main__":
    if sys.argv[1] == "check":
        sys.exit(0 if check() else 1)
    apply(list(NEW) if sys.argv[2:] == ["all"] else sys.argv[2:])
