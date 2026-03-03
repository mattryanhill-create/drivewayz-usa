#!/usr/bin/env python3
"""
Process guides/*/index.html: add JSON-LD structured data and contextual internal links.
Safe, idempotent. Dry-run by default; use --apply to write changes.
"""
import argparse
import html.parser
import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Paths
GUIDES_DIR = Path(__file__).resolve().parent.parent / "guides"
SKIP_GUIDE = "gravel-pothole-repair"  # Has manually crafted structured data

# Publisher/author for structured data
PUBLISHER = {
    "@type": "Organization",
    "name": "Drivewayz USA",
    "logo": {
        "@type": "ImageObject",
        "url": "https://drivewayzusa.co/images/drivewayz-usa-logo.png",
    },
}
AUTHOR = {"@type": "Organization", "name": "Drivewayz USA"}

# State slug mapping (folder substring -> locations slug)
STATE_SLUGS = [
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi",
    "missouri", "montana", "nebraska", "nevada", "new-hampshire", "new-jersey",
    "new-mexico", "new-york", "north-carolina", "north-dakota", "ohio",
    "oklahoma", "oregon", "pennsylvania", "rhode-island", "south-carolina",
    "south-dakota", "tennessee", "texas", "utah", "vermont", "virginia",
    "washington", "west-virginia", "wisconsin", "wyoming", "washington-dc",
]
STATE_DISPLAY = {
    "new-york": "New York", "new-jersey": "New Jersey", "new-mexico": "New Mexico",
    "new-hampshire": "New Hampshire", "north-carolina": "North Carolina",
    "north-dakota": "North Dakota", "south-carolina": "South Carolina",
    "south-dakota": "South Dakota", "west-virginia": "West Virginia",
    "washington-dc": "Washington DC",
}

# Contextual link rules: (keyword_substring, href, link_text)
LINK_RULES = [
    ("asphalt", "/guides/concrete-vs-asphalt-vs-gravel/", "Compare driveway materials"),
    ("concrete", "/guides/concrete-vs-asphalt-vs-gravel/", "Compare driveway materials"),
    ("gravel", "/guides/gravel-pothole-repair/", "Gravel pothole repair guide"),
    ("cost", "/cost-calculator/", "Calculate your driveway cost"),
    ("pricing", "/cost-calculator/", "Calculate your driveway cost"),
    ("repair", "/for-homeowners/", "Homeowner repair resources"),
    ("fix", "/for-homeowners/", "Homeowner repair resources"),
    ("seal", "/guides/driveway-sealing-complete-guide/", "Complete sealing guide"),
    ("coat", "/guides/driveway-sealing-complete-guide/", "Complete sealing guide"),
    ("drain", "/guides/driveway-drainage-problems-causes-and-fixes/", "Drainage solutions guide"),
]


def _state_display(slug: str) -> str:
    """Convert slug like 'north-carolina' to 'North Carolina'."""
    if slug in STATE_DISPLAY:
        return STATE_DISPLAY[slug]
    return slug.replace("-", " ").title()


def find_state_in_folder(folder_name: str) -> Optional[str]:
    """Return locations slug if folder name contains a state, else None."""
    lower = folder_name.lower()
    # Prefer longer matches (e.g. north-carolina before carolina)
    for slug in sorted(STATE_SLUGS, key=len, reverse=True):
        if slug.replace("-", "") in lower.replace("-", ""):
            return slug
    return None


def get_contextual_links(folder_name: str, existing_hrefs: set, max_to_add: int = 3) -> List[Tuple[str, str]]:
    """
    Return list of (href, text) to add, max max_to_add, no duplicates.
    """
    if max_to_add <= 0:
        return []
    lower = folder_name.lower()
    new_links = []  # List[Tuple[str, str]]
    seen_hrefs = set(existing_hrefs)

    # State link (higher priority)
    state = find_state_in_folder(folder_name)
    if state:
        href = f"/locations/{state}/"
        if href not in seen_hrefs and len(new_links) < max_to_add:
            new_links.append((href, f"Driveway services in {_state_display(state)}"))
            seen_hrefs.add(href)

    # Keyword rules
    for kw, href, text in LINK_RULES:
        if len(new_links) >= max_to_add:
            break
        if kw in lower and href not in seen_hrefs:
            new_links.append((href, text))
            seen_hrefs.add(href)

    return new_links


def extract_headline(title: str) -> str:
    """Strip common suffixes from title."""
    for suffix in (" | Drivewayz USA Guide", " | Drivewayz USA Guides", " | Drivewayz USA"):
        if title.endswith(suffix):
            return title[: -len(suffix)].strip()
    return title.strip()


def extract_description(html: str) -> str:
    """Extract meta description content."""
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html, re.I)
    return m.group(1).strip() if m else ""


def extract_canonical(html: str) -> str:
    """Extract canonical URL."""
    m = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', html, re.I)
    return m.group(1).strip() if m else ""


class FAQParser(html.parser.HTMLParser):
    """Extract FAQ question/answer pairs from HTML."""

    def __init__(self):
        super().__init__()
        self.faqs: list[tuple[str, str]] = []
        self._in_faq_section = False
        self._in_faq_item = False
        self._current_q: str | None = None
        self._current_a_parts: list[str] = []
        self._capturing_a = False
        self._q_tags = ("button", "h3", "h4")
        self._in_q_tag: str | None = None
        self._in_a_container = False

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        cls = (attrs_d.get("class") or "").split()
        tid = attrs_d.get("id", "")

        if tid == "faq" or "faq" in cls:
            self._in_faq_section = True
        if "faq-item" in cls:
            self._in_faq_item = True
            self._current_q = None
            self._current_a_parts = []
            self._capturing_a = False
        if self._in_faq_item and tag in self._q_tags and "faq-q" in cls:
            self._in_q_tag = tag
        if self._in_faq_item and tag == "div" and "faq-a" in cls:
            self._in_a_container = True
            self._capturing_a = True
        if self._in_faq_section and not self._in_faq_item and tag in ("h3", "h4") and "faq" in " ".join(cls).lower():
            self._in_q_tag = tag

    def handle_endtag(self, tag):
        if self._in_faq_item and tag in self._q_tags and self._in_q_tag == tag:
            self._in_q_tag = None
        if self._in_faq_item and tag == "div" and self._in_a_container:
            self._in_a_container = False
            self._capturing_a = False
            if self._current_q and self._current_a_parts:
                a_text = " ".join(self._current_a_parts).strip()
                if a_text:
                    self.faqs.append((self._current_q, a_text))
            self._current_a_parts = []
        if tag == "div" and "faq-item" in (self._current_tag_classes or []):
            self._in_faq_item = False

    def handle_data(self, data):
        if self._in_q_tag and self._in_faq_item:
            if self._current_q is None:
                self._current_q = data.strip()
            else:
                self._current_q += " " + data.strip()
        if self._capturing_a and data.strip():
            self._current_a_parts.append(data.strip())

    def error(self, msg):
        pass


# Track tag for endtag
class FAQParserWithTag(FAQParser):
    def handle_starttag(self, tag, attrs):
        self._current_tag_classes = (dict(attrs).get("class") or "").split()
        super().handle_starttag(tag, attrs)


def parse_faqs(html_content: str) -> List[Tuple[str, str]]:
    """Parse FAQ items from HTML. Returns list of (question, answer)."""
    parser = FAQParserWithTag()
    parser._current_tag_classes = []
    try:
        parser.feed(html_content)
        return parser.faqs
    except Exception:
        return []


def parse_faqs_regex(html_content: str) -> List[Tuple[str, str]]:
    """
    Fallback regex-based FAQ parsing for faq-item structure:
    .faq-item with .faq-q (button) and .faq-a (div with p).
    """
    faqs = []
    # Match <div class="faq-item">...<button class="faq-q">Q</button>...<div class="faq-a">...A...</div>
    pattern = re.compile(
        r'<div\s+class="[^"]*faq-item[^"]*"[^>]*>'
        r'\s*<button[^>]*class="[^"]*faq-q[^"]*"[^>]*>([^<]+)</button>'
        r'.*?<div[^>]*class="[^"]*faq-a[^"]*"[^>]*>(.*?)</div>',
        re.DOTALL | re.IGNORECASE
    )
    for m in pattern.finditer(html_content):
        q = re.sub(r"\s+", " ", m.group(1)).strip()
        a_block = m.group(2)
        a_text = re.sub(r"<[^>]+>", " ", a_block)
        a_text = re.sub(r"\s+", " ", a_text).strip()
        if q and a_text:
            faqs.append((q, a_text))
    return faqs


def build_article_schema(title: str, description: str, canonical: str, folder_name: str) -> Dict:
    headline = extract_headline(title)
    image_url = f"https://drivewayzusa.co/images/hero-{folder_name}.webp"
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "description": description,
        "author": AUTHOR,
        "publisher": PUBLISHER,
        "datePublished": "2025-01-15",
        "dateModified": "2025-03-01",
        "image": image_url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
    }


def build_faq_schema(faqs: List[Tuple[str, str]]) -> Optional[Dict]:
    if not faqs:
        return None
    main_entity = []
    for q, a in faqs:
        main_entity.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        })
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entity,
    }


def build_json_ld_scripts(article: Dict, faq: Optional[Dict]) -> str:
    blocks = []
    blocks.append(f'<script type="application/ld+json">\n{json.dumps(article, indent=2)}\n</script>')
    if faq:
        blocks.append(f'<script type="application/ld+json">\n{json.dumps(faq, indent=2)}\n</script>')
    return "\n".join(blocks) + "\n"


def inject_structured_data(html: str, folder_name: str) -> Tuple[str, bool]:
    """
    Inject JSON-LD blocks immediately before the main.css link.
    Returns (modified_html, changed).
    """
    # Find insertion point: immediately before <link rel="stylesheet" href="/main.css
    pattern = re.compile(
        r'(\s*)(<link\s+rel="stylesheet"\s+href="/main\.css[^"]*">)',
        re.IGNORECASE,
    )
    m = pattern.search(html)
    if not m:
        return html, False

    indent = m.group(1)
    title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
    title = title_m.group(1).strip() if title_m else ""
    description = extract_description(html)
    canonical = extract_canonical(html)
    if not canonical:
        canonical = f"https://drivewayzusa.co/guides/{folder_name}/"

    article = build_article_schema(title, description, canonical, folder_name)
    faqs = parse_faqs_regex(html) or parse_faqs(html)
    faq_schema = build_faq_schema(faqs)

    ld_blocks = build_json_ld_scripts(article, faq_schema)
    insertion = indent + ld_blocks.strip().replace("\n", "\n" + indent) + "\n" + indent
    new_html = html[: m.start()] + insertion + m.group(2) + html[m.end() :]
    return new_html, True


def get_existing_nav_hrefs(html: str) -> set:
    """Extract hrefs from guide-internal-links nav."""
    hrefs = set()
    nav_match = re.search(
        r'<nav\s+class="guide-internal-links"[^>]*>.*?</nav>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if nav_match:
        nav_block = nav_match.group(0)
        for m in re.finditer(r'<a\s+href="([^"]*)"', nav_block):
            hrefs.add(m.group(1))
    return hrefs


def enhance_internal_links(html: str, folder_name: str) -> Tuple[str, bool]:
    """
    Add 2-3 contextual links to guide-internal-links nav. Cap at 4 total.
    Returns (modified_html, changed).
    """
    existing = get_existing_nav_hrefs(html)
    current_count = len(existing)
    max_to_add = min(3, 4 - current_count)
    if max_to_add <= 0:
        return html, False

    new_links = get_contextual_links(folder_name, existing, max_to_add)
    if not new_links:
        return html, False

    # Find the </ul> inside the nav and insert new <li> before it
    nav_pattern = re.compile(
        r'(<nav\s+class="guide-internal-links"[^>]*>\s*<ul[^>]*>)(.*?)(</ul>\s*</nav>)',
        re.DOTALL | re.IGNORECASE,
    )
    m = nav_pattern.search(html)
    if not m:
        return html, False

    prefix, inner, suffix = m.group(1), m.group(2), m.group(3)
    new_lis = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in new_links)
    new_inner = inner.rstrip() + "\n    " + new_lis + "\n  "
    new_nav = prefix + new_inner + suffix
    new_html = html[: m.start()] + new_nav + html[m.end() :]
    return new_html, True


def process_file(path: Path, apply: bool, stats: Dict) -> None:
    folder_name = path.parent.name
    if folder_name == SKIP_GUIDE:
        stats["skipped_gravel"] += 1
        print(f"  SKIP (gravel-pothole-repair): {path}")
        return

    content = path.read_text(encoding="utf-8")
    modified = False
    schema_added = False

    if "application/ld+json" in content:
        stats["skipped_has_schema"] += 1
        print(f"  SKIP (has schema): {path}")
    else:
        content, schema_added = inject_structured_data(content, folder_name)
        if schema_added:
            modified = True
            print(f"  MODIFY (add schema): {path}")

    content, link_changed = enhance_internal_links(content, folder_name)
    if link_changed:
        modified = True
        print(f"  MODIFY (add links): {path}")

    if modified:
        stats["modified"] += 1
        if apply:
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            path.write_text(content, encoding="utf-8")
            print(f"    -> Wrote (backup: {backup.name})")
        else:
            print(f"    -> Would write (dry-run)")


def main():
    ap = argparse.ArgumentParser(description="Add structured data and internal links to guides")
    ap.add_argument("--apply", action="store_true", help="Actually write changes (default: dry-run)")
    args = ap.parse_args()

    guides_dir = GUIDES_DIR
    if not guides_dir.is_dir():
        print(f"Guides directory not found: {guides_dir}")
        return 1

    index_files = sorted(guides_dir.glob("*/index.html"))
    stats = {
        "processed": 0,
        "modified": 0,
        "skipped_has_schema": 0,
        "skipped_gravel": 0,
        "errors": 0,
    }

    print("Dry-run mode (use --apply to write changes)" if not args.apply else "APPLY mode - writing changes")
    print("-" * 60)

    for path in index_files:
        stats["processed"] += 1
        try:
            process_file(path, args.apply, stats)
        except Exception as e:
            stats["errors"] += 1
            print(f"  ERROR: {path}: {e}")

    print("-" * 60)
    print("Summary:")
    print(f"  Files processed: {stats['processed']}")
    print(f"  Files modified: {stats['modified']}")
    print(f"  Skipped (already had schema): {stats['skipped_has_schema']}")
    print(f"  Skipped (gravel-pothole-repair): {stats['skipped_gravel']}")
    print(f"  Errors: {stats['errors']}")
    return 1 if stats["errors"] else 0


if __name__ == "__main__":
    exit(main())
