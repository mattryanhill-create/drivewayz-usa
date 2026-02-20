#!/usr/bin/env python3
"""
Generate individual static HTML files for each state from Drivewayz.txt files.
Uses locations/state-page.html as the template base.
Output: locations/[state-slug].html (e.g., florida.html, california.html)
"""

import re
import os
import html

# Config
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_DIR = os.path.join(PROJECT_ROOT, "locations")
TEMPLATE_PATH = os.path.join(LOCATIONS_DIR, "state-page.html")
BASE_URL = "https://www.drivewayzusa.com"
GA_TAG = "G-V08M9YKRR7"

# State/territory name to abbreviation mapping (50 states + DC + territories)
STATE_ABBREVIATIONS = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT",
    "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
    "maryland": "MD", "massachusetts": "MA", "michigan": "MI",
    "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
    "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
    "new york": "NY", "north carolina": "NC", "north dakota": "ND",
    "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
    "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY",
    # Territories (keys are slugs)
    "washington-dc": "DC", "puerto-rico": "PR", "us-virgin-islands": "VI",
    "guam": "GU", "american-samoa": "AS", "northern-mariana-islands": "MP",
}

# Generic services derived from common driveway types
DEFAULT_SERVICES = ["Concrete Installation", "Asphalt Paving", "Sealcoating", "Repairs"]

SERVICE_ICONS = {
    "Asphalt Paving": "🛣️", "Sealcoating": "🛡️", "Repairs": "🔧",
    "Concrete Installation": "🏗️", "Heated Driveways": "🔥", "Snow Removal": "❄️",
    "Concrete Paving": "🧱", "Decorative Concrete": "🎨", "Heat Resistant Coatings": "☀️",
    "Gravel Driveways": "🪨", "Drainage Solutions": "💧", "Pavers": "🔷",
    "Permeable Paving": "🌿", "Earthquake Resistant": "🌋",
}


def state_name_to_slug(name: str) -> str:
    """Convert state name to URL slug (e.g., 'New York' -> 'new-york')."""
    return name.lower().replace(".", "").replace(" ", "-")


def parse_drivewayz_txt(content: str, state_name: str) -> dict:
    """Parse a Drivewayz.txt file and extract structured data."""
    data = {
        "intro": "",
        "climate_summary": "",
        "driveway_types": [],
        "local_facts": [],
        "related_resources": [],
        "references": [],
        "cities": [],
        "cta_paragraph": "",
    }
    lines = content.split("\n")
    i = 0

    # Skip title line (e.g., "Florida Drivewayz – Expert...")
    while i < len(lines) and ("Drivewayz" in lines[i] or not lines[i].strip()):
        i += 1

    # Intro paragraph (climate description)
    intro_lines = []
    while i < len(lines):
        line = lines[i]
        if "Best Driveway Types for" in line:
            break
        if line.strip() and not line.strip().startswith("*"):
            intro_lines.append(line.strip())
        i += 1
    data["intro"] = " ".join(intro_lines).strip()
    if data["intro"]:
        data["climate_summary"] = data["intro"][:200] + "..." if len(data["intro"]) > 200 else data["intro"]

    # Best Driveway Types section
    while i < len(lines) and "Best Driveway Types" not in lines[i]:
        i += 1
    i += 1  # Skip header
    if i < len(lines) and not lines[i].strip():
        i += 1

    current_type = None
    while i < len(lines):
        line = lines[i]
        if "Local Facts" in line or "Local Facts &" in line:
            break
        # Match "1. Title" or "2. Title (Subtitle)"
        match = re.match(r"^(\d+)\.\s+(.+?)$", line.strip())
        if match:
            if current_type:
                data["driveway_types"].append(current_type)
            title = match.group(2).strip()
            current_type = {"title": title, "description": ""}
            i += 1
            # Collect description (following paragraphs)
            desc_lines = []
            while i < len(lines):
                next_line = lines[i]
                if re.match(r"^\d+\.\s+", next_line.strip()) or not next_line.strip():
                    break
                if not next_line.strip().startswith("*"):
                    desc_lines.append(next_line.strip())
                i += 1
            current_type["description"] = " ".join(desc_lines).strip()
        else:
            i += 1
    if current_type:
        data["driveway_types"].append(current_type)

    # Local Facts & Considerations
    while i < len(lines) and "Local Facts" not in lines[i] and "Considerations" not in lines[i]:
        i += 1
    i += 1
    if i < len(lines) and not lines[i].strip():
        i += 1

    while i < len(lines):
        line = lines[i]
        if "Get your driveway" in line or "Get Free Estimate" in line or "Related Resources" in line:
            if "Get your driveway" in line:
                data["cta_paragraph"] = line.strip()
                # Extract cities: "Whether you're in City1, City2, City3, or City4"
                cities_match = re.search(r"Whether you're in ([^.]+)", line, re.IGNORECASE)
                if cities_match:
                    cities_str = cities_match.group(1)
                    data["cities"] = [c.strip() for c in re.split(r",|\s+or\s+", cities_str, flags=re.I)]
                    data["cities"] = [c for c in data["cities"] if c and len(c) > 2]
            break
        # Match "* **Title**: Description"
        match = re.match(r"\*\s+\*\*(.+?)\*\*:\s*(.+)", line.strip())
        if match:
            data["local_facts"].append({"title": match.group(1).strip(), "description": match.group(2).strip()})
        i += 1

    # Related Resources
    while i < len(lines) and "Related Resources" not in lines[i]:
        i += 1
    i += 1
    if i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines):
        line = lines[i]
        if "References" in line and not line.strip().startswith("*"):
            break
        if line.strip().startswith("* ") and "References" not in line:
            title = line.strip().lstrip("* ").strip()
            if title:
                data["related_resources"].append({"title": title, "url": "../guides-hub.html"})
        i += 1

    # References
    while i < len(lines) and "References" not in lines[i]:
        i += 1
    i += 1
    if i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped and (re.match(r"^\[\d+\]", stripped) or stripped[0].isupper()):
            # Remove [1], [2] etc. from start
            ref = re.sub(r"^\[\d+\]\s*", "", stripped)
            if ref and len(ref) > 10:
                data["references"].append(ref)
        i += 1

    return data


def get_template_static_parts():
    """Extract static head, nav, footer, and styles from state-page.html."""
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract content between <head> and </head> (excluding dynamic title/meta)
    head_start = content.find("<head>") + 6
    head_end = content.find("</head>")
    head_content = content[head_start:head_end]

    # Remove/replace the default title and meta description (we'll add our own)
    head_content = re.sub(r'<title>.*?</title>', "{{TITLE}}", head_content, flags=re.DOTALL)
    head_content = re.sub(r'<meta name="description"[^>]*>', "{{META_DESCRIPTION}}", head_content)
    # Add canonical placeholder
    head_content = head_content.replace("{{META_DESCRIPTION}}", "{{META_DESCRIPTION}}\n    <link rel=\"canonical\" href=\"{{CANONICAL_URL}}\">")

    # Extract style block (from <style> to </style>)
    style_match = re.search(r"<style>(.*?)</style>", content, re.DOTALL)
    styles = style_match.group(1) if style_match else ""

    # Extract nav HTML
    nav_match = re.search(r'<nav class="navbar">(.*?)</nav>', content, re.DOTALL)
    nav_html = nav_match.group(0) if nav_match else ""

    # Extract footer HTML
    footer_match = re.search(r'<footer class="footer">(.*?)</footer>', content, re.DOTALL)
    footer_html = footer_match.group(0) if footer_match else ""

    return {
        "head_template": head_content,
        "styles": styles,
        "nav": nav_html,
        "footer": footer_html,
    }


def build_state_html(state_name: str, slug: str, data: dict) -> str:
    """Build complete HTML for a state page."""
    abbr = STATE_ABBREVIATIONS.get(slug, slug[:2].upper())
    canonical_url = f"{BASE_URL}/locations/{slug}.html"
    title = f"{state_name} Driveway Services | Drivewayz USA"
    meta_desc = f"Professional driveway installation and repair in {state_name}. Expert services for {state_name}'s unique climate. Free estimates. Call today."
    if data["climate_summary"]:
        meta_desc = data["climate_summary"][:155] + "..." if len(data["climate_summary"]) > 155 else data["climate_summary"]

    # Hero gradient - use consistent brand colors
    gradient = "linear-gradient(135deg, #2B5797 0%, #5B9BD5 50%, #4A90D9 100%)"
    hero_tagline = f"Expert Driveway Solutions for {state_name}"

    # Intro HTML
    intro_html = f"<p>{html.escape(data['intro'])}</p>" if data["intro"] else ""

    # Services - use generic based on driveway types or default
    services = DEFAULT_SERVICES[:3]
    services_html = "\n".join(
        f'''            <div class="service-card">
                <div class="service-icon">{SERVICE_ICONS.get(s, "🛠️")}</div>
                <h3>{html.escape(s)}</h3>
                <p>Professional {s.lower()} services designed specifically for {state_name}'s unique conditions and requirements.</p>
            </div>'''
        for s in services
    )

    # Driveway types
    driveway_types_html = ""
    if data["driveway_types"]:
        items = []
        for idx, dt in enumerate(data["driveway_types"], 1):
            items.append(f'''            <div class="driveway-type-card">
                <div class="type-number">{idx}</div>
                <h3>{html.escape(dt['title'])}</h3>
                <p>{html.escape(dt['description'])}</p>
            </div>''')
        driveway_types_html = "\n".join(items)

    # Benefits - derive from local facts or use generic
    benefits = [
        {"title": "Climate-Tailored Solutions", "description": f"Our driveway materials and installation techniques are specifically chosen to perform in {state_name}'s unique climate and soil conditions."},
        {"title": "Local Expertise", "description": f"We understand {state_name}'s permitting requirements, HOA regulations, and local building codes."},
        {"title": "Quality Guarantee", "description": "Professional installation with materials built to last. Free estimates, no obligation."},
    ]
    benefits_html = "\n".join(
        f'''            <div class="benefit-card">
                <div class="benefit-number">{idx + 1}</div>
                <div class="benefit-content">
                    <h3>{html.escape(b['title'])}</h3>
                    <p>{html.escape(b['description'])}</p>
                </div>
            </div>'''
        for idx, b in enumerate(benefits)
    )

    # Local facts (accordion)
    local_facts_html = ""
    if data["local_facts"]:
        items = []
        for fact in data["local_facts"]:
            items.append(f'''            <div class="fact-item">
                <button class="fact-header" onclick="this.parentElement.classList.toggle('active')">
                    <span class="fact-title">{html.escape(fact['title'])}</span>
                    <span class="fact-toggle">+</span>
                </button>
                <div class="fact-content">
                    <p>{html.escape(fact['description'])}</p>
                </div>
            </div>''')
        local_facts_html = "\n".join(items)

    # Cities - use parsed or generic
    cities = data["cities"]
    if not cities:
        cities = [f"{state_name} homeowners"]
    cities_html = "\n".join(
        f'''            <div class="city-card">
                <h4>{html.escape(c)}</h4>
                <p>Serving the area</p>
            </div>'''
        for c in cities[:6]
    )

    # References
    references_html = ""
    if data["references"]:
        references_html = "\n".join(f"            <li>{html.escape(r)}</li>" for r in data["references"])

    # Related resources
    resources_html = ""
    if data["related_resources"]:
        resources_html = "\n".join(
            f'            <a href="{html.escape(r["url"])}" target="_blank" rel="noopener" class="resource-link">{html.escape(r["title"])}</a>'
            for r in data["related_resources"]
        )

    # Climate info block
    climate_block = ""
    if data["climate_summary"]:
        climate_block = f'<div class="climate-info"><span class="climate-icon">🌤️</span><div><h4>Climate</h4><p>{html.escape(data["climate_summary"][:300])}</p></div></div>'

    # Driveway types section
    driveway_section = ""
    if driveway_types_html:
        driveway_section = (
            f"        <section class=\"driveway-types-section\">\n"
            f"            <div class=\"container\">\n"
            f"                <div class=\"section-header\">\n"
            f"                    <h2>Best Driveway Types for {state_name}</h2>\n"
            f"                    <p>Choose the right material for your climate, soil conditions, and budget</p>\n"
            f"                </div>\n"
            f"                <div class=\"driveway-types-grid\">\n"
            f"{driveway_types_html}\n"
            f"                </div>\n"
            f"            </div>\n"
            f"        </section>\n"
        )

    # Local facts section
    facts_section = ""
    if local_facts_html:
        facts_section = (
            f"        <section class=\"local-facts-section\">\n"
            f"            <div class=\"container\">\n"
            f"                <div class=\"section-header\">\n"
            f"                    <h2>Local Facts &amp; Considerations</h2>\n"
            f"                    <p>Important information for {state_name} homeowners planning a driveway project</p>\n"
            f"                </div>\n"
            f"                <div class=\"facts-accordion\">\n"
            f"{local_facts_html}\n"
            f"                </div>\n"
            f"            </div>\n"
            f"        </section>\n"
        )

    # References section
    refs_section = ""
    if references_html:
        refs_section = (
            f"        <section class=\"references-section\">\n"
            f"            <div class=\"container\">\n"
            f"                <h3>References &amp; Standards</h3>\n"
            f"                <ul class=\"references-list\">\n"
            f"{references_html}\n"
            f"                </ul>\n"
            f"            </div>\n"
            f"        </section>\n"
        )

    # Resources section
    res_section = ""
    if resources_html:
        res_section = (
            f"        <section class=\"resources-section\">\n"
            f"            <div class=\"container\">\n"
            f"                <h3>Related Resources</h3>\n"
            f"                <div class=\"resources-links\">\n"
            f"{resources_html}\n"
            f"                </div>\n"
            f"            </div>\n"
            f"        </section>\n"
        )

    # Build full content
    content_html = f'''    <!-- Main Content -->
    <main id="content">
        <!-- Hero Section -->
        <section class="state-hero" style="background: {gradient};">
            <div class="state-hero-content">
                <span class="state-badge">{abbr}</span>
                <h1>{html.escape(state_name)}</h1>
                <p class="tagline">{html.escape(hero_tagline)}</p>
                <a href="../index.html#contact" class="btn-primary">Get Your Free Estimate</a>
            </div>
        </section>

        <!-- Intro Section -->
        <section class="intro-section">
            <div class="container">
                <div class="intro-content">
                    <h2>Driveway Installation in {state_name}</h2>
                    <div class="intro-text">
                        {intro_html}
                    </div>
                </div>
                {climate_block}
            </div>
        </section>

        <!-- Services Section -->
        <section class="services-section">
            <div class="container">
                <div class="section-header">
                    <h2>Driveway Services in {state_name}</h2>
                    <p>Professional solutions tailored for {state_name}'s unique climate and terrain</p>
                </div>
                <div class="services-grid">
{services_html}
                </div>
            </div>
        </section>

        <!-- Driveway Types Section -->
{driveway_section}
        <!-- Why Choose Section -->
        <section class="why-section">
            <div class="container">
                <div class="section-header">
                    <h2>Why Choose Drivewayz in {state_name}</h2>
                    <p>Local expertise meets professional excellence</p>
                </div>
                <div class="benefits-grid">
{benefits_html}
                </div>
            </div>
        </section>

{facts_section}
        <!-- Service Areas -->
        <section class="areas-section">
            <div class="container">
                <div class="section-header">
                    <h2>Service Areas</h2>
                    <p>Serving communities across {state_name}</p>
                </div>
                <div class="cities-grid">
{cities_html}
                </div>
            </div>
        </section>

{refs_section}{res_section}
        <!-- CTA Section -->
        <section class="cta-section">
            <div class="cta-box">
                <h2>Ready to Transform Your Driveway?</h2>
                <p>Join thousands of satisfied homeowners in {state_name}. Get your free, no-obligation estimate today.</p>
                <a href="../index.html#contact" class="btn-primary">Schedule Free Estimate</a>
            </div>
        </section>
    </main>
'''

    # Read template and extract head
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        full_template = f.read()

    # Build head - we need title, meta description, canonical, GA
    head_start = full_template.find("<head>") + 6
    head_end = full_template.find("</head>")
    original_head = full_template[head_start:head_end]
    # Keep link and style, replace title and meta
    new_head = re.sub(r'<title>.*?</title>', f'<title>{html.escape(title)}</title>', original_head, count=1)
    new_head = re.sub(
        r'<meta name="description"[^>]*>',
        f'<meta name="description" content="{html.escape(meta_desc)}">',
        new_head, count=1
    )
    # Add canonical before closing head
    if "<link rel=\"canonical\"" not in new_head:
        new_head = new_head.replace("</style>", "</style>\n    <link rel=\"canonical\" href=\"" + canonical_url + "\">")
    # Ensure GA tag
    if GA_TAG not in new_head:
        ga_block = f'''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_TAG}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_TAG}');
</script>'''
        new_head = new_head + "\n" + ga_block

    # Get nav and footer from template
    nav_match = re.search(r'<nav class="navbar">.*?</nav>', full_template, re.DOTALL)
    footer_match = re.search(r'<footer class="footer">.*?</footer>', full_template, re.DOTALL)
    nav_html = nav_match.group(0) if nav_match else ""
    footer_html = footer_match.group(0) if footer_match else ""

    # Update footer with state name
    footer_html = re.sub(
        r'&copy; 2024 Drivewayz USA\. All rights reserved\.',
        f"&copy; 2024 Drivewayz USA. All rights reserved. | {state_name} Driveway Services",
        footer_html
    )

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <meta name="description" content="{html.escape(meta_desc)}">
    <link rel="canonical" href="{canonical_url}">
    <link rel="stylesheet" href="../main.css">
{full_template[full_template.find("<style>"):full_template.find("</style>") + 8]}
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_TAG}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_TAG}');
</script>
</head>

<body>
    {nav_html}

{content_html}

    {footer_html}
</body>
</html>"""

    return full_html


def main():
    """Main entry point."""
    # Find all Drivewayz.txt files
    txt_files = [f for f in os.listdir(PROJECT_ROOT) if f.endswith(" Drivewayz.txt")]
    print(f"Found {len(txt_files)} Drivewayz.txt files")

    generated = []
    for filename in sorted(txt_files):
        # Extract state name: "Florida Drivewayz.txt" -> "Florida"
        state_name = filename.replace(" Drivewayz.txt", "").strip()
        slug = state_name_to_slug(state_name)

        txt_path = os.path.join(PROJECT_ROOT, filename)
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()

        data = parse_drivewayz_txt(content, state_name)
        html_content = build_state_html(state_name, slug, data)

        output_path = os.path.join(LOCATIONS_DIR, f"{slug}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        generated.append((state_name, slug))
        print(f"  Generated: {slug}.html ({state_name})")

    print(f"\nDone! Generated {len(generated)} state pages in {LOCATIONS_DIR}/")
    return generated


if __name__ == "__main__":
    main()
