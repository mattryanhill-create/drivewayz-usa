#!/usr/bin/env python3
"""Audit FAQPage JSON-LD coverage across /guides/* pages."""
import csv
import json
import re
import glob


def parse_faq_blocks(text: str) -> list[dict]:
    blocks = []
    for m in re.finditer(
        r'<script\s+type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        text,
        re.S,
    ):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if data.get("@type") == "FAQPage":
            blocks.append(data)
    return blocks


def count_valid_pairs(block: dict) -> int:
    entities = block.get("mainEntity") or []
    valid = 0
    for q in entities:
        if q.get("@type") != "Question":
            continue
        ans = (q.get("acceptedAnswer") or {}).get("text", "")
        if len(ans) >= 50:
            valid += 1
    return valid


def slug_to_url(path: str) -> str:
    slug = path.replace("guides/", "").replace("/index.html", "")
    return f"https://drivewayzusa.co/guides/{slug}/"


def main():
    priority_slugs = {
        "gravel-pothole-repair",
        "tar-and-chip-driveway-vs-asphalt-comparison",
        "percolation-test-for-driveway-drainage-planning",
        "asphalt-rejuvenator-products-review",
    }

    rows = []
    for path in sorted(glob.glob("guides/*/index.html")):
        text = open(path, encoding="utf-8").read()
        url = slug_to_url(path)
        faq_blocks = parse_faq_blocks(text)
        if faq_blocks:
            pair_count = max(count_valid_pairs(b) for b in faq_blocks)
            has_faq = "yes" if pair_count >= 3 else "partial"
            notes = f"{len(faq_blocks)} FAQPage block(s)"
        else:
            pair_count = 0
            has_faq = "no"
            # note if page has visible FAQ section
            notes = "has_faq_section" if 'id="faq"' in text or "class=\"faq-q\"" in text else ""

        slug = path.split("/")[1]
        rows.append(
            {
                "url": url,
                "has_faq": has_faq,
                "faq_pair_count": pair_count,
                "notes": notes,
                "priority": "P1" if slug in priority_slugs else "",
            }
        )

    out = "reports/faq-schema-audit-2026-06.csv"
    rows.sort(key=lambda r: (r["priority"] != "P1", r["has_faq"], r["url"]))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["url", "has_faq", "faq_pair_count", "notes", "priority"])
        w.writeheader()
        w.writerows(rows)

    yes = sum(1 for r in rows if r["has_faq"] == "yes")
    partial = sum(1 for r in rows if r["has_faq"] == "partial")
    no = sum(1 for r in rows if r["has_faq"] == "no")
    section_no_schema = sum(1 for r in rows if r["has_faq"] == "no" and "has_faq_section" in r["notes"])
    print(f"Wrote {out}")
    print(f"Total guides: {len(rows)}")
    print(f"has_faq=yes (3+ valid pairs): {yes}")
    print(f"has_faq=partial: {partial}")
    print(f"has_faq=no: {no}")
    print(f"no schema but FAQ section in HTML: {section_no_schema}")


if __name__ == "__main__":
    main()
