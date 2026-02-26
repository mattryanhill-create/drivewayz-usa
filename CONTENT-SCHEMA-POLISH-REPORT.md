# Content Schema Polish – Summary Report

**Branch:** `content-schema-polish`  
**Date:** February 24, 2026

---

## Task 1: Structured Data Schema

### Pages updated with JSON-LD schema

| Page | Article | FAQ | HowTo | Notes |
|------|---------|-----|-------|-------|
| `/guides/gravel-pothole-repair/` | ✓ | ✓ | ✓ | 7 repair steps in HowTo |
| `/guides/chip-seal-driveway/` | ✓ | ✓ | — | 4 FAQ items |
| `/guides/concrete-vs-asphalt-vs-gravel/` | ✓ | ✓ | — | 4 FAQ items |
| `/cost-calculator/` | ✓ | — | — | Tool/guide page |
| `/guides/driveway-pros-and-cons-by-material-complete-breakdown/` | ✓ | — | — | Materials comparison |
| `/guides/percolation-test-for-driveway-drainage-planning/` | ✓ | — | — | Drainage planning |
| `/guides/driveway-drainage-problems-causes-and-fixes/` | ✓ | — | — | Drainage fixes |
| `/guides/driveway-basics-types-costs-lifespan/` | ✓ | — | — | Driveway basics |

### Schema properties used

- **Article:** @context, @type, headline, description, author, datePublished, dateModified, image, mainEntityOfPage
- **FAQ:** mainEntity with question/answer pairs (Question, acceptedAnswer, Answer)
- **HowTo:** step array with name, text, url

### Validation

Run through [Google Rich Results Test](https://search.google.com/test/rich-results) and [schema.org validator](https://validator.schema.org/) before deployment.

---

## Task 2: Internal Linking

### Guide pages enhanced with contextual links

| Guide | Links added | Target pages |
|-------|-------------|--------------|
| **gravel-pothole-repair** | 6 | drainage-problems, percolation-test, concrete-vs-asphalt, driveway-basics, cost-calculator, locations/florida |
| **chip-seal-driveway** | 4 | concrete-vs-asphalt, driveway-base-subgrade, gravel-pothole-repair, cost-calculator, locations/texas |
| **concrete-vs-asphalt-vs-gravel** | 4 | cost-calculator, chip-seal, driveway-pros-and-cons, locations/michigan |

### guides-hub

Added a “Popular driveway guides” section with descriptive anchor text links:

- How to fix gravel driveway potholes
- Chip seal driveway cost guide
- Concrete vs asphalt vs gravel comparison
- Driveway cost calculator
- Driveway pros and cons by material
- Driveway drainage problems and fixes
- Driveway basics: types, costs and lifespan

### Location pages

Existing location pages already link to 2–3 relevant guides in the sidebar. No changes made.

### Link density

- Contextual links in body content only (no generic “click here”)
- About 2–4 internal links per 500 words
- Descriptive anchor text used throughout

---

## Task 3: Privacy Policy

### New file

**Path:** `/privacy-policy/index.html`

### Sections

1. **Introduction** – What data is collected and why  
2. **Information we collect** – Form submissions, cookies, analytics  
3. **How we use information** – Contractor matching, service improvement  
4. **Data sharing** – Contractors, HubSpot, n8n, hosting  
5. **Your rights** – Access, correction, deletion  
6. **Contact** – privacy@drivewayzusa.co  

### Footer link

- Privacy Policy link updated from `#` to `/privacy-policy/` across **1,084+ HTML pages**
- `js/guides-enhancements.js` footer injection updated for the guides-hub page

---

## Schema types by page

| Page | Article | FAQ | HowTo |
|------|---------|-----|-------|
| gravel-pothole-repair | ✓ | ✓ | ✓ |
| chip-seal-driveway | ✓ | ✓ | — |
| concrete-vs-asphalt-vs-gravel | ✓ | ✓ | — |
| cost-calculator | ✓ | — | — |
| driveway-pros-and-cons-by-material | ✓ | — | — |
| percolation-test | ✓ | — | — |
| driveway-drainage-problems | ✓ | — | — |
| driveway-basics | ✓ | — | — |

---

## Internal link count per page

| Page | New contextual links |
|------|----------------------|
| gravel-pothole-repair | 6 |
| chip-seal-driveway | 4 |
| concrete-vs-asphalt-vs-gravel | 4 |
| guides-hub | 7 (new featured section) |

---

## Constraints followed

- No changes to homeowner funnel, n8n, HubSpot, or email automation
- Only static HTML content and JSON-LD schema modified
- No JavaScript changes except the Privacy Policy link in `guides-enhancements.js` footer
- No form, CSS, or styling changes beyond the privacy policy link
