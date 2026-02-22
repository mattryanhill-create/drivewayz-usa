#!/usr/bin/env python3
"""
Technical SEO audit: internal links, broken paths, orphans, legacy URLs.
Outputs findings and optionally fixes.
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent

# Patterns for legacy/staging URLs
LEGACY_DOMAINS = [
    r"drivewayz\.com",
    r"www\.drivewayz\.com",
    r"drivewayzusa\.com",
    r"www\.drivewayzusa\.com",
    r"staging\.drivewayz",
    r"dev\.drivewayz",
    r"drivewayz-usa\.netlify",
    r"drivewayz-usa\.vercel",
]
LEGACY_PATTERN = re.compile(
    r"https?://(?:www\.)?(" + "|".join(LEGACY_DOMAINS) + r")[^\s\"'<>]*",
    re.I
)


def find_all_html(root: Path) -> list[Path]:
    """Find all HTML files excluding node_modules, .git."""
    html_files = []
    for p in root.rglob("*.html"):
        rel = p.relative_to(root)
        if any(part.startswith(".") or part == "node_modules" for part in rel.parts):
            continue
        html_files.append(p)
    return html_files


def path_to_url_path(p: Path, root: Path) -> str:
    """Convert file path to URL path (e.g. locations/florida/index.html -> /locations/florida/)."""
    rel = p.relative_to(root)
    parts = rel.parts
    # index.html at end -> directory URL with trailing slash
    if parts[-1] == "index.html":
        return "/" + "/".join(parts[:-1]) + "/"
    return "/" + "/".join(parts)


def url_path_to_file(root: Path, href: str) -> Optional[Path]:
    """Resolve href (path-only) to file path. Returns Path if exists, else None."""
    # Normalize: strip query/fragment
    path_part = href.split("?")[0].split("#")[0]
    if not path_part or path_part.startswith("mailto:") or path_part.startswith("tel:"):
        return None
    # Ensure starts with /
    if not path_part.startswith("/"):
        path_part = "/" + path_part
    # Remove leading/trailing slashes for path join
    clean = path_part.strip("/")
    if not clean:
        candidate = root / "index.html"
        return candidate if candidate.exists() else None
    # /locations/florida/ -> locations/florida/index.html
    # /guides/foo/ -> guides/foo/index.html
    # /for-homeowners/ -> for-homeowners/index.html
    base = clean.rstrip("/")
    # Handle .html in path: /foo.html -> foo.html or foo/index.html
    if base.endswith(".html"):
        base = base[:-5]
    candidates = [
        root / base / "index.html",
        root / (base + "/index.html"),
        root / base,
        root / (base + ".html"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def extract_internal_hrefs(html_content: str, base_dir: Path) -> list[str]:
    """Extract internal href values (path-only). Excludes external URLs."""
    # Match href="..." or href='...'
    pattern = re.compile(r'\bhref\s*=\s*["\']([^"\']+)["\']', re.I)
    internal = []
    for m in pattern.finditer(html_content):
        href = m.group(1).strip()
        # Skip external
        if href.startswith("http://") or href.startswith("https://"):
            continue
        if href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
            continue
        if href == "#" or (href.startswith("#") and len(href) > 1):
            continue  # Anchors
        # Include relative and absolute path
        internal.append(href)
    return internal


def normalize_href(href: str) -> str:
    """Normalize href for comparison (path-only, no fragment)."""
    path = href.split("?")[0].split("#")[0].strip()
    if not path.startswith("/"):
        path = "/" + path
    # Ensure trailing slash for directories
    if path and not path.endswith("/") and "." not in path.split("/")[-1]:
        path = path + "/"
    return path.rstrip("/") + "/" if path != "/" else "/"


def run_audit():
    root = PROJECT_ROOT
    html_files = find_all_html(root)

    # Build set of valid URL paths (what exists)
    url_to_file = {}
    file_to_url = {}
    for f in html_files:
        url = path_to_url_path(f, root)
        url_to_file[url] = f
        file_to_file_url = str(f.relative_to(root))
        file_to_url[f] = url

    # Canonical forms: /path/ and /path (index) 
    valid_paths = set()
    for f in html_files:
        rel = f.relative_to(root)
        if rel.name == "index.html":
            dir_path = "/" + "/".join(rel.parts[:-1]) + "/"
            valid_paths.add(dir_path)
            valid_paths.add(dir_path.rstrip("/"))
        else:
            valid_paths.add("/" + str(rel).replace("\\", "/"))

    # For each HTML file, extract internal links and check
    link_map = {}  # file -> list of (href, resolved_path|None)
    broken = []  # (source_file, href)
    legacy_refs = []  # (source_file, matched_url)
    all_inbound = defaultdict(list)

    for f in html_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        hrefs = extract_internal_hrefs(content, root)
        link_map[f] = []

        for href in hrefs:
            # Skip template/JS placeholders
            if "${" in href or "{{" in href:
                continue
            # Resolve href to file
            resolved = url_path_to_file(root, href)
            link_map[f].append((href, resolved))
            if resolved is None:
                broken.append((str(f.relative_to(root)), href))
            else:
                all_inbound[resolved].append(f)

        # Check for legacy URLs
        for m in LEGACY_PATTERN.finditer(content):
            legacy_refs.append((str(f.relative_to(root)), m.group(0)))

    # Orphans: HTML files with no incoming internal links (except index.html, guides-hub, locations index)
    orphans = []
    root_index = root / "index.html"
    guides_hub = root / "guides-hub" / "index.html" if (root / "guides-hub").exists() else None
    guides_hub_html = root / "guides-hub.html"
    locations_index = root / "locations" / "index.html"

    for f in html_files:
        if f == root_index:
            continue  # Homepage often linked from nav/footer
        incoming = all_inbound.get(f, [])
        if not incoming:
            orphans.append(str(f.relative_to(root)))

    return {
        "html_count": len(html_files),
        "valid_paths": valid_paths,
        "link_map": {str(f.relative_to(root)): [(h, str(r) if r else None) for h, r in links] for f, links in link_map.items()},
        "broken": broken,
        "legacy_refs": legacy_refs,
        "orphans": orphans,
        "file_to_url": {str(f.relative_to(root)): file_to_url[f] for f in html_files},
    }


def fix_href(href: str) -> Optional[str]:
    """
    Suggest fixed href for broken links.
    .html -> /path/ migration: /for-homeowners.html -> /for-homeowners/
    """
    path = href.split("?")[0].split("#")[0]
    if not path.startswith("/"):
        path = "/" + path
    # Old .html URLs: /guides-hub.html -> /guides-hub/
    if path.endswith(".html"):
        return path[:-5] + "/"  # Remove .html, add /
    return None


if __name__ == "__main__":
    audit = run_audit()
    print("HTML files:", audit["html_count"])
    print("Broken links:", len(audit["broken"]))
    for src, href in audit["broken"][:20]:
        print(f"  {src} -> {href}")
    print("Legacy refs:", len(audit["legacy_refs"]))
    for src, url in audit["legacy_refs"][:10]:
        print(f"  {src}: {url[:60]}...")
    print("Orphans (sample):", audit["orphans"][:15])
