#!/usr/bin/env python3
"""Extract FAQ Q&A from guide HTML and inject FAQPage JSON-LD when missing."""
import json
import re
import glob
import sys
from html import unescape


def extract_faq_pairs(text: str) -> list[tuple[str, str]]:
    section = re.search(r'<section[^>]*id="faq"[^>]*>(.*?)</section>', text, re.S | re.I)
    if not section:
        return []
    block = section.group(1)
    pairs = []
    for item in re.finditer(r'class="faq-item"[^>]*>(.*?)</div>\s*</div>', block, re.S):
        chunk = item.group(1)
        qm = re.search(r'class="faq-q"[^>]*>([^<]+)', chunk)
        am = re.search(r'class="faq-a"[^>]*>\s*(?:<p>)?([^<]+)', chunk, re.S)
        if not qm or not am:
            continue
        q = unescape(re.sub(r"\s+", " ", qm.group(1)).strip())
        a = unescape(re.sub(r"\s+", " ", am.group(1)).strip())
        if len(a) >= 50:
            pairs.append((q, a))
    return pairs


def build_faq_json(pairs: list[tuple[str, str]]) -> str:
    entities = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in pairs[:6]
    ]
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}
    return (
        '  <script type="application/ld+json">\n'
        + json.dumps(data, indent=2)
        + "\n  </script>\n"
    )


def process(path: str, dry_run: bool = False) -> str:
    text = open(path, encoding="utf-8").read()
    if "FAQPage" in text:
        return "has_faq"
    pairs = extract_faq_pairs(text)
    if len(pairs) < 3:
        return f"insufficient_pairs_{len(pairs)}"
    snippet = build_faq_json(pairs)
    # Insert after first Article ld+json block
    m = re.search(r'(</script>\s*)', text)
    if not m:
        return "no_script"
    # find end of first ld+json script
    first = re.search(r'(<script type="application/ld\+json">.*?</script>)', text, re.S)
    if not first:
        return "no_article"
    insert_at = first.end()
    new_text = text[:insert_at] + "\n" + snippet + text[insert_at:]
    if not dry_run:
        open(path, "w", encoding="utf-8").write(new_text)
    return f"updated_{len(pairs)}"


def main():
    dry_run = "--dry-run" in sys.argv
    targets = sys.argv[1:] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else [
        "guides/percolation-test-for-driveway-drainage-planning/index.html",
        "guides/driveway-basics-types-costs-lifespan/index.html",
        "guides/driveway-drainage-problems-causes-and-fixes/index.html",
        "guides/driveway-pros-and-cons-by-material-complete-breakdown/index.html",
        "guides/french-drain-installation-for-driveways/index.html",
    ]
    for path in targets:
        print(path, process(path, dry_run))


if __name__ == "__main__":
    main()
