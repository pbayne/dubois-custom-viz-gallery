# Architecture

## Custom Viz (`custom-vega-viz`) widget shape

AI/BI dashboards store a Custom Viz (Vega-Lite) widget in the dashboard's
serialized JSON (`lvdash.json`) like this. This shape was reverse-engineered and
verified by rendering (the widget type is `custom-vega-viz`, spec `version` 1):

```jsonc
{
  "name": "<widget-name>",
  "queries": [{
    "name": "main_query",
    "query": {
      "datasetName": "<dataset name>",
      "fields": [{ "name": "colA", "expression": "`colA`" }, ...],
      "disaggregated": true
    }
  }],
  "spec": {
    "version": 1,
    "widgetType": "custom-vega-viz",
    "jsonSpec": { "type": "vega-lite", "spec": "<STRINGIFIED Vega-Lite JSON>" },
    "frame": { "title": "...", "showTitle": true },
    "encodings": { "fields": [{ "fieldName": "colA" }, ...] },
    "data": { "queryName": "main_query" }
  }
}
```

Rules that make it render:
- The Vega-Lite spec reads rows via `{"data": {"name": "databricks_query"}}`.
- Every column the spec references must appear in BOTH `queries[].query.fields`
  (as a backtick expression, with `disaggregated: true`) AND
  `spec.encodings.fields[].fieldName`.
- Use `"width": "container"`, `"height": "container"`.
- The Lakeview API accepts almost any widget JSON without complaint, so **"it
  saved" ≠ "it renders"** — always verify by rendering the dashboard.

## Datasets

Each chart's dataset is a SQL query over a table in `pb_demo.custom_gallery`. The
Vega-Lite gallery reuses a small set of canonical datasets, so ~15 generated
tables back the entire gallery.

## Build pipeline

`build/build_dashboard.py`:
1. reads every spec in `specs/<category>/*.json` (+ a per-spec sidecar mapping
   dataset name, SQL, fields, title),
2. builds datasets + `custom-vega-viz` widgets, laid out on one page per category,
3. `PATCH`es the dashboard via `/api/2.0/lakeview/dashboards/<id>` (etag-guarded)
   or creates it, then publishes with embedded credentials.

## Native `choropleth-map` widget (filled maps)

Custom-viz Vega-Lite `geoshape` does not fill polygons in the AI/BI sandbox (it
renders a degenerate rectangle / nothing). Filled choropleths therefore use AI/BI's
**native** map widget instead of a Vega spec:

```jsonc
{
  "name": "w_map_ca_choropleth",
  "queries": [{ "name": "main_query", "query": {
    "datasetName": "<ds>",
    "fields": [
      { "name": "value",   "expression": "`value`" },
      { "name": "name",    "expression": "`name`" },
      { "name": "geojson", "expression": "`geojson`" }   // GeoJSON geometry as text
    ],
    "disaggregated": true }}],
  "spec": {
    "version": 1,
    "widgetType": "choropleth-map",
    "encodings": {
      "color":  { "fieldName": "value", "scale": { "type": "quantitative",
                  "colorRamp": { "mode": "scheme", "scheme": "blues" } } },
      "extra":  [{ "fieldName": "name" }],               // tooltip fields
      "region": { "regionType": "custom", "fieldName": "geojson" }
    },
    "mark": { "opacity": 0.85 },
    "frame": { "title": "…", "showTitle": true }
  }
}
```

The geometry lives in a table column as GeoJSON text (see
`data_generation/10_generate_geo_tables.py`). In the spec library these charts set
`"native": {...}` + `"query_fields": [...]`; the build emits the widget verbatim
(no Vega wrapping, no injected config). The `albersUsa` point projection also works
fine inside a normal `custom-vega-viz` (that's how Gallery II's point maps are done),
but there is a native point-map widget too — see `symbol-map` below.

## Native `box` and `symbol-map` widgets (non-obvious schemas)

Most native widgets take plain `x`/`y`/`color` encodings over raw rows
(`disaggregated: true`). Two do not, and were confirmed from the AI/BI
visualization editor:

**`box`** (version 3) — the y channel is *five* box-stat sub-encodings, each bound
to an **aggregation** query field, and the query is **aggregated**
(`disaggregated: false`):

```jsonc
"query": { "fields": [
  { "name": "cylinders",  "expression": "`cylinders`" },
  { "name": "min(hp)",    "expression": "MIN(`hp`)" },
  { "name": "q1(hp)",     "expression": "PERCENTILE(`hp`, 0.25)" },
  { "name": "median(hp)", "expression": "MEDIAN(`hp`)" },
  { "name": "q3(hp)",     "expression": "PERCENTILE(`hp`, 0.75)" },
  { "name": "max(hp)",    "expression": "MAX(`hp`)" } ],
  "disaggregated": false }
"spec": { "version": 3, "widgetType": "box", "encodings": {
  "x": { "fieldName": "cylinders", "scale": { "type": "categorical" } },
  "y": { "whiskerStart": { "fieldName": "min(hp)" },
         "boxStart":     { "fieldName": "q1(hp)" },
         "boxMid":       { "fieldName": "median(hp)" },
         "boxEnd":       { "fieldName": "q3(hp)" },
         "whiskerEnd":   { "fieldName": "max(hp)" },
         "scale": { "type": "quantitative" } } } }
```

**`symbol-map`** (version 2) — markers are placed by a single `coordinates`
encoding (NOT bare `latitude`/`longitude` channels — those render "no fields
selected"):

```jsonc
"spec": { "version": 2, "widgetType": "symbol-map",
  "mark": { "opacity": 0.8, "size": 0 },
  "encodings": {
    "coordinates": { "coordinateType": "longitude-latitude",
                     "latitude":  { "fieldName": "latitude" },
                     "longitude": { "fieldName": "longitude" } },
    "color": { "fieldName": "state", "scale": { "type": "categorical" } },
    "extra": [{ "fieldName": "city" }, { "fieldName": "state" }] } }
```

The build supports the aggregated case via a per-chart `"disaggregated": False`
flag, and `NATIVE_VERSION` pins `symbol-map` to version 2.

## Flow / hierarchy / specialized native types

Seven more native types, each with a bespoke encoding shape (confirmed from the
AI/BI viz editor). Versions: sankey / gantt / combo / forecast-line = 1; funnel /
waterfall / pivot = 3. Aggregating ones use `disaggregated: false`.

```jsonc
// sankey  — nodes via stages[], plus a value measure
"encodings": { "value": { "fieldName": "sum(value)" },
               "stages": [{ "fieldName": "source" }, { "fieldName": "target" }] }
// gantt   — rows[] + a temporal range{start,end} (raw rows, disaggregated:true)
"encodings": { "rows": [{ "fieldName": "task" }],
               "range": { "scale": { "type": "temporal" },
                          "start": { "fieldName": "start_date" },
                          "end":   { "fieldName": "end_date" } } }
// funnel  — quantitative x, categorical y sorted by a measure
"encodings": { "x": { "fieldName": "sum(value)", "scale": { "type": "quantitative" } },
               "y": { "fieldName": "stage", "scale": { "type": "categorical",
                      "sort": { "by": "measure", "measure": { "fieldName": "sum(step)" } } } } }
// waterfall — categorical x sorted by a measure, quantitative delta y
"encodings": { "x": { "fieldName": "category", "scale": { "type": "categorical",
                      "sort": { "by": "measure", "measure": { "fieldName": "sum(ord)" } } } },
               "y": { "fieldName": "sum(delta)", "scale": { "type": "quantitative" } } }
// combo   — shared x, y.primary (bars) + y.secondary (line, own axis)
"encodings": { "x": { "fieldName": "month", "scale": { "type": "categorical" } },
               "y": { "primary":   { "fields": [{ "fieldName": "sum(revenue)" }], "axis": { "title": "Revenue" }, "scale": { "type": "quantitative" } },
                      "secondary": { "fields": [{ "fieldName": "sum(growth_pct)" }], "axis": { "title": "Growth %" }, "scale": { "type": "quantitative" } } } }
// pivot   — rows[] x columns[] with a cell measure
"encodings": { "rows": [{ "fieldName": "origin" }],
               "columns": [{ "fieldName": "cylinders", "scale": { "type": "categorical" } }],
               "cell": { "type": "single-cell", "fieldName": "sum(avg_mpg)" } }
// forecast-line — temporal x, y.original measure (auto-projects a forecast)
"encodings": { "x": { "fieldName": "date", "scale": { "type": "temporal" } },
               "y": { "original": { "fieldName": "sum(co2)" }, "scale": { "type": "quantitative" } } }
```

## Dashboard theme (Du Bois palette on native widgets)

Native widgets take their colors from the dashboard theme, so `build_dashboard.py`
sets `serialized_dashboard.uiSettings.theme` from `palette.dubois.dubois_theme()`:
`visualizationColors` (the categorical series order), plus canvas / widget / font /
selection colors (each `{light, dark}`). This makes the out-of-the-box charts
render in the Du Bois palette without per-widget color overrides.

## Du Bois styling

`palette/dubois.py` exposes the Du Bois tokens and a `dubois_config()` helper that
returns a Vega-Lite `config` block (range.category, range.ramp, axis/legend/view
styling, fonts) applied to every spec so the whole gallery reads as one system.
