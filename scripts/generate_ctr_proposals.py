#!/usr/bin/env python3
"""Generate CTR rewrite proposals for P1 zero-click pages (Initiative 2)."""
import csv
import re

P1 = [
    "/guides/gravel-pothole-repair/",
    "/guides/tar-and-chip-driveway-vs-asphalt-comparison/",
    "/guides/percolation-test-for-driveway-drainage-planning/",
    "/guides/asphalt-rejuvenator-products-review/",
]

CTA = " Get a free estimate."


def path_to_file(url: str) -> str:
    slug = url.strip("/").replace("guides/", "")
    return f"guides/{slug}/index.html"


def extract(path: str) -> dict:
    text = open(path, encoding="utf-8").read()
    title_m = re.search(r"<title>([^<]+)</title>", text, re.I)
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', text, re.I)
    h1_m = re.search(r"<h1[^>]*>([^<]+)", text, re.I)
    sub_m = re.search(r'class="guide-hero-subtitle"[^>]*>([^<]+)', text, re.I)
    body_m = re.search(r"<section[^>]*>\s*<p>([^<]+)", text, re.S)
    return {
        "title": title_m.group(1).strip() if title_m else "",
        "description": desc_m.group(1).strip() if desc_m else "",
        "h1": h1_m.group(1).strip() if h1_m else "",
        "intro": (sub_m.group(1).strip() if sub_m else (body_m.group(1).strip() if body_m else ""))[:200],
    }


def propose_title(h1: str, url: str) -> str:
    # 60 chars max, no pipe — lead with keyword
    slug = url.split("/")[-2].replace("-", " ")
    if "gravel pothole" in slug or "pothole" in slug:
        t = "Fix Gravel Driveway Potholes: Step-by-Step Guide"
    elif "tar-and-chip" in url:
        t = "Tar and Chip vs Asphalt Driveways: Cost & Durability"
    elif "percolation" in url:
        t = "Percolation Test for Driveway Drainage Planning"
    elif "rejuvenator" in url:
        t = "Best Asphalt Rejuvenator Products Reviewed (2026)"
    else:
        t = h1[:60]
    return t[:60]


def propose_desc(intro: str, h1: str) -> str:
    base = intro or h1
    base = re.sub(r"\s+", " ", base).strip()
    if len(base) > 120:
        base = base[:117].rsplit(" ", 1)[0] + "..."
    desc = base
    if not desc.endswith("."):
        desc += "."
    desc += CTA
    if len(desc) > 155:
        desc = desc[:152].rsplit(" ", 1)[0] + "..." + CTA
    return desc[:155]


def main():
    rows = []
    for url in P1:
        path = path_to_file(url)
        cur = extract(path)
        prop_title = propose_title(cur["h1"], url)
        prop_desc = propose_desc(cur["intro"], cur["h1"])
        rows.append(
            {
                "url": f"https://drivewayzusa.co{url}",
                "current_title": cur["title"],
                "proposed_title": prop_title,
                "title_chars": len(prop_title),
                "current_description": cur["description"],
                "proposed_description": prop_desc,
                "desc_chars": len(prop_desc),
            }
        )
    out = "reports/ctr-rewrite-p1-2026-06.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out}")
    for r in rows:
        print(f"\n{r['url']}")
        print(f"  Title ({r['title_chars']}): {r['proposed_title']}")
        print(f"  Desc  ({r['desc_chars']}): {r['proposed_description']}")


if __name__ == "__main__":
    main()
