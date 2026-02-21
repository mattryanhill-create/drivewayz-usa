#!/usr/bin/env python3
"""
Download hero images from Pexels and inject them into gradient-only pages.

NOTE: This script is ready to run once PEXELS_API_KEY is provided in .env.
"""

from __future__ import annotations

import io
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
MAP_PATH = ROOT / "hero-image-map.json"
IMAGES_DIR = ROOT / "images"
PEXELS_ENDPOINT = "https://api.pexels.com/v1/search"
API_DELAY_SECONDS = 2
MIN_WIDTH = 1280
MIN_HEIGHT = 720


def load_env_key() -> str:
    env_path = ROOT / ".env"
    if not env_path.exists():
        raise RuntimeError(".env not found. Add PEXELS_API_KEY=... first.")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("PEXELS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("PEXELS_API_KEY not found in .env")


def slug_for_page(page_rel: str) -> str:
    path = Path(page_rel)
    if page_rel == "locations/index.html":
        return "locations-hub"
    if page_rel == "guides-hub/index.html":
        return "guides-hub"
    if path.name == "index.html" and len(path.parts) >= 2:
        return path.parts[-2]
    return path.stem


def pexels_search(api_key: str, query: str) -> dict:
    params = {
        "query": query,
        "orientation": "landscape",
        "per_page": 10,
        "page": 1,
        "size": "large",
    }
    req = Request(f"{PEXELS_ENDPOINT}?{urlencode(params)}")
    req.add_header("Authorization", api_key)
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pick_photo(result: dict) -> dict:
    photos = result.get("photos", [])
    for photo in photos:
        width = int(photo.get("width", 0))
        height = int(photo.get("height", 0))
        if width >= MIN_WIDTH and height >= MIN_HEIGHT and photo.get("src", {}).get("large2x"):
            return photo
    if photos:
        return photos[0]
    raise RuntimeError("No photos returned from Pexels")


def download_bytes(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "drivewayz-usa-hero-pipeline/1.0"})
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def save_webp(raw: bytes, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Pillow first, fallback to cwebp if Pillow unavailable.
    try:
        from PIL import Image  # type: ignore

        with Image.open(io.BytesIO(raw)) as img:
            img.convert("RGB").save(out_path, format="WEBP", quality=82, method=6)
        return
    except Exception:
        pass

    temp_in = out_path.with_suffix(".tmp.bin")
    temp_in.write_bytes(raw)
    try:
        subprocess.run(
            ["cwebp", "-q", "82", str(temp_in), "-o", str(out_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    finally:
        if temp_in.exists():
            temp_in.unlink()


def ensure_bg_size_position(block: str) -> str:
    if "background-size" not in block:
        block += "background-size:cover;"
    if "background-position" not in block:
        block += "background-position:center;"
    return block


def inject_image_into_guide(html: str, image_src: str) -> str:
    def _replace(match: re.Match) -> str:
        block = match.group(1)
        if "/images/" in block:
            return match.group(0)
        block = re.sub(
            r"background-image\s*:\s*(linear-gradient\([^;]+\))\s*;",
            rf"background-image:\1,url('{image_src}');",
            block,
            flags=re.IGNORECASE,
        )
        block = ensure_bg_size_position(block)
        return f".guide-hero{{{block}}}"

    return re.sub(r"\.guide-hero\s*\{([^{}]*)\}", _replace, html, count=1, flags=re.IGNORECASE | re.DOTALL)


def inject_image_into_state(html: str, image_src: str) -> str:
    # Preferred target in generated state pages: <section class="state-hero" style="background: ...;">
    section_re = re.compile(
        r'(<section[^>]*class=["\']state-hero["\'][^>]*style=["\'])([^"\']+)(["\'])',
        re.IGNORECASE,
    )
    section_match = section_re.search(html)
    if section_match:
        style_val = section_match.group(2)
        if "/images/" not in style_val:
            style_val = re.sub(
                r"background\s*:\s*(linear-gradient\([^;]+\))\s*;?",
                rf"background:\1, url('{image_src}');",
                style_val,
                flags=re.IGNORECASE,
            )
            if "background-size" not in style_val:
                style_val += " background-size: cover;"
            if "background-position" not in style_val:
                style_val += " background-position: center;"
        return section_re.sub(rf"\1{style_val}\3", html, count=1)

    def _replace(match: re.Match) -> str:
        block = match.group(1)
        if "/images/" in block:
            return match.group(0)
        block = re.sub(
            r"background\s*:\s*(linear-gradient\([^;]+\))\s*;",
            rf"background:\1, url('{image_src}');",
            block,
            flags=re.IGNORECASE,
        )
        block = ensure_bg_size_position(block)
        return f".state-hero{{{block}}}"

    return re.sub(r"\.state-hero\s*\{([^{}]*)\}", _replace, html, count=1, flags=re.IGNORECASE | re.DOTALL)


def inject_image_into_hub(html: str, image_src: str, selector: str) -> str:
    def _replace(match: re.Match) -> str:
        block = match.group(1)
        if "/images/" in block:
            return match.group(0)
        block = re.sub(
            r"background\s*:\s*(linear-gradient\([^;]+\))\s*;",
            rf"background:\1, url('{image_src}');",
            block,
            flags=re.IGNORECASE,
        )
        block = ensure_bg_size_position(block)
        return f"{selector}{{{block}}}"

    return re.sub(
        rf"{re.escape(selector)}\s*\{{([^{{}}]*)\}}",
        _replace,
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )


def inject_page_hero(page_rel: str, image_src: str) -> None:
    path = ROOT / page_rel
    html = path.read_text(encoding="utf-8", errors="ignore")
    original = html

    if page_rel.startswith("guides/"):
        html = inject_image_into_guide(html, image_src)
    elif page_rel.startswith("locations/") and page_rel != "locations/index.html":
        html = inject_image_into_state(html, image_src)
    elif page_rel == "locations/index.html":
        html = inject_image_into_hub(html, image_src, ".hero")
    elif page_rel == "guides-hub/index.html":
        html = inject_image_into_hub(html, image_src, ".guides-hero")

    if html != original:
        path.write_text(html, encoding="utf-8")


def update_generate_articles_template_hint() -> None:
    path = ROOT / "generate_articles.py"
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "hero-image-map.json" in text:
        return
    marker = "TEMPLATE_PATH = PROJECT_ROOT / \"guides\" / \"basalt-driveway\" / \"index.html\"\n"
    insert = (
        "TEMPLATE_PATH = PROJECT_ROOT / \"guides\" / \"basalt-driveway\" / \"index.html\"\n"
        "HERO_IMAGE_MAP_PATH = PROJECT_ROOT / \"hero-image-map.json\"  # Future hero image mapping input\n"
    )
    text = text.replace(marker, insert, 1)
    path.write_text(text, encoding="utf-8")


def update_generate_state_template_hint() -> None:
    path = ROOT / "generate_state_pages.py"
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "hero-image-map.json" in text:
        return
    marker = "BASE_URL = \"https://drivewayzusa.co\"\n"
    insert = (
        "BASE_URL = \"https://drivewayzusa.co\"\n"
        "HERO_IMAGE_MAP_PATH = os.path.join(PROJECT_ROOT, \"hero-image-map.json\")  # Future hero image mapping input\n"
    )
    text = text.replace(marker, insert, 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    api_key = load_env_key()
    if not MAP_PATH.exists():
        raise RuntimeError("hero-image-map.json not found. Run mapping script first.")

    mapping = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    downloaded = 0
    skipped_existing = 0
    failed: list[tuple[str, str]] = []

    for page_rel, info in mapping.items():
        slug = slug_for_page(page_rel)
        image_rel = f"/images/hero-{slug}.webp"
        image_path = IMAGES_DIR / f"hero-{slug}.webp"

        if image_path.exists():
            skipped_existing += 1
        else:
            query = info.get("search_keyword", "residential driveway")
            try:
                result = pexels_search(api_key, query)
                photo = pick_photo(result)
                raw = download_bytes(photo["src"]["large2x"])
                save_webp(raw, image_path)
                downloaded += 1
                time.sleep(API_DELAY_SECONDS)
            except (RuntimeError, HTTPError, URLError, OSError, subprocess.CalledProcessError) as exc:
                failed.append((page_rel, str(exc)))
                continue

        inject_page_hero(page_rel, image_rel)

    # Maintain crawlable hero <img> tags after updates.
    subprocess.run(["node", "scripts/add-hero-img-tags.js"], cwd=ROOT, check=True)

    # Template hints for future generation workflows.
    update_generate_articles_template_hint()
    update_generate_state_template_hint()

    print(f"Downloaded: {downloaded}")
    print(f"Skipped existing: {skipped_existing}")
    print(f"Failed: {len(failed)}")
    if failed:
        for rel, reason in failed[:20]:
            print(f"  - {rel}: {reason}")


if __name__ == "__main__":
    main()
