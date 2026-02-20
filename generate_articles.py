#!/usr/bin/env python3
"""
Generate SEO articles from content briefs using Moonshot's Kimi API.
Reads content_briefs.csv and outputs HTML articles to articles/ folder.

Dependencies: pip install openai python-dotenv
"""

import csv
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
ARTICLES_DIR = PROJECT_ROOT / "articles"
FAILED_JSON = PROJECT_ROOT / "failed.json"
API_BASE_URL = "https://api.moonshot.ai/v1"
MODEL = "kimi-k2-0905-preview"
DELAY_SECONDS = 2
WORD_COUNT_MIN = 1500
WORD_COUNT_MAX = 2000

# Load env
load_dotenv()


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")[:80]


def build_prompt(row: dict) -> str:
    """Build the system + user prompt for article generation."""
    topic = row.get("topic", "")
    target_keyword = row.get("target_keyword", "")
    brief = row.get("brief", "")

    return f"""You are an expert SEO content writer. Generate a high-quality, informative article with the following requirements:

**Topic:** {topic}
**Target Keyword:** {target_keyword}
**Content Brief:** {brief}

**Requirements:**
- Length: {WORD_COUNT_MIN}-{WORD_COUNT_MAX} words
- Output format: Clean HTML only (no markdown, no code blocks)
- Use semantic HTML: <h2> for main sections, <h3> for subsections, <p> for paragraphs, <ul>/<li> for lists
- Include the target keyword naturally in the title (use <h1>), intro, and throughout
- Write in a professional, helpful tone
- Ensure the content is original, accurate, and valuable for readers
- No XML declarations or <html>/<head>/<body> wrappers—just the article content as a fragment
"""


def generate_article(client: OpenAI, row: dict) -> Optional[str]:
    """Call Kimi API to generate article. Returns HTML or None on failure."""
    prompt = build_prompt(row)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert SEO content writer. Output only valid HTML, no markdown or explanations.",
            },
            {"role": "user", "content": prompt},
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


def main():
    api_key = os.environ.get("MOONSHOT_API_KEY")
    if not api_key:
        print("ERROR: MOONSHOT_API_KEY not found in .env")
        return 1

    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found")
        return 1

    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    client = OpenAI(api_key=api_key, base_url=API_BASE_URL)

    failed = []
    total = 0

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    for col in ("topic", "target_keyword", "brief"):
        if col not in fieldnames:
            print(f"WARNING: CSV may be missing column '{col}'")

    for i, row in enumerate(rows):
        total += 1
        topic = row.get("topic", "untitled")
        slug = slugify(topic)
        filename = f"{slug}.html"
        filepath = ARTICLES_DIR / filename

        print(f"[{i + 1}/{len(rows)}] Generating: {topic} -> {filename}")

        try:
            html = generate_article(client, row)
            if html:
                filepath.write_text(html, encoding="utf-8")
                print(f"  ✓ Saved to {filepath}")
            else:
                failed.append(
                    {"row": i + 1, "topic": topic, "error": "Empty response"}
                )
                print("  ✗ Empty response")
        except Exception as e:
            failed.append(
                {"row": i + 1, "topic": topic, "error": str(e)}
            )
            print(f"  ✗ Failed: {e}")

        if i < len(rows) - 1:
            time.sleep(DELAY_SECONDS)

    if failed:
        with open(FAILED_JSON, "w", encoding="utf-8") as f:
            json.dump(failed, f, indent=2)
        print(f"\n{len(failed)} failure(s) saved to {FAILED_JSON}")

    print(f"\nDone. Generated {total - len(failed)}/{total} articles.")
    return 0 if not failed else 1


if __name__ == "__main__":
    exit(main())
