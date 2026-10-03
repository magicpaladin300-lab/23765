# Operating conventions on top of PALIMPSEST RUBRIC v1.0

Status key: LOCKED = in the rubric; PROPOSED = awaiting the user's ruling (used as default until overruled).

| # | Convention | Status |
|---|---|---|
| C1 | **Floor interpolation.** Piecewise-linear over McEvedy & Jones' published anchors plus the rubric table's explicit points (160M at 1 CE, 185M plague trough c. 550, 350M at 1450, 5M at 4500 BCE, 9M at 3300 BCE), taking the lower where they differ; Maddison/UN anchors from 1870 on, as the table itself does. Implemented in `palimpsest.py`. | PROPOSED |
| C2 | **Deep floors with citation** (rubric: "Going below the floor requires a citation"). Deevey 1960: 133M at 1 CE. Biraben 1979: 226M / 254M / 301M at 900 / 1000 / 1100 (below M&J's 240 / 265 / 320; confirmed against the Census Bureau comparison table via search). Willcox 1931: 470M (1650), 694M (1750), 1,091M (1850), 1,571M (1900) — NOT yet verified against the printed table from this sandbox; flag until checked. Used only when they help, with the citation in the unit file. | PROPOSED |
| C3 | **Polygon choice.** If the user names a modern unit, use it. If the user names a city or region, take the smallest official county-tier polygon (US county / NUTS-3 / ADM2; for China prefer the ADM2 prefecture only when the historic core is not contained in a single county-level district) that contains the historic core. Flag polygons over ~10,000 km² or ~10M residents as boundary smearing. | PROPOSED |
| C4 | **Open-top band extension.** Above band 10 continue at ×1.8 steps: 11 ≥0.16%, 12 ≥0.29%, 13 ≥0.52%, 14 ≥0.94%, 15 ≥1.7%, 16 ≥3.1%. Reported as "10 (ext N)"; the official ladder is unchanged. | PROPOSED |
| C5 | **Contemporary GDP basis.** Nominal USD or PPP, whichever maximizes, with numerator and denominator on the same basis and the same year; flag the basis. Local statistical-yearbook figures are admissible numerators; the denominator is the lowest published vintage for that year. | PROPOSED |
| C6 | **Pre-1820 multiplier stacking.** GDP multiplier = documented regional per-capita ratio to world (Maddison) × role premium from the rubric schedule. Anything above 2.5× still needs Ruling A/B documentation (ledgers, registered output). | PROPOSED |
| C7 | **Physical veto ceilings.** Built-up density ≤ ~600 persons/ha for single-storey premodern cities, ≤ ~1,000/ha where multi-storey housing is attested (Rome's insulae, Fustat, Edo chōnin wards); hinterland at attested yields plus documented imports; survey and necropolis evidence override texts. Record every kill. | LOCKED (ceilings PROPOSED) |
| C8 | **Transient populations** (pilgrims, daytime commuters, fairs, garrisons on campaign) are metadata, never the share. | PROPOSED |
| C9 | **Reporting.** Same-year rule for numerator and denominator; ranges before 1500; delta (lawyered ÷ consensus) reported and never capped, with a "thin lawyering" note when it exceeds 3×. | LOCKED |
| C10 | **Record keeping.** Each finalized unit gets `units/<slug>.md` in the output schema and a row in `GALLERY.md`, committed to the branch. | PROPOSED |
