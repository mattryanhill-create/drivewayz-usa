# Initiative 1B — BreadcrumbList Audit (Locations)

**Crawl:** Lumar 7508639 · 28 June 2026

## Results

| Check | Result |
|-------|--------|
| Locations with BreadcrumbList | **56 / 57** state pages |
| Missing BreadcrumbList | `locations/state-page/index.html` (template stub, not live) |
| ListItem count | PASS — 3 items on all live pages |
| Positions 1, 2, 3 (1-indexed) | PASS |
| Pos 1: Home → `https://drivewayzusa.co/` | PASS |
| Pos 2: Locations → `https://drivewayzusa.co/locations/` | PASS |
| Pos 3: State name | PASS (dynamic) |
| Pos 3 `item` URL | **Note:** omitted on all location pages (name only) |

## Spot-check (pos 3)

- `/locations/alabama/` → Alabama
- `/locations/alaska/` → Alaska
- `/locations/american-samoa/` → American Samoa

## Reference template (for guides rollout)

Guides use the same 3-level structure with pos 3 including canonical `item` URL:

```json
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {"@type":"ListItem","position":1,"name":"Home","item":"https://drivewayzusa.co/"},
  {"@type":"ListItem","position":2,"name":"Guides Hub","item":"https://drivewayzusa.co/guides-hub/"},
  {"@type":"ListItem","position":3,"name":"[Page Title]","item":"[Canonical URL]"}
]}
```

## Initiative 1A status

- **1,021 / 1,021** guide pages now have BreadcrumbList JSON-LD in `<head>`.
- Pilot pages verified: gravel-pothole-repair, tar-and-chip, percolation-test, asphalt-rejuvenator, resurfacing-vs-replacement.
