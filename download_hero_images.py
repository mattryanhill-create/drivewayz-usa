#!/usr/bin/env python3
"""
Download hero images from Unsplash and inject them into gradient-only pages.

Uses hero-image-map.json (search_keyword per page). Requires UNSPLASH_ACCESS_KEY in .env.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
MAP_PATH = ROOT / "hero-image-map.json"
IMAGES_DIR = ROOT / "images"
UNSPLASH_ENDPOINT = "https://api.unsplash.com/search/photos"
API_DELAY_SECONDS = 2


def load_env_key() -> str:
    env_path = ROOT / ".env"
    if not env_path.exists():
        raise RuntimeError(".env not found. Add UNSPLASH_ACCESS_KEY=... first.")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("UNSPLASH_ACCESS_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("UNSPLASH_ACCESS_KEY not found in .env")


def slug_for_page(page_rel: str) -> str:
    path = Path(page_rel)
    if page_rel == "locations/index.html":
        return "locations-hub"
    if page_rel == "guides-hub/index.html":
        return "guides-hub"
    if path.name == "index.html" and len(path.parts) >= 2:
        return path.parts[-2]
    return path.stem


def unsplash_search(access_key: str, query: str) -> tuple[dict, int, str]:
    params = {
        "query": query,
        "orientation": "landscape",
        "per_page": 1,
        "page": 1,
    }
    search_url = f"{UNSPLASH_ENDPOINT}?{urlencode(params)}"
    req = Request(search_url)
    req.add_header("Authorization", f"Client-ID {access_key}")
    with urlopen(req, timeout=30) as resp:
        status = int(resp.getcode() or 0)
        return json.loads(resp.read().decode("utf-8")), status, search_url


def pick_photo(result: dict) -> dict:
    results = result.get("results", [])
    if not results:
        raise RuntimeError("No photos returned from Unsplash")
    photo = results[0]
    urls = photo.get("urls", {})
    if not urls.get("regular"):
        raise RuntimeError("No regular URL in Unsplash result")
    return photo


def download_bytes(url: str) -> tuple[bytes, int]:
    req = Request(url, headers={"User-Agent": "drivewayz-usa-hero-pipeline/1.0"})
    with urlopen(req, timeout=60) as resp:
        status = int(resp.getcode() or 0)
        return resp.read(), status


def save_webp(raw: bytes, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
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
        block = re.sub(
            r"background-image\s*:\s*(linear-gradient\([^;]+\))\s*(?:,\s*url\([^;]+\))?\s*;",
            rf"background-image:\1,url('{image_src}');",
            block,
            flags=re.IGNORECASE,
        )
        if "background-image" not in block:
            block = re.sub(
                r"background\s*:\s*(linear-gradient\([^;]+\))\s*(?:,\s*url\([^;]+\))?\s*;",
                rf"background:\1, url('{image_src}');",
                block,
                flags=re.IGNORECASE,
            )
        if "background-image" not in block and "background:" not in block:
            block = f"background:linear-gradient(135deg,rgba(0,0,0,.45) 0%,rgba(0,0,0,.45) 100%), url('{image_src}');" + block
        block = ensure_bg_size_position(block)
        return f".guide-hero{{{block}}}"

    return re.sub(r"\.guide-hero\s*\{([^{}]*)\}", _replace, html, count=1, flags=re.IGNORECASE | re.DOTALL)


def inject_image_into_state(html: str, image_src: str) -> str:
    section_re = re.compile(
        r'(<section[^>]*class=["\']state-hero["\'][^>]*style=["\'])([^"\']+)(["\'])',
        re.IGNORECASE,
    )
    section_match = section_re.search(html)
    if section_match:
        style_val = section_match.group(2)
        # Use semi-transparent gradient so photo shows through (solid hex hides it)
        semi_transparent = f"linear-gradient(135deg, rgba(43, 87, 151, 0.7) 0%, rgba(91, 155, 213, 0.6) 50%, rgba(74, 144, 217, 0.6) 100%), url('{image_src}')"
        style_val = re.sub(
            r"background\s*:\s*(?:linear-gradient\([^;]+\)\s*,?\s*)?(?:url\([^)]+\)\s*)?;?",
            f"background: {semi_transparent}; ",
            style_val,
            count=1,
            flags=re.IGNORECASE,
        )
        if "background:" not in style_val:
            style_val = f"background: {semi_transparent}; " + style_val
        if "background-size" not in style_val:
            style_val += " background-size: cover;"
        if "background-position" not in style_val:
            style_val += " background-position: center;"
        return section_re.sub(rf"\1{style_val}\3", html, count=1)

    def _replace(match: re.Match) -> str:
        block = match.group(1)
        block = re.sub(
            r"background\s*:\s*(linear-gradient\([^;]+\))\s*(?:,\s*url\([^;]+\))?\s*;",
            rf"background:\1, url('{image_src}');",
            block,
            flags=re.IGNORECASE,
        )
        if "background:" not in block:
            block = f"background:linear-gradient(135deg,rgba(43,87,151,.8),rgba(91,155,213,.6)), url('{image_src}');" + block
        block = ensure_bg_size_position(block)
        return f".state-hero{{{block}}}"

    return re.sub(r"\.state-hero\s*\{([^{}]*)\}", _replace, html, count=1, flags=re.IGNORECASE | re.DOTALL)


def inject_image_into_hub(html: str, image_src: str, selector: str) -> str:
    # Use semi-transparent gradient so photo shows through
    semi_transparent = f"linear-gradient(135deg, rgba(43, 87, 151, 0.65) 0%, rgba(91, 155, 213, 0.6) 100%), url('{image_src}')"

    def _replace(match: re.Match) -> str:
        block = match.group(1)
        block = re.sub(
            r"background\s*:\s*(?:linear-gradient\([^;]+\)\s*,?\s*)?(?:url\([^)]+\)\s*)?;?",
            f"background: {semi_transparent}; ",
            block,
            count=1,
            flags=re.IGNORECASE,
        )
        if "background:" not in block:
            block = f"background: {semi_transparent}; " + block
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
    marker = 'TEMPLATE_PATH = PROJECT_ROOT / "guides" / "basalt-driveway" / "index.html"\n'
    insert = marker + 'HERO_IMAGE_MAP_PATH = PROJECT_ROOT / "hero-image-map.json"\n'
    text = text.replace(marker, insert, 1)
    path.write_text(text, encoding="utf-8")


def update_generate_state_template_hint() -> None:
    path = ROOT / "generate_state_pages.py"
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "hero-image-map.json" in text:
        return
    marker = 'BASE_URL = "https://drivewayzusa.co"\n'
    insert = marker + 'HERO_IMAGE_MAP_PATH = os.path.join(PROJECT_ROOT, "hero-image-map.json")\n'
    text = text.replace(marker, insert, 1)
    path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and inject hero images from Unsplash.")
    parser.add_argument(
        "--limit-guides",
        nargs="+",
        default=[],
        help="Only process these mapping paths.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned API calls without network/filesystem changes.",
    )
    args = parser.parse_args()
    normalized: list[str] = []
    for token in args.limit_guides:
        normalized.extend([p.strip() for p in token.split(",") if p.strip()])
    args.limit_guides = normalized
    return args


def main() -> None:
    args = parse_args()
    access_key = load_env_key()
    if not MAP_PATH.exists():
        raise RuntimeError("hero-image-map.json not found. Run mapping script first.")

    mapping: dict[str, dict] = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    if args.limit_guides:
        selected: dict[str, dict] = {}
        for rel in args.limit_guides:
            if rel in mapping:
                selected[rel] = mapping[rel]
            else:
                print(f"[WARN] Not in hero-image-map.json: {rel}")
        mapping = selected

    downloaded = 0
    skipped_existing = 0
    failed: list[tuple[str, str]] = []
    processed = 0

    if args.dry_run:
        print("[INFO] Dry-run; no API calls or file writes.")

    for page_rel, info in mapping.items():
        processed += 1
        slug = slug_for_page(page_rel)
        query = info.get("search_keyword", "residential driveway")
        image_rel = f"/images/hero-{slug}.webp"
        image_path = IMAGES_DIR / f"hero-{slug}.webp"

        if args.dry_run:
            search_url = f"{UNSPLASH_ENDPOINT}?query={query}&orientation=landscape&per_page=1"
            print(f"\n[PLAN] {page_rel}")
            print(f"  query: {query}")
            print(f"  search_url: {search_url}")
            print(f"  would_write: {image_path.relative_to(ROOT)}")
            print(f"  would_inject: {image_rel}")
            continue

        if image_path.exists():
            skipped_existing += 1
            inject_page_hero(page_rel, image_rel)
            time.sleep(API_DELAY_SECONDS)
            continue

        query_used = query
        try:
            result, search_status, real_url = unsplash_search(access_key, query)
            print(f"[{page_rel}] HTTP {search_status} search")
            try:
                photo = pick_photo(result)
            except RuntimeError as e:
                if "No photos" in str(e) and query != "residential driveway home":
                    query_used = "residential driveway home"
                    result, search_status, _ = unsplash_search(access_key, query_used)
                    print(f"[{page_rel}] fallback HTTP {search_status} search")
                    time.sleep(API_DELAY_SECONDS)
                    photo = pick_photo(result)
                else:
                    raise
            url = photo["urls"]["regular"]
            raw, image_status = download_bytes(url)
            print(f"[{page_rel}] HTTP {image_status} image download")
            save_webp(raw, image_path)
            downloaded += 1
            inject_page_hero(page_rel, image_rel)
        except (RuntimeError, HTTPError, URLError, OSError, subprocess.CalledProcessError) as exc:
            failed.append((page_rel, str(exc)))
            continue

        time.sleep(API_DELAY_SECONDS)

    if not args.dry_run and (downloaded > 0 or skipped_existing > 0):
        add_hero_script = ROOT / "scripts" / "add-hero-img-tags.js"
        if add_hero_script.exists():
            subprocess.run(["node", str(add_hero_script)], cwd=ROOT, check=False)
        update_generate_articles_template_hint()
        update_generate_state_template_hint()

    print(f"\nProcessed: {processed}, Downloaded: {downloaded}, Skipped existing: {skipped_existing}, Failed: {len(failed)}")
    if failed:
        for rel, reason in failed[:20]:
            print(f"  - {rel}: {reason}")


if __name__ == "__main__":
    main()
