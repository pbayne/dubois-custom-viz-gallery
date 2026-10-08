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
| `examples/example_live_data.py` | **D3 bound to LIVE Unity Catalog data** (not synthetic) — see below. |

## Example: D3 on live, governed data

The 178-tile gallery uses synthetic data to showcase D3 *technique*. The real payoff of a
custom page (vs. a standalone D3 app) is rendering D3 — and native widgets — from **live,
UC-governed SQL queries**. `examples/example_live_data.py` demonstrates it against the
built-in `samples.bakehouse` catalog:

- `viz.Value` → a KPI bound to `SUM(totalPrice)`
- `viz.CustomWidget` → a D3 bar chart drawn from a "revenue by product" query

```bash
cd custom_page/examples
python3 example_live_data.py --profile <cli-profile> --warehouse <id>
```

Verified rendering (Oct 2026): KPI = **66,471**; bars labeled with the real
top products (Golden Gate Ginger, Outback Oatmeal, …).

> **Gotcha worth knowing:** `viz.CustomWidget` **requires a `schema` prop**
> (`schema:{fields:[{name,type},…]}`). Omit it and the whole page crashes with *"Custom Page
> sandbox failed to render … Cannot convert undefined or null to object."* `viz.Value` needs
> no schema. Query rows arrive at `render(config, data)` as `data.main.rows` (array-of-arrays,
> column order). The dashboard carries the SQL as `datasets`; a `datasetMap` maps an alias →
> datasetId, and each `viz.*` query references the alias via `datasetName`.

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
