#!/usr/bin/env python3
"""Phase 1 — join hero_prep piles with Kimi render specs into render_manifest.csv."""

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROTECT = os.path.join(HERE, "DO_NOT_TOUCH.txt")
PILES = os.path.join(HERE, "pages_with_piles.csv")
KIMI = os.path.join(HERE, "job2_output_final.json")
OUT = os.path.join(HERE, "render_manifest.csv")

SITE = "https://drivewayzusa.co"
TARGET_PILES = ("A_REPLACE_PRIORITY", "B_REPLACE_BULK")

COLUMNS = [
    "url", "slug", "pile", "html_file", "working_filename", "render_prompt",
    "negative_prompt", "subject", "material", "setting", "condition",
    "lighting", "angle", "intended_alt_CONSTRAINT_NOT_FINAL", "render_status",
]

# render_prompt is not a field in job2_output_final.json; it is composed from
# the six structured attributes in this fixed order so it can be regenerated.
PROMPT_PARTS = ("subject", "material", "setting", "condition", "lighting", "angle")


def die(msg):
    print(f"\nHARD FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def load_protect_list(path):
    special, dir_prefixes, exact_files = [], [], []
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "/":
            special.append(line)
        elif line.endswith("/"):
            dir_prefixes.append(line)
        else:
            exact_files.append(line)
    return special, dir_prefixes, exact_files


def make_matcher(special, dir_prefixes, exact_files):
    def is_protected(url_path):
        """Returns the matched protect-list entry, or None."""
        if url_path in ("/", "/index.html") and "/" in special:
            return "/"
        for prefix in dir_prefixes:
            if url_path.startswith(prefix):
                return prefix
        for exact in exact_files:
            if url_path == exact:
                return exact
        return None
    return is_protected


def url_to_path(url):
    return url[len(SITE):] if url.startswith(SITE) else url


def slug_of(url_path):
    segments = [s for s in url_path.split("/") if s]
    return segments[-1] if segments else ""


def compose_prompt(rec):
    return ", ".join(v for v in (rec.get(p, "").strip() for p in PROMPT_PARTS) if v)


def main():
    for path in (PROTECT, PILES, KIMI):
        if not os.path.isfile(path):
            die(f"missing prereq {path}")

    special, dir_prefixes, exact_files = load_protect_list(PROTECT)
    is_protected = make_matcher(special, dir_prefixes, exact_files)
    print(f"protect-list: {len(special)} special, {len(dir_prefixes)} dir prefixes, "
          f"{len(exact_files)} exact files")

    with open(PILES, encoding="utf-8") as f:
        pile_rows = [r for r in csv.DictReader(f) if r["pile"] in TARGET_PILES]
    print(f"pile A/B rows: {len(pile_rows)}")
    if len(pile_rows) != 1009:
        die(f"expected 1,009 pile A/B rows, got {len(pile_rows)}")

    kimi = json.load(open(KIMI, encoding="utf-8"))
    by_url = {r["url"]: r for r in kimi}
    print(f"kimi records: {len(kimi)} ({len(by_url)} unique urls)")

    violations = []
    for r in pile_rows:
        entry = is_protected(url_to_path(r["url"]))
        if entry:
            violations.append((r["url"], r["pile"], entry))
    if violations:
        print("\nHARD FAIL: pile A/B pages matched the protect-list.", file=sys.stderr)
        print("The pipeline design guarantees this cannot happen — something is "
              "wrong upstream.\n", file=sys.stderr)
        for url, pile, entry in violations:
            print(f"  {pile}  {url}\n        matched entry: {entry}", file=sys.stderr)
        die(f"{len(violations)} protect-list violation(s)")
    print("protect-list violations: 0")

    unmatched = [r["url"] for r in pile_rows if r["url"] not in by_url]
    if unmatched:
        print(f"\nHARD FAIL: {len(unmatched)} pile A/B url(s) have no Kimi record:",
              file=sys.stderr)
        for u in unmatched[:10]:
            print(f"  {u}", file=sys.stderr)
        die("incomplete join")
    print("join coverage: 1009/1009")

    manifest = []
    for r in pile_rows:
        url_path = url_to_path(r["url"])
        slug = slug_of(url_path)
        k = by_url[r["url"]]
        manifest.append({
            "url": r["url"],
            "slug": slug,
            "pile": r["pile"],
            "html_file": f"guides/{slug}/index.html",
            "working_filename": k.get("intended_filename", ""),
            "render_prompt": compose_prompt(k),
            "negative_prompt": k.get("negative", ""),
            "subject": k.get("subject", ""),
            "material": k.get("material", ""),
            "setting": k.get("setting", ""),
            "condition": k.get("condition", ""),
            "lighting": k.get("lighting", ""),
            "angle": k.get("angle", ""),
            "intended_alt_CONSTRAINT_NOT_FINAL": k.get("intended_alt", ""),
            "render_status": "pending",
            "_impressions": float(r["gsc_impressions"] or 0),
        })

    pile_order = {"A_REPLACE_PRIORITY": 0, "B_REPLACE_BULK": 1}
    manifest.sort(key=lambda m: (pile_order[m["pile"]], -m["_impressions"]))

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for m in manifest:
            w.writerow({k: m[k] for k in COLUMNS})

    missing_html = sum(
        1 for m in manifest
        if not os.path.isfile(os.path.join(HERE, os.pardir, m["html_file"]))
    )
    a = sum(1 for m in manifest if m["pile"] == "A_REPLACE_PRIORITY")
    b = sum(1 for m in manifest if m["pile"] == "B_REPLACE_BULK")
    print(f"\nwrote {OUT}")
    print(f"  total rows: {len(manifest)}")
    print(f"  pile A: {a}    pile B: {b}    A+B: {a + b}")
    print(f"  html_file paths not found on disk: {missing_html}")


if __name__ == "__main__":
    main()
