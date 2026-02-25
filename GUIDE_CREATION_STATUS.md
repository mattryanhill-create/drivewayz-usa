# Guide Creation Status

## Completed (7 guides)
All with cobblestone structure: navbar, footer, tab nav, 2-column layout, sidebar (Quick Facts, CTA form, Related Guides), 8+ FAQ accordion.

1. **driveway-base-subgrade.html** – Earth Brown theme, from 04_driveway_base_subgrade.md
2. **driveway-excavation-grading.html** – Construction Orange, from 15_driveway_excavation_grading.md
3. **driveway-reinforcement.html** – Steel Blue, from 16_driveway_reinforcement.md
4. **driveway-sealing.html** – Dark Charcoal, from 12_driveway_sealing.md
5. **driveway-slope-drainage.html** – Water Blue, from 05_driveway_slope_drainage.md
6. **gravel-pothole-repair.html** – Natural Stone theme, FAQ tab added (no .md)
7. *(driveway-thickness-guide through when-can-you-drive – see below)*

## Remaining (9 guides)
These need conversion to cobblestone structure (tabs, sidebar, 8+ FAQ):

- driveway-thickness-guide.html – Concrete Gray, 03 .md
- driveway-weight-limits.html – Heavy Red, 13 .md
- expansion-control-joints.html – Technical Purple, 10 .md
- how-long-driveway-last.html – Forest Green, 08 .md
- oyster-shell-driveway.html – Coastal Pearl (no .md)
- permeable-vs-traditional.html – Eco Green, 06 .md
- recycled-glass-driveway.html – Jewel Teal (no .md)
- resurfacing-vs-replacement.html – Decision Orange, 14 .md
- standard-driveway-dimensions.html – Blueprint Blue, 02 .md
- when-can-you-drive.html – Caution Yellow, 09 .md

## Template Reference
Use driveway-base-subgrade.html or driveway-sealing.html as the template. Key elements:
- Same navbar from cobblestone
- Tab nav with Overview + 2–4 topic tabs + FAQ tab
- guide-content-wrapper: guide-main + guide-sidebar
- Sidebar: Quick Facts card, CTA form card, Related Guides card (2–3 links using ./filename.html)
- 8+ FAQ accordion items in FAQ tab
- Theme colors in :root
