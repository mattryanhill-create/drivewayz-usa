# Structured Data & Internal Links Script

## Overview

`add_structured_data_and_internal_links.py` processes every `guides/*/index.html` file to:

1. **Add JSON-LD structured data** (Article + FAQPage when FAQs exist)
2. **Enhance internal links** in the `guide-internal-links` nav section with contextual links

The script is **safe and idempotent**: it skips files that already contain `application/ld+json`, skips the `gravel-pothole-repair` guide (manually crafted schema), and never modifies CSS, JavaScript, form logic, canonical tags, meta tags, or any file outside `guides/*/index.html`.

## Requirements

- **Python 3.6+** (standard library only — no pip dependencies)

## Usage

### Dry-run (default)

Preview what would change without writing files:

```bash
python3 scripts/add_structured_data_and_internal_links.py
```

### Apply changes

Write changes to disk (creates `index.html.bak` backup before modifying each file):

```bash
python3 scripts/add_structured_data_and_internal_links.py --apply
```

## What the Script Does

### Task 1: JSON-LD Structured Data

For each guide that does **not** already have `application/ld+json`:

- **Article schema** — Injected immediately before the `/main.css` stylesheet link:
  - `headline` from `<title>` (suffixes like `| Drivewayz USA` stripped)
  - `description` from `<meta name="description">`
  - `mainEntityOfPage` @id from canonical link
  - `author` / `publisher`: Drivewayz USA
  - `datePublished`: 2025-01-15, `dateModified`: 2025-03-01
  - Image: `https://drivewayzusa.co/images/hero-{folder-name}.webp`

- **FAQPage schema** — Only if FAQ content is found:
  - Parses `.faq-item` elements with `.faq-q` (question) and `.faq-a` (answer)
  - If no FAQ content is detected, the FAQPage block is **not** added

### Task 2: Internal Links

For each guide, finds `<nav class="guide-internal-links" aria-label="Related pages">` and adds 2–3 contextual links based on the guide’s folder name:

| Keyword in folder name | Link added |
|------------------------|------------|
| State (e.g. florida, texas, california) | `/locations/{state}/` — "Driveway services in {State}" |
| asphalt | `/guides/concrete-vs-asphalt-vs-gravel/` — "Compare driveway materials" |
| concrete | `/guides/concrete-vs-asphalt-vs-gravel/` — "Compare driveway materials" |
| gravel | `/guides/gravel-pothole-repair/` — "Gravel pothole repair guide" |
| cost, pricing | `/cost-calculator/` — "Calculate your driveway cost" |
| repair, fix | `/for-homeowners/` — "Homeowner repair resources" |
| seal, coat | `/guides/driveway-sealing-complete-guide/` — "Complete sealing guide" |
| drain | `/guides/driveway-drainage-problems-causes-and-fixes/` — "Drainage solutions guide" |

- Existing links (including "View all driveway guides") are preserved.
- At most 3 new links are added; total links are capped at 4.
- Duplicate `href`s are not added.

## Safety

- **Dry-run by default** — Must use `--apply` to write changes
- **Backup on apply** — Each modified file is copied to `index.html.bak` before editing
- **Idempotent** — Re-running skips files that already have structured data
- **Scope-limited** — Only inserts JSON-LD and nav links; does not alter CSS, JS, forms, meta, canonical, or robots.txt
- **Gravel-pothole-repair excluded** — Never modified

## Verifying Results

### After dry-run

- Check the printed summary: files processed, modified, skipped, errors
- Inspect sample output for a few paths

### After apply

1. **Structured data**
   - Open a modified guide in a browser
   - View page source and confirm `<script type="application/ld+json">` appears in `<head>` before the main.css link
   - Use [Google Rich Results Test](https://search.google.com/test/rich-results) or [Schema.org validator](https://validator.schema.org/) on a sample URL

2. **Internal links**
   - Scroll to the bottom of a guide
   - Find the "Related pages" nav and confirm new contextual links appear (e.g. state, material, cost calculator)

3. **Backups**
   - Each modified `guides/*/index.html` should have a corresponding `index.html.bak` in the same folder

## Example Output

```
Dry-run mode (use --apply to write changes)
------------------------------------------------------------
  MODIFY (add schema): guides/driveway-polyaspartic-coating-fast-cure-alternative/index.html
  MODIFY (add links): guides/driveway-polyaspartic-coating-fast-cure-alternative/index.html
    -> Would write (dry-run)
  SKIP (gravel-pothole-repair): guides/gravel-pothole-repair/index.html
  SKIP (has schema): guides/concrete-vs-asphalt-vs-gravel/index.html
------------------------------------------------------------
Summary:
  Files processed: 1018
  Files modified: 1015
  Skipped (already had schema): 6
  Skipped (gravel-pothole-repair): 1
  Errors: 0
```
