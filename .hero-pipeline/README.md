# Hero Image Pipeline

Locally reproducible pipeline that produced 1,009 unique AI-rendered
hero images for drivewayzusa.co guide pages in July 2026.

## Overview

Before this pipeline, 255 guide pages shared the same pexels-pixabay
hero image, and 1,002 pages had broken JSON-LD image schema pointing
at nonexistent files. This pipeline generated unique heroes per page
using Flux 1.1 Pro on Replicate and swapped them in via automated
regex-based HTML rewriting.

## Files

### Input data
- `pages_with_piles.csv` — 1,019 rows, one per guide page. Contains
  current hero filename, GSC impressions, and pile assignment
  (A=priority, B=bulk, D=already unique, E=missing).
- `job2_output_final.json` — 1,009 records from Moonshot Kimi
  containing per-page image generation prompts (subject, material,
  setting, condition, lighting, angle) + intended filenames +
  intended alt text.

### Manifests
- `render_manifest.csv` — 1,009 rows joining pile data with Kimi's
  prompts. Built by `build_render_manifest.py`. Sorted pile A first
  (highest impressions) then pile B alphabetical.

### Render scripts (Phase 2)
- `render_pilot.py` — Renders 8 pile A images. Used to validate
  Flux 1.1 Pro before scaling.
- `render_bulk.py` — Renders all 1,009 images. Idempotent
  (skips existing files). Retries on Replicate throttles.

### Logs
- `pilot_log.csv` — Timestamps, costs, times for pilot 8 renders.
- `bulk_log.csv` — Same for full 1,009 renders. Total spend ~$40.42.
- `swap_log.csv` — HTML swap results from Phase 3b (990 swapped,
  19 skipped as gradient-hero pages).
- `swap_log_stage3b.csv` — Backup of the earlier partial swap log.
- `warnings.csv` — Pages where inline CSS url() couldn't be swapped
  (1 row: basalt-driveway, which has no inline CSS url).
- `skipped_pages.csv` — 19 pages skipped (no <img class="guide-hero-img">
  found; these use gradient heroes).

### Deployment scripts (Phase 3b)
- `swap_heroes.py` — Swaps hero <img> src+alt, JSON-LD image field,
  and inline CSS url() on every applicable guide page. Idempotent
  via already_swapped detection.

### Reference files
- `DO_NOT_TOUCH.txt` — Protect-list for pages the pipeline must not
  modify (homepage, top-level pages, pile D). Used for planning;
  runtime enforcement is via the pile-A-or-B filter in swap_heroes.py.
- `skipped_slugs_gradient_hero.txt` — The 19 gradient-hero page
  slugs, extracted for Phase 5d follow-up work.

## Regenerating from scratch

1. Run `build_render_manifest.py` to produce `render_manifest.csv`.
2. Set REPLICATE_API_TOKEN, run `render_bulk.py` to produce
   `renders/*.webp` (~$40 on Flux 1.1 Pro).
3. Move renders to `/images/heroes/` in the repo root.
4. Run `swap_heroes.py --dry-run` to preview HTML changes.
5. Run `swap_heroes.py` to apply.
6. Commit and push. Cloudflare Pages deploys automatically.

## Costs

- Kimi (Moonshot AI): free (used within a Kimi session, no direct cost)
- Flux 1.1 Pro via Replicate: $40.42 (1,009 images × $0.04)
- Perplexity Comet coordination: covered by subscription

## Known deferred work

- 19 gradient-hero pages need proper <img> markup added (Phase 5d).
- ~5% of rendered images contain visible people (negative-prompt
  violation Flux ignored). Automated re-render sweep pending.
