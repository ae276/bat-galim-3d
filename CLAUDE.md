# Bat Galim 3D model – maintainer notes

- Live site: GitHub Pages from `main` / root → https://ae276.github.io/bat-galim-3d/ (embed via `embed.js`).
- `index.html` is GENERATED. Never hand-edit it: change `src/` and rebuild:
  `cd src && python3 gen3.py && python3 build_unified.py` (needs `pip install shapely pyproj --break-system-packages`).
- `src/template.html` (desktop) and `src/template_m.html` (phone) hold the UI; `__DATA__` is replaced with `src/data.json`.
  `build_unified.py` packs both into one page that picks the layout by device (phone / narrow / coarse-pointer <1000px → phone),
  re-picks on resize, honours `?view=d|m`, and exposes `window.__bgSwitch(k)` for the manual switch buttons (`#lay-sw`).
- Plans/massing: `gen2.py` (Bat Galim plans), `gen3.py` (Rambam, waterfront, institutions via `inst_part.py`).
  Encoded inputs (`*.txt`) come from XPLAN, OSM and data.gov.il; see the `neighborhood-3d-plans-model` skill for how to refetch.
- Before pushing: `node --check` the extracted last `<script>` of each template, and screenshot with playwright-core
  (three.js routed from a local `npm i three@0.128.0`) at 1400×850 and 390×844 (isMobile) to confirm no `pageerror`.
- UI text is Hebrew, RTL. Mark estimated volumes as "משוער"; cite sources in plan cards.
