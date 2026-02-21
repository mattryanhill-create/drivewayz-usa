#!/usr/bin/env python3
"""
Generate SEO articles from content briefs using Moonshot's Kimi API.
Reads content_briefs.csv (column: Article Topic) and outputs full HTML pages to guides/

Dependencies: pip install openai python-dotenv

Usage:
  python generate_articles.py              # Process all briefs
  python generate_articles.py --start 37 --end 61   # Process briefs 37-61 only
"""

import argparse
import concurrent.futures
import csv
import html
import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Optional, List, Tuple

from dotenv import load_dotenv
from openai import OpenAI

# Config
PROJECT_ROOT = Path(__file__).resolve().parent
CSV_PATH = PROJECT_ROOT / "content_briefs.csv"
TEMPLATE_PATH = PROJECT_ROOT / "guides" / "basalt-driveway" / "index.html"
HERO_IMAGE_MAP_PATH = PROJECT_ROOT / "hero-image-map.json"  # Future hero image mapping input
OUTPUT_DIR = PROJECT_ROOT / "guides"
FAILED_JSON = PROJECT_ROOT / "failed.json"
API_BASE_URL = "https://api.moonshot.ai/v1"
MODEL = "kimi-k2-0905-preview"
DELAY_SECONDS = 0.5
BASE_URL = "https://drivewayzusa.co/"

# System prompt for Kimi API
SYSTEM_PROMPT = """You are an expert SEO content writer for Drivewayz USA, a driveway services company. Write detailed, helpful, original articles. Use H2 and H3 subheadings. Include practical advice homeowners can use. Write in a friendly, authoritative tone. Use short paragraphs. Include a FAQ section at the end with 3-4 common questions. Output only the article body HTML — no full page structure, just the content that goes inside the main article area."""

# Load env
load_dotenv()


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")[:80]


def derive_target_keyword(topic: str) -> str:
    """Derive a target keyword from the article title."""
    # Use the main phrase - before colon if present, else full title
    if ":" in topic:
        return topic.split(":")[0].strip()
    return topic


def build_user_prompt(topic: str) -> str:
    """Build the user prompt for article generation."""
    target_keyword = derive_target_keyword(topic)
    return f"""Write a comprehensive 1500-2000 word SEO article on: **{topic}**

Target keyword: {target_keyword}

The article should cover this topic in depth for homeowners interested in driveway services. Include:
- An engaging introduction
- Several H2 sections with H3 subsections
- Practical, actionable advice
- A FAQ section at the end with 3-4 relevant questions (wrap it in <section id="faq"> for anchor linking)
- Use class="faq-item" for each FAQ, with <button class="faq-q" onclick="toggleFaq(this)"> for the question and <div class="faq-a"> for the answer

Output only the HTML content for the main article body. Use semantic HTML: <section>, <h2>, <h3>, <p>, <ul>, <ol>, <li>. Add id attributes to main sections for table of contents linking (e.g., id="overview", id="costs", id="faq").
"""


def generate_article_body(client: OpenAI, topic: str) -> Optional[str]:
    """Call Kimi API to generate article body HTML. Returns HTML or None on failure."""
    user_prompt = build_user_prompt(topic)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content
    if not content:
        return None

    # Strip markdown code blocks if present
    content = content.strip()
    if content.startswith("```html"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    return content


def generate_meta_description(topic: str, max_length: int = 155) -> str:
    """Generate a meta description from the topic."""
    base = f"Learn about {topic.lower()}. Expert guide from Drivewayz USA."
    return base[:max_length] + ("..." if len(base) > max_length else "")


def extract_faq_qas(article_body: str) -> List[Tuple[str, str]]:
    """
    Extract (question, answer) pairs from the FAQ section of the HTML article body.
    Looks for <section id="faq"> with children of .faq-item.
    """
    faqs = []
    faq_section_match = re.search(
        r'<section[^>]*id=["\']faq["\'][^>]*>(.*?)</section>',
        article_body,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if faq_section_match:
        faq_html = faq_section_match.group(1)
        faq_items = re.findall(
            r'<div\s+class=["\']faq-item["\'][^>]*>(.*?)</div>',
            faq_html,
            flags=re.DOTALL | re.IGNORECASE,
        )
        for item_html in faq_items:
            # Extract question from <button class="faq-q" ...>?</button>
            q_match = re.search(
                r'<button\s+class=["\']faq-q["\'][^>]*>(.*?)</button>',
                item_html,
                flags=re.DOTALL | re.IGNORECASE,
            )
            # Extract answer from <div class="faq-a">...</div>
            a_match = re.search(
                r'<div\s+class=["\']faq-a["\'][^>]*>(.*?)</div>',
                item_html,
                flags=re.DOTALL | re.IGNORECASE,
            )
            if q_match and a_match:
                question = re.sub(r"\s+", " ", html.unescape(q_match.group(1).strip()))
                # Remove any html tags from answer text for schema
                answer_html = a_match.group(1).strip()
                answer = re.sub(r"<[^>]+>", "", answer_html)
                answer = re.sub(r"\s+", " ", html.unescape(answer.strip()))
                faqs.append((question, answer))
    return faqs


def build_faq_json_ld(qas: List[Tuple[str, str]], topic: str, url: str) -> str:
    """Build FAQPage JSON-LD schema script given Q&A list."""
    if not qas:
        return ""
    main_entity = []
    for q, a in qas:
        main_entity.append(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": a,
                },
            }
        )
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entity,
    }
    # No root-level "name" or "url" to keep compliant.
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(schema, ensure_ascii=False, indent=2)
        + "\n</script>"
    )


def build_page_from_template(
    template_html: str,
    topic: str,
    article_body: str,
) -> str:
    """Replace template placeholders with generated content (with FAQPage JSON-LD)."""
    meta_desc = generate_meta_description(topic)
    page_title = f"{topic} | Drivewayz USA Guides"
    subtitle = (
        f"A complete guide to {derive_target_keyword(topic).lower()} — "
        "what homeowners need to know."
    )

    result = template_html

    # Replace <title>
    result = re.sub(
        r"<title>.*?</title>",
        f"<title>{html.escape(page_title)}</title>",
        result,
        count=1,
        flags=re.DOTALL,
    )

    # Replace meta description
    result = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{html.escape(meta_desc)}">',
        result,
        count=1,
    )

    # Replace guide-hero h1
    result = re.sub(
        r"<h1>.*?</h1>",
        f"<h1>{html.escape(topic)}</h1>",
        result,
        count=1,
        flags=re.DOTALL,
    )

    # Replace guide-hero-subtitle
    result = re.sub(
        r'<p class="guide-hero-subtitle">.*?</p>',
        f'<p class="guide-hero-subtitle">{html.escape(subtitle)}</p>',
        result,
        count=1,
    )

    # Replace breadcrumb span (last segment)
    result = re.sub(
        r"(<a href=\"/guides-hub/\">Guides</a> / <span>)[^<]*(</span>)",
        rf"\g<1>{html.escape(topic)}\g<2>",
        result,
        count=1,
    )

    # Replace main content
    # We want to inject the FAQ JSON-LD after the FAQ section (if any).
    article_body_with_jsonld = article_body
    # Determine canonical URL for the FAQ page for possible use (not strictly needed here).
    slug = slugify(topic)
    page_url = BASE_URL + "guides/" + slug + "/"

    faq_qas = extract_faq_qas(article_body)
    faq_json_ld = build_faq_json_ld(faq_qas, topic, page_url)

    # If FAQ section exists, inject after </section> (where section id="faq")
    if faq_json_ld:
        def _inject_ld(match):
            section = match.group(0)
            # Add JSON-LD after FAQ </section>
            return section + "\n" + faq_json_ld

        # Try to find the FAQ section close tag
        article_body_with_jsonld, count = re.subn(
            r'(</section>\s*)(?!.*</section>)',  # Only the LAST </section>
            lambda m: _inject_ld(m),
            article_body_with_jsonld,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if count == 0:
            # If not found (FAQ section missing), append JSON-LD at end just in case
            article_body_with_jsonld += "\n" + faq_json_ld

    result = re.sub(
        r"(<main class=\"guide-main\">)\s*[\s\S]*?(\s*</main>)",
        rf"\g<1>\n\n    {article_body_with_jsonld}\g<2>",
        result,
        count=1,
    )

    return result


def process_single_row(
    client: OpenAI, template_html: str, row: dict, index: int
) -> dict:
    """Process one row: skip if file exists, else generate and save. Returns status dict."""
    topic = row.get("Article Topic", row.get("article_topic", "Untitled")).strip()
    if not topic:
        return {"status": "skipped", "topic": "", "error": None, "row": index + 1}

    slug = slugify(topic)
    output_dir = OUTPUT_DIR / slug
    filepath = output_dir / "index.html"

    if filepath.exists():
        return {"status": "skipped", "topic": topic, "error": None, "row": index + 1}

    try:
        article_body = generate_article_body(client, topic)
        time.sleep(DELAY_SECONDS)  # Per-thread delay to avoid rate limits

        if article_body:
            full_page = build_page_from_template(
                template_html, topic, article_body
            )
            output_dir.mkdir(parents=True, exist_ok=True)
            filepath.write_text(full_page, encoding="utf-8")
            return {"status": "success", "topic": topic, "error": None, "row": index + 1}
        else:
            return {
                "status": "failed",
                "topic": topic,
                "error": "Empty response",
                "row": index + 1,
            }
    except Exception as e:
        return {"status": "failed", "topic": topic, "error": str(e), "row": index + 1}


def main():
    parser = argparse.ArgumentParser(description="Generate SEO articles from content briefs")
    parser.add_argument("--start", type=int, help="First brief number (1-based)")
    parser.add_argument("--end", type=int, help="Last brief number (1-based)")
    args = parser.parse_args()

    api_key = os.environ.get("MOONSHOT_API_KEY")
    if not api_key:
        print("ERROR: MOONSHOT_API_KEY not found in .env")
        return 1

    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found")
        return 1

    if not TEMPLATE_PATH.exists():
        print(f"ERROR: Template {TEMPLATE_PATH} not found")
        return 1

    template_html = TEMPLATE_PATH.read_text(encoding="utf-8")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    client = OpenAI(api_key=api_key, base_url=API_BASE_URL)

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if "Article Topic" not in fieldnames:
        print("WARNING: CSV should have column 'Article Topic'")

    # Build list of (index, row) for rows with non-empty topic
    work_items = [
        (i, row)
        for i, row in enumerate(rows)
        if row.get("Article Topic", row.get("article_topic", "")).strip()
    ]

    # Filter by brief range if --start/--end provided (brief numbers are 1-based)
    if args.start is not None or args.end is not None:
        start = args.start or 1
        end = args.end or len(work_items)
        work_items = [(i, row) for i, row in work_items if start <= (i + 1) <= end]
        print(f"Processing briefs {start}–{end} ({len(work_items)} articles)")

    total = len(work_items)

    failed = []
    completed_count = 0
    skipped_count = 0
    print_lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(
                process_single_row, client, template_html, row, index
            ): (index, row)
            for index, row in work_items
        }

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            with print_lock:
                completed_count += 1
                if result["status"] == "success":
                    print(f"[{completed_count}/{total}] Generated: {result['topic']}")
                elif result["status"] == "skipped" and result["topic"]:
                    skipped_count += 1
                    print(f"[{completed_count}/{total}] Skipped: {result['topic']}")
                elif result["status"] == "failed":
                    failed.append(
                        {
                            "row": result["row"],
                            "topic": result["topic"],
                            "error": result["error"],
                        }
                    )
                    print(f"[{completed_count}/{total}] Failed: {result['topic']}")

    if failed:
        with open(FAILED_JSON, "w", encoding="utf-8") as f:
            json.dump(failed, f, indent=2)
        print(f"\n{len(failed)} failure(s) saved to {FAILED_JSON}")

    attempted = total - skipped_count
    print(f"\nDone. Generated {attempted - len(failed)}/{attempted} articles.")
    return 0 if not failed else 1


if __name__ == "__main__":
    exit(main())
