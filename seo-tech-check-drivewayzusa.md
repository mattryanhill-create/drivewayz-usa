# Technical SEO Check — Drivewayz USA

**Date:** February 22, 2026  
**Scope:** Internal links, broken paths, orphan files, legacy URLs (HTML files only)

---

## Summary

| Metric | Before | After |
|--------|--------|-------|
| **Broken internal links** | 14 | 2 |
| **Legacy .com / staging URLs** | 1 | 0 |
| **HTML files audited** | 1,149 | 1,149 |

---

## Broken Links — Fixed

The following broken internal links were corrected:

| Source | Old Path | New Path |
|--------|----------|----------|
| `index.html` | `/guides/exposed-aggregate-driveway/` | `/guides/exposed-aggregate-concrete-driveway-guide/` |
| `index.html` | `/guides/pavestone-driveway/` | `/guides/paver-driveway-installation-step-by-step-guide/` |
| `guides/best-driveway-luxury-homes/` | `/guides/paver-driveway-guide/` | `/guides/paver-driveway-installation-step-by-step-guide/` |
| `guides/best-material-long-rural-driveway/` | `/guides/gravel-driveway/` | `/guides/gravel-driveway-installation-step-by-step-guide/` |
| `guides/budget-long-rural-driveway/` | `/guides/gravel-driveway/` | `/guides/gravel-driveway-installation-step-by-step-guide/` |
| `guides/budget-driveway-small-urban-lot/` | `/guides/driveway-layouts-straight-l-shaped-circular/` | `/guides/driveway-layouts-straight-l-shaped-circular-and-more/` |
| `guides/budget-driveway-small-urban-lot/` | `/guides/driveway-cost-per-square-foot-guide/` | `/guides/how-much-does-a-new-driveway-cost-in-2026/` |
| `guides/best-driveway-hoa-neighborhoods/` | `/guides/driveway-easements-right-of-way/` | `/guides/driveway-right-of-way-and-easements-what-homeowners-need-to-know/` |
| `guides/best-driveway-hoa-neighborhoods/` | `/guides/paver-driveway-guide/` | `/guides/paver-driveway-installation-step-by-step-guide/` |
| `guides/driveway-critical-path-method-project-scheduling-technique/` | `/checklist` | `/cost-calculator/` |

---

## Legacy URL — Fixed

| File | Old | New |
|------|-----|-----|
| `guides/asphalt-driveway-cost-in-illinois-local-pricing/index.html` | `https://drivewayzusa.com/verify` | `https://drivewayzusa.co/verify` |
| `locations/index.html` (footer) | `www.drivewayzusa.com` (display text) | `drivewayzusa.co` |

---

## Files Requiring Manual Review

### 1. Broken links to non-HTML assets (targets do not exist)

| Source | Target | Suggestion |
|--------|--------|------------|
| `guides/driveway-project-checklist-for-homeowners-free-pdf/index.html` | `/downloads/driveway-project-checklist-homeowners.pdf` | Create the PDF and place in `downloads/`, or update the link to a relevant existing resource (e.g. `/cost-calculator/`) |
| `guides/driveway-critical-path-method-project-scheduling-technique/index.html` | `/pdf/driveway-cpm-cards.pdf` | Create the PDF and place in `pdf/`, or remove/rewrite the link |

### 2. Orphan files (no incoming internal links)

**65 redirect stubs** — intentional for legacy URLs (e.g. `for-homeowners.html` → `/for-homeowners/`, `locations/florida.html` → `/locations/florida/`). No action required.

**1 additional orphan:** `locations.html` — redirect to `/locations/`. Also a redirect stub; no action required.

---

## Methodology

- **Internal map:** All `*.html` files parsed; `href` values extracted (path-only, excluding external URLs, anchors, mailto, tel).
- **Broken links:** `href` resolved to filesystem; target missing → broken.
- **Orphans:** HTML files with zero incoming internal links.
- **Legacy refs:** Regex match for `drivewayz.com`, `drivewayzusa.com`, staging/netlify/vercel URLs.
- **Excluded:** Template placeholders (`${...}`), external links, `#` anchors.

---

## Audit Script

Run `python3 seo_tech_audit.py` to re-run the audit.
