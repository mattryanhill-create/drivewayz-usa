# Hero Image Uniqueness Audit

**Audit date:** 2026-07-09

## Summary

| Metric | Count |
|--------|------:|
| Pages scanned | **1086** |
| Pages with a hero image | **1085** |
| Pages missing hero image | **1** |
| Unique hero image files in use | **98** |
| Images used on 2+ pages | **12** |
| Extra page slots filled by reused images | **987** |
| Images reused on 3+ pages | **12** |
| Guides not using slug-matched `hero-{slug}.webp` | **1001** |

## How to read this audit

- **Goal:** every indexable page should have a distinct hero image.
- **Guide convention:** `/images/hero-{page-slug}.webp` (e.g. `guides/foo-bar/` → `hero-foo-bar.webp`).
- **Location convention:** `/images/hero-{state-slug}.webp` (already slug-matched).
- **Marketing pages:** shared stock images are acceptable only where intentional (e.g. thank-you pages).

## High-priority duplicates (3+ pages)

### `/images/pexels-curtis-adams-1694007-3990589.webp` — **477 pages**

- `for-homeowners/index.html` → /for-homeowners/
- `guides/driveway-30-year-total-cost-material-lifecycle-comparison/index.html` → /guides/driveway-30-year-total-cost-material-lifecycle-comparison/
- `guides/driveway-3d-scanning-creating-digital-twin-of-your-surface/index.html` → /guides/driveway-3d-scanning-creating-digital-twin-of-your-surface/
- `guides/driveway-abrasion-resistance-how-surfaces-wear-over-time/index.html` → /guides/driveway-abrasion-resistance-how-surfaces-wear-over-time/
- `guides/driveway-access-permit-municipal-street-connection/index.html` → /guides/driveway-access-permit-municipal-street-connection/
- `guides/driveway-acrylic-sealer-water-based-protection/index.html` → /guides/driveway-acrylic-sealer-water-based-protection/
- `guides/driveway-ada-transition-plan-municipal-accessibility-upgrades/index.html` → /guides/driveway-ada-transition-plan-municipal-accessibility-upgrades/
- `guides/driveway-aggregate-color-options-regional-stone-varieties/index.html` → /guides/driveway-aggregate-color-options-regional-stone-varieties/
- `guides/driveway-aggregate-size-guide-fine-medium-and-coarse/index.html` → /guides/driveway-aggregate-size-guide-fine-medium-and-coarse/
- `guides/driveway-airport-proximity-faa-height-restrictions/index.html` → /guides/driveway-airport-proximity-faa-height-restrictions/
- `guides/driveway-alarm-systems-and-motion-sensors/index.html` → /guides/driveway-alarm-systems-and-motion-sensors/
- `guides/driveway-alexa-and-google-home-compatible-lights/index.html` → /guides/driveway-alexa-and-google-home-compatible-lights/
- `guides/driveway-algae-prevention-treatments-and-surface-options/index.html` → /guides/driveway-algae-prevention-treatments-and-surface-options/
- `guides/driveway-and-garage-floor-connection-seamless-design/index.html` → /guides/driveway-and-garage-floor-connection-seamless-design/
- `guides/driveway-and-landscaping-integration-cohesive-property-design/index.html` → /guides/driveway-and-landscaping-integration-cohesive-property-design/
- … and 462 more (see `hero-uniqueness-audit.json`)

### `/images/pexels-pixabay-221540.webp` — **253 pages**

- `guides/accessible-driveway-design-ada-considerations/index.html` → /guides/accessible-driveway-design-ada-considerations/
- `guides/acid-staining-a-concrete-driveway-unique-effects/index.html` → /guides/acid-staining-a-concrete-driveway-unique-effects/
- `guides/airbnb-driveway-requirements-parking-for-short-term-rentals/index.html` → /guides/airbnb-driveway-requirements-parking-for-short-term-rentals/
- `guides/ant-hill-prevention-in-paver-driveways/index.html` → /guides/ant-hill-prevention-in-paver-driveways/
- `guides/anti-ice-coatings-for-driveways/index.html` → /guides/anti-ice-coatings-for-driveways/
- `guides/apartment-complex-driveway-design/index.html` → /guides/apartment-complex-driveway-design/
- `guides/average-driveway-replacement-cost-by-material/index.html` → /guides/average-driveway-replacement-cost-by-material/
- `guides/basalt-driveway/index.html` → /guides/basalt-driveway/
- `guides/before-and-after-driveway-renovation-photo-gallery-ideas/index.html` → /guides/before-and-after-driveway-renovation-photo-gallery-ideas/
- `guides/best-asphalt-driveway-sealer-top-products-for-2026/index.html` → /guides/best-asphalt-driveway-sealer-top-products-for-2026/
- `guides/best-budget-driveway-for-clay-soil/index.html` → /guides/best-budget-driveway-for-clay-soil/
- `guides/best-budget-driveway-for-coastal-homes/index.html` → /guides/best-budget-driveway-for-coastal-homes/
- `guides/best-budget-driveway-for-sandy-soil/index.html` → /guides/best-budget-driveway-for-sandy-soil/
- `guides/best-concrete-driveway-sealer-penetrating-vs-film-forming/index.html` → /guides/best-concrete-driveway-sealer-penetrating-vs-film-forming/
- `guides/best-de-icing-products-for-driveways-salt-vs-chemical-vs-natural/index.html` → /guides/best-de-icing-products-for-driveways-salt-vs-chemical-vs-natural/
- … and 238 more (see `hero-uniqueness-audit.json`)

### `/images/pexels-goodcitizen-1315919.webp` — **75 pages**

- `guides/concrete-driveway-air-entrainment-freeze-thaw-protection/index.html` → /guides/concrete-driveway-air-entrainment-freeze-thaw-protection/
- `guides/concrete-driveway-color-hardener-application-and-benefits/index.html` → /guides/concrete-driveway-color-hardener-application-and-benefits/
- `guides/concrete-driveway-cost-in-alabama-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-alabama-2026-price-guide/
- `guides/concrete-driveway-cost-in-alaska-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-alaska-2026-price-guide/
- `guides/concrete-driveway-cost-in-arizona-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-arizona-2026-price-guide/
- `guides/concrete-driveway-cost-in-arkansas-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-arkansas-2026-price-guide/
- `guides/concrete-driveway-cost-in-california-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-california-2026-price-guide/
- `guides/concrete-driveway-cost-in-colorado-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-colorado-2026-price-guide/
- `guides/concrete-driveway-cost-in-connecticut-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-connecticut-2026-price-guide/
- `guides/concrete-driveway-cost-in-delaware-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-delaware-2026-price-guide/
- `guides/concrete-driveway-cost-in-florida-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-florida-2026-price-guide/
- `guides/concrete-driveway-cost-in-georgia-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-georgia-2026-price-guide/
- `guides/concrete-driveway-cost-in-hawaii-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-hawaii-2026-price-guide/
- `guides/concrete-driveway-cost-in-idaho-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-idaho-2026-price-guide/
- `guides/concrete-driveway-cost-in-illinois-2026-price-guide/index.html` → /guides/concrete-driveway-cost-in-illinois-2026-price-guide/
- … and 60 more (see `hero-uniqueness-audit.json`)

### `/images/pexels-introspectivedsgn-9890648.webp` — **62 pages**

- `guides/asphalt-compaction-tools-and-techniques/index.html` → /guides/asphalt-compaction-tools-and-techniques/
- `guides/asphalt-driveway-alligator-cracking-what-it-means-and-how-to-fix-it/index.html` → /guides/asphalt-driveway-alligator-cracking-what-it-means-and-how-to-fix-it/
- `guides/asphalt-driveway-cost-in-alabama-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-alabama-local-pricing/
- `guides/asphalt-driveway-cost-in-alaska-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-alaska-local-pricing/
- `guides/asphalt-driveway-cost-in-arizona-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-arizona-local-pricing/
- `guides/asphalt-driveway-cost-in-arkansas-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-arkansas-local-pricing/
- `guides/asphalt-driveway-cost-in-california-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-california-local-pricing/
- `guides/asphalt-driveway-cost-in-colorado-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-colorado-local-pricing/
- `guides/asphalt-driveway-cost-in-connecticut-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-connecticut-local-pricing/
- `guides/asphalt-driveway-cost-in-delaware-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-delaware-local-pricing/
- `guides/asphalt-driveway-cost-in-florida-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-florida-local-pricing/
- `guides/asphalt-driveway-cost-in-georgia-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-georgia-local-pricing/
- `guides/asphalt-driveway-cost-in-idaho-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-idaho-local-pricing/
- `guides/asphalt-driveway-cost-in-illinois-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-illinois-local-pricing/
- `guides/asphalt-driveway-cost-in-indiana-local-pricing/index.html` → /guides/asphalt-driveway-cost-in-indiana-local-pricing/
- … and 47 more (see `hero-uniqueness-audit.json`)

### `/images/pexels-artbovich-8134848.webp` — **60 pages**

- `guides/5-signs-your-driveway-needs-replacement/index.html` → /guides/5-signs-your-driveway-needs-replacement/
- `guides/annual-driveway-maintenance-costs-by-material-type/index.html` → /guides/annual-driveway-maintenance-costs-by-material-type/
- `guides/driveway-acoustic-emission-testing-crack-detection/index.html` → /guides/driveway-acoustic-emission-testing-crack-detection/
- `guides/driveway-annual-maintenance-cost-comparison-all-materials/index.html` → /guides/driveway-annual-maintenance-cost-comparison-all-materials/
- `guides/driveway-basics-types-costs-lifespan/index.html` → /guides/driveway-basics-types-costs-lifespan/
- `guides/driveway-bonded-concrete-overlay-thin-layer-resurfacing/index.html` → /guides/driveway-bonded-concrete-overlay-thin-layer-resurfacing/
- `guides/driveway-callback-repair-contractors-responsibility/index.html` → /guides/driveway-callback-repair-contractors-responsibility/
- `guides/driveway-cold-pour-crack-filler-diy-application-guide/index.html` → /guides/driveway-cold-pour-crack-filler-diy-application-guide/
- `guides/driveway-corrective-maintenance-planning-addressing-existing-issues/index.html` → /guides/driveway-corrective-maintenance-planning-addressing-existing-issues/
- `guides/driveway-crack-filler-best-products-reviewed-for-2026/index.html` → /guides/driveway-crack-filler-best-products-reviewed-for-2026/
- `guides/driveway-crack-filling-products-and-techniques/index.html` → /guides/driveway-crack-filling-products-and-techniques/
- `guides/driveway-crack-routing-preparing-for-sealant-application/index.html` → /guides/driveway-crack-routing-preparing-for-sealant-application/
- `guides/driveway-crack-sealing-vs-crack-filling-whats-different/index.html` → /guides/driveway-crack-sealing-vs-crack-filling-whats-different/
- `guides/driveway-damage-from-garbage-trucks-filing-for-repairs/index.html` → /guides/driveway-damage-from-garbage-trucks-filing-for-repairs/
- `guides/driveway-edge-crumbling-causes-and-repair-solutions/index.html` → /guides/driveway-edge-crumbling-causes-and-repair-solutions/
- … and 45 more (see `hero-uniqueness-audit.json`)

### `/images/pexels-sobeslavjan-13838908.webp` — **30 pages**

- `guides/best-budget-driveway-material-for-heavy-snow-regions/index.html` → /guides/best-budget-driveway-material-for-heavy-snow-regions/
- `guides/best-budget-driveway-material-for-hot-climates/index.html` → /guides/best-budget-driveway-material-for-hot-climates/
- `guides/best-driveway-for-desert-heat-and-sun-exposure/index.html` → /guides/best-driveway-for-desert-heat-and-sun-exposure/
- `guides/best-driveway-for-rainy-and-wet-climates/index.html` → /guides/best-driveway-for-rainy-and-wet-climates/
- `guides/best-driveway-material-for-heavy-snow-regions-longevity-focus/index.html` → /guides/best-driveway-material-for-heavy-snow-regions-longevity-focus/
- `guides/best-driveway-material-for-hot-climates-longevity-focus/index.html` → /guides/best-driveway-material-for-hot-climates-longevity-focus/
- `guides/cold-climates-best-driveway-materials-for-michigan/index.html` → /guides/cold-climates-best-driveway-materials-for-michigan/
- `guides/cold-climates-best-driveway-materials-for-minnesota/index.html` → /guides/cold-climates-best-driveway-materials-for-minnesota/
- `guides/cold-climates-best-driveway-materials-for-new-york/index.html` → /guides/cold-climates-best-driveway-materials-for-new-york/
- `guides/cold-climates-best-driveway-materials-for-wisconsin/index.html` → /guides/cold-climates-best-driveway-materials-for-wisconsin/
- `guides/desert-driveways-new-mexico-and-arizona-tips/index.html` → /guides/desert-driveways-new-mexico-and-arizona-tips/
- `guides/driveway-climate-adaptation-strategy-building-for-future-conditions/index.html` → /guides/driveway-climate-adaptation-strategy-building-for-future-conditions/
- `guides/driveway-concrete-vs-asphalt-in-your-climate-zone/index.html` → /guides/driveway-concrete-vs-asphalt-in-your-climate-zone/
- `guides/driveway-for-climate-zone-1-extreme-cold-materials/index.html` → /guides/driveway-for-climate-zone-1-extreme-cold-materials/
- `guides/driveway-for-climate-zone-2-cold-winter-materials/index.html` → /guides/driveway-for-climate-zone-2-cold-winter-materials/
- … and 15 more (see `hero-uniqueness-audit.json`)

### `/images/matt-jones-xpDHTc-pkog-unsplash.webp` — **9 pages**

- `guides/best-driveway-luxury-homes/index.html` → /guides/best-driveway-luxury-homes/
- `guides/black-driveway-vs-light-driveway-heat-absorption-and-curb-appeal/index.html` → /guides/black-driveway-vs-light-driveway-heat-absorption-and-curb-appeal/
- `guides/decorative-concrete-driveway-ideas-and-costs/index.html` → /guides/decorative-concrete-driveway-ideas-and-costs/
- `guides/driveway-curb-appeal-for-selling-your-home/index.html` → /guides/driveway-curb-appeal-for-selling-your-home/
- `guides/driveway-polymer-overlay-decorative-and-protective/index.html` → /guides/driveway-polymer-overlay-decorative-and-protective/
- `guides/driveway-stamped-overlay-adding-decorative-patterns/index.html` → /guides/driveway-stamped-overlay-adding-decorative-patterns/
- `guides/first-impressions-driveway-design-for-curb-appeal/index.html` → /guides/first-impressions-driveway-design-for-curb-appeal/
- `guides/modern-home-driveways-contemporary-design-ideas/index.html` → /guides/modern-home-driveways-contemporary-design-ideas/
- `guides/real-estate-staging-driveway-curb-appeal-tips/index.html` → /guides/real-estate-staging-driveway-curb-appeal-tips/

### `/images/pexels-pixabay-277667.webp` — **8 pages**

- `guides/crushed-concrete-driveways-budget-friendly-option/index.html` → /guides/crushed-concrete-driveways-budget-friendly-option/
- `guides/crushed-granite-driveways-installation-and-care/index.html` → /guides/crushed-granite-driveways-installation-and-care/
- `guides/crushed-limestone-base-for-driveways-benefits-and-installation/index.html` → /guides/crushed-limestone-base-for-driveways-benefits-and-installation/
- `guides/gravel-driveway-cost-per-square-foot-guide/index.html` → /guides/gravel-driveway-cost-per-square-foot-guide/
- `guides/gravel-driveway-installation-step-by-step-guide/index.html` → /guides/gravel-driveway-installation-step-by-step-guide/
- `guides/gravel-driveway-lifespan-how-long-before-you-need-to-refresh/index.html` → /guides/gravel-driveway-lifespan-how-long-before-you-need-to-refresh/
- `guides/gravel-driveway-maintenance-raking-grading-and-refilling/index.html` → /guides/gravel-driveway-maintenance-raking-grading-and-refilling/
- `guides/gravel-vs-paved-driveway-which-is-right-for-you/index.html` → /guides/gravel-vs-paved-driveway-which-is-right-for-you/

### `/images/pexels-curtis-adams-1694007-3958961.webp` — **7 pages**

- `guides/brick-driveway-installation-and-maintenance/index.html` → /guides/brick-driveway-installation-and-maintenance/
- `guides/cobblestone-driveway-traditional-style-guide/index.html` → /guides/cobblestone-driveway-traditional-style-guide/
- `guides/paver-base-material-selection-guide/index.html` → /guides/paver-base-material-selection-guide/
- `guides/paver-driveway-cost-per-square-foot-guide/index.html` → /guides/paver-driveway-cost-per-square-foot-guide/
- `guides/paver-driveway-installation-step-by-step-guide/index.html` → /guides/paver-driveway-installation-step-by-step-guide/
- `guides/paver-driveway-lifespan-what-to-expect-over-30-years/index.html` → /guides/paver-driveway-lifespan-what-to-expect-over-30-years/
- `guides/paver-sealing-pros-cons-and-best-practices/index.html` → /guides/paver-sealing-pros-cons-and-best-practices/

### `/images/pexels-introspectivedsgn-7475608.webp` — **7 pages**

- `guides/chip-seal-driveway/index.html` → /guides/chip-seal-driveway/
- `guides/chip-seal-driveways-costs-and-longevity/index.html` → /guides/chip-seal-driveways-costs-and-longevity/
- `guides/exposed-aggregate-concrete-driveway-guide/index.html` → /guides/exposed-aggregate-concrete-driveway-guide/
- `guides/permeable-vs-standard-driveways-environmental-impact/index.html` → /guides/permeable-vs-standard-driveways-environmental-impact/
- `guides/permeable-vs-traditional-driveways-pros-cons-and-costs/index.html` → /guides/permeable-vs-traditional-driveways-pros-cons-and-costs/
- `guides/resin-bound-driveway-cost-per-square-foot-guide/index.html` → /guides/resin-bound-driveway-cost-per-square-foot-guide/
- `guides/resin-vs-block-paving-driveway-a-full-comparison/index.html` → /guides/resin-vs-block-paving-driveway-a-full-comparison/

### `/images/hugo-sousa-BghGseQbAkA-unsplash.webp` — **6 pages**

- `guides/driveway-cost-plus-contract-transparent-pricing-model/index.html` → /guides/driveway-cost-plus-contract-transparent-pricing-model/
- `guides/driveway-time-and-materials-contract-flexible-pricing/index.html` → /guides/driveway-time-and-materials-contract-flexible-pricing/
- `guides/how-much-does-a-new-driveway-cost-in-2026/index.html` → /guides/how-much-does-a-new-driveway-cost-in-2026/
- `guides/large-driveway-cost-pricing-for-1000-square-feet/index.html` → /guides/large-driveway-cost-pricing-for-1000-square-feet/
- `guides/seasonal-pricing-for-driveway-projects/index.html` → /guides/seasonal-pricing-for-driveway-projects/
- `guides/why-driveway-quotes-vary-so-much-understanding-pricing-factors/index.html` → /guides/why-driveway-quotes-vary-so-much-understanding-pricing-factors/

### `/hero-driveway-640.jpg` — **5 pages**

- `cost-calculator/index.html` → /cost-calculator/
- `for-contractors/index.html` → /for-contractors/
- `for-homeowners-quiz/index.html` → /for-homeowners-quiz/
- `thank-you-contractor/index.html` → /thank-you-contractor/
- `thank-you-homeowner/index.html` → /thank-you-homeowner/

## All duplicate images (2+ pages)

- `/images/pexels-curtis-adams-1694007-3990589.webp` — 477 pages
- `/images/pexels-pixabay-221540.webp` — 253 pages
- `/images/pexels-goodcitizen-1315919.webp` — 75 pages
- `/images/pexels-introspectivedsgn-9890648.webp` — 62 pages
- `/images/pexels-artbovich-8134848.webp` — 60 pages
- `/images/pexels-sobeslavjan-13838908.webp` — 30 pages
- `/images/matt-jones-xpDHTc-pkog-unsplash.webp` — 9 pages
- `/images/pexels-pixabay-277667.webp` — 8 pages
- `/images/pexels-curtis-adams-1694007-3958961.webp` — 7 pages
- `/images/pexels-introspectivedsgn-7475608.webp` — 7 pages
- `/images/hugo-sousa-BghGseQbAkA-unsplash.webp` — 6 pages
- `/hero-driveway-640.jpg` — 5 pages

## Pages missing hero images

- `privacy-policy/index.html`

## Guide slug mismatches (sample)

Guides using a stock/shared image instead of a dedicated `hero-{slug}.webp` file.

- `guides/5-signs-your-driveway-needs-replacement/index.html`
  - Current: `/images/pexels-artbovich-8134848.webp`
  - Expected: `/images/hero-5-signs-your-driveway-needs-replacement.webp`
- `guides/accessible-driveway-design-ada-considerations/index.html`
  - Current: `/images/pexels-pixabay-221540.webp`
  - Expected: `/images/hero-accessible-driveway-design-ada-considerations.webp`
- `guides/acid-staining-a-concrete-driveway-unique-effects/index.html`
  - Current: `/images/pexels-pixabay-221540.webp`
  - Expected: `/images/hero-acid-staining-a-concrete-driveway-unique-effects.webp`
- `guides/airbnb-driveway-requirements-parking-for-short-term-rentals/index.html`
  - Current: `/images/pexels-pixabay-221540.webp`
  - Expected: `/images/hero-airbnb-driveway-requirements-parking-for-short-term-rentals.webp`
- `guides/annual-driveway-maintenance-costs-by-material-type/index.html`
  - Current: `/images/pexels-artbovich-8134848.webp`
  - Expected: `/images/hero-annual-driveway-maintenance-costs-by-material-type.webp`
- `guides/ant-hill-prevention-in-paver-driveways/index.html`
  - Current: `/images/pexels-pixabay-221540.webp`
  - Expected: `/images/hero-ant-hill-prevention-in-paver-driveways.webp`
- `guides/anti-ice-coatings-for-driveways/index.html`
  - Current: `/images/pexels-pixabay-221540.webp`
  - Expected: `/images/hero-anti-ice-coatings-for-driveways.webp`
- `guides/apartment-complex-driveway-design/index.html`
  - Current: `/images/pexels-pixabay-221540.webp`
  - Expected: `/images/hero-apartment-complex-driveway-design.webp`
- `guides/asphalt-compaction-tools-and-techniques/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-compaction-tools-and-techniques.webp`
- `guides/asphalt-driveway-alligator-cracking-what-it-means-and-how-to-fix-it/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-alligator-cracking-what-it-means-and-how-to-fix-it.webp`
- `guides/asphalt-driveway-cost-in-alabama-local-pricing/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-cost-in-alabama-local-pricing.webp`
- `guides/asphalt-driveway-cost-in-alaska-local-pricing/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-cost-in-alaska-local-pricing.webp`
- `guides/asphalt-driveway-cost-in-arizona-local-pricing/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-cost-in-arizona-local-pricing.webp`
- `guides/asphalt-driveway-cost-in-arkansas-local-pricing/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-cost-in-arkansas-local-pricing.webp`
- `guides/asphalt-driveway-cost-in-california-local-pricing/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-cost-in-california-local-pricing.webp`
- `guides/asphalt-driveway-cost-in-colorado-local-pricing/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-cost-in-colorado-local-pricing.webp`
- `guides/asphalt-driveway-cost-in-connecticut-local-pricing/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-cost-in-connecticut-local-pricing.webp`
- `guides/asphalt-driveway-cost-in-delaware-local-pricing/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-cost-in-delaware-local-pricing.webp`
- `guides/asphalt-driveway-cost-in-florida-local-pricing/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-cost-in-florida-local-pricing.webp`
- `guides/asphalt-driveway-cost-in-georgia-local-pricing/index.html`
  - Current: `/images/pexels-introspectivedsgn-9890648.webp`
  - Expected: `/images/hero-asphalt-driveway-cost-in-georgia-local-pricing.webp`
- … and 981 more

## Next steps

1. Run `python3 scripts/audit_hero_uniqueness.py` after any hero image changes.
2. For each high-priority duplicate cluster, source or generate a unique image per page.
3. Name new guide images `hero-{slug}.webp` and place in `/images/`.
4. Update `.guide-hero` CSS `background-image` and `<img class="guide-hero-img">` together.
5. Re-run until `duplicate_image_count` is limited to intentional shared pages only.

## Related scripts

- `scripts/hero_audit.py` — finds gradient-only heroes (no photo at all)
- `scripts/build_hero_image_map.py` — keyword map for sourcing missing images
- `scripts/add-hero-img.js` — inserts crawlable `<img>` tags into guide heroes
