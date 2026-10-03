# Du Bois D3 Gallery — Custom Page

A companion to the Vega-Lite gallery in this repo: **178 D3 visualizations in a single
Databricks AI/BI [Custom Page](https://docs.databricks.com/aws/en/dashboards/)** — charts,
interactions, animations, and generative-art simulations — all themed with the Du Bois
design-system palette.

Where the main gallery renders native + custom-Vega widgets in a grid, this is **one
custom-page widget** running author-written **React + D3**, so it supports real
interactivity (hover, zoom, drag, click-to-expand) and live animation while staying a
governed AI/BI dashboard (one `.lvdash` spec; versions / publishes / shares like any other).

## Contents

| Path | Description |
|------|-------------|
| `build_custom_page.py` | Self-contained build + deploy. Embeds the full React/D3 source and the 14-section tile registry; creates + publishes the dashboard. |
| `deploy_custom_page.py` | Tiny vendored Lakeview REST helper (`custom_page_widget`, `deploy`) — no external dependencies beyond the Databricks CLI. |

## The 178 tiles — 14 sections

Distribution · Correlation · Ranking · Part of a whole · Grouped & stacked bars ·
Evolution (time series) · Hierarchy · Flow & network · Gauges & radial · Time & calendar ·
Interaction · Animation & algorithms · Scales, color & text · **Generative art & simulation** (32)

The generative section is the showpiece: Fourier epicycles, double pendulum, boids,
Conway's Game of Life, reaction-diffusion (Turing patterns), Mandelbrot & animated Julia
sets, Barnsley fern, Perlin terrain, Hilbert curve, Lorenz/Clifford/De Jong attractors,
Langton's ant, n-body orbits, and more.

## Prerequisites

1. **The workspace preview "Custom pages in AI/BI dashboards" must be ENABLED.** This is a
   Private Preview — enable it on the workspace *Previews* page (FEVM: post your workspace
   id in `#feature-preview-discuss`; customer workspaces: nominate via the SFDC Preview
   Portal). Without it the page renders blank.
2. Databricks CLI authenticated to a profile, and a SQL warehouse id.

## Install

As part of the repo's one-command installer (adds this on top of the Vega-Lite dashboards):

```bash
./install.sh --profile <cli-profile> --with-custom-page
```

Or standalone (no data generation needed — all tile data is synthetic / self-contained):

```bash
cd custom_page
python3 build_custom_page.py --profile <cli-profile> --warehouse <warehouse-id>
```

Options: `--parent-path /Users/you` (workspace folder; default = your home),
`--name "..."` (dashboard display name). Re-running is **idempotent** — it adopts and
updates the same-named dashboard in place.

## Notes & constraints

- **Core d3 only.** The custom-page sandbox ships a curated `d3@7` build. Stripped modules
  (verified): `d3-geo`, `d3-brush`, `d3-quadtree`, `d3-ease`, `d3-polygon`, `d3-dsv`, and
  top-level `d3-timer` (`d3.interval`/`timer`/`timeout`). All tiles here avoid those — maps
  use the native `symbol-map`/`choropleth-map` widgets in the main gallery instead.
- **Animations use `setInterval` / `requestAnimationFrame`** and each returns a cleanup fn;
  heavy point clouds (Barnsley, De Jong) render as path strings rather than thousands of
  SVG nodes.
- All 178 tiles render against real `d3@7` without throwing (headless-verified), and the
  deployed page was visually QA'd end-to-end.
