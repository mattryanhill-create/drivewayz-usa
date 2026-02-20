#!/usr/bin/env python3
"""
Generate SEO articles from content briefs using Moonshot's Kimi API.
Reads content_briefs.csv (column: Article Topic) and outputs full HTML pages to guides/

Dependencies: pip install openai python-dotenv
"""

import csv
import html
import json
import os
import re
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

# Config
PROJECT_ROOT = Path(__file__).resolve().parent
CSV_PATH = PROJECT_ROOT / "content_briefs.csv"
TEMPLATE_PATH = PROJECT_ROOT / "guides" / "basalt-driveway.html"
OUTPUT_DIR = PROJECT_ROOT / "guides"
FAILED_JSON = PROJECT_ROOT / "failed.json"
API_BASE_URL = "https://api.moonshot.ai/v1"
MODEL = "kimi-k2-0905-preview"
DELAY_SECONDS = 2

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


def build_page_from_template(
    template_html: str,
    topic: str,
    article_body: str,
) -> str:
    """Replace template placeholders with generated content."""
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
        flags=re.DOTALL,
    )

    # Replace breadcrumb span (last segment)
    result = re.sub(
        r"(<a href=\"../guides-hub.html\">Guides</a> / <span>)[^<]*(</span>)",
        rf"\g<1>{html.escape(topic)}\g<2>",
        result,
        count=1,
    )

    # Replace main content
    result = re.sub(
        r"(<main class=\"guide-main\">)\s*[\s\S]*?(\s*</main>)",
        rf"\g<1>\n\n    {article_body}\g<2>",
        result,
        count=1,
    )

    return result


def main():
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

    failed = []
    total = 0

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if "Article Topic" not in fieldnames:
        print("WARNING: CSV should have column 'Article Topic'")

    for i, row in enumerate(rows):
        topic = row.get("Article Topic", row.get("article_topic", "Untitled")).strip()
        if not topic:
            continue

        slug = slugify(topic)
        filename = f"{slug}.html"
        filepath = OUTPUT_DIR / filename

        if filepath.exists():
            print(f"[{i + 1}/{len(rows)}] Skipping existing: {topic} -> {filename}")
            continue

        total += 1
        print(f"[{i + 1}/{len(rows)}] Generating: {topic} -> {filename}")

        try:
            article_body = generate_article_body(client, topic)
            if article_body:
                full_page = build_page_from_template(
                    template_html, topic, article_body
                )
                filepath.write_text(full_page, encoding="utf-8")
                print(f"  ✓ Saved to {filepath}")
            else:
                failed.append(
                    {"row": i + 1, "topic": topic, "error": "Empty response"}
                )
                print("  ✗ Empty response")
        except Exception as e:
            failed.append({"row": i + 1, "topic": topic, "error": str(e)})
            print(f"  ✗ Failed: {e}")

        time.sleep(DELAY_SECONDS)

    if failed:
        with open(FAILED_JSON, "w", encoding="utf-8") as f:
            json.dump(failed, f, indent=2)
        print(f"\n{len(failed)} failure(s) saved to {FAILED_JSON}")

    print(f"\nDone. Generated {total - len(failed)}/{total} articles.")
    return 0 if not failed else 1


if __name__ == "__main__":
    exit(main())
