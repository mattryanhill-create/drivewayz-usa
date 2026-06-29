#!/usr/bin/env python3
"""Find internal linking opportunities for high-impression guide pages."""
import csv
import re
import glob

TARGETS = {
    "/guides/gravel-pothole-repair/": [
        r"gravel pothole",
        r"pothole repair",
        r"fix potholes",
        r"potholes in gravel",
    ],
    "/guides/tar-and-chip-driveway-vs-asphalt-comparison/": [
        r"tar and chip",
        r"tar & chip",
        r"chip seal",
    ],
    "/guides/percolation-test-for-driveway-drainage-planning/": [
        r"percolation test",
        r"perc test",
    ],
    "/guides/asphalt-rejuvenator-products-review/": [
        r"asphalt rejuvenator",
        r"rejuvenator product",
    ],
    "/guides/resurfacing-vs-replacement/": [
        r"resurfacing vs replacement",
        r"resurface or replace",
    ],
    "/guides/concrete-vs-asphalt-driveway-the-ultimate-2026-comparison/": [
        r"concrete vs asphalt",
        r"asphalt vs concrete",
    ],
}


def slug_from_path(path: str) -> str:
    return path.replace("guides/", "").replace("/index.html", "")


def has_link(text: str, target: str) -> bool:
    return target in text or target.rstrip("/") + '"' in text


def find_matches(text: str, patterns: list[str]) -> list[tuple[str, str]]:
    # strip tags for sentence context
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = re.sub(r"\s+", " ", plain)
    hits = []
    for pat in patterns:
        for m in re.finditer(pat, plain, re.I):
            start = max(0, m.start() - 40)
            end = min(len(plain), m.end() + 80)
            snippet = plain[start:end].strip()
            anchor = m.group(0)
            hits.append((anchor, snippet))
            break  # one per pattern per page
    return hits


def main():
    rows = []
    for path in sorted(glob.glob("guides/*/index.html")):
        source = f"/guides/{slug_from_path(path)}/"
        text = open(path, encoding="utf-8").read()
        if source in TARGETS:
            continue
        for target, patterns in TARGETS.items():
            if has_link(text, target):
                continue
            for anchor, sentence in find_matches(text, patterns):
                words = sentence.split()[:15]
                rows.append(
                    {
                        "source_page": source,
                        "target_page": target,
                        "anchor_text": anchor,
                        "surrounding_sentence": " ".join(words),
                    }
                )
                break

    out = "reports/internal-linking-opportunities-2026-06.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["source_page", "target_page", "anchor_text", "surrounding_sentence"],
        )
        w.writeheader()
        w.writerows(rows[:100])  # cap for review
    print(f"Wrote {len(rows)} opportunities (showing top 100) to {out}")


if __name__ == "__main__":
    main()
