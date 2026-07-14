# Spec-authoring reference (READ THIS FIRST)

Each `specs/<category>.py` exports `CATEGORY = "<Tab Title>"` and
`CHARTS = [chart, ...]`. A **chart** is:

```python
{
  "id": "unique_snake_id",          # unique across the WHOLE project -> dataset ds_<id>, widget w_<id>
  "title": "Human Title",           # widget frame title
  "sql": "SELECT ...",              # dataset query; MUST output exactly the columns in `fields`
  "fields": ["colA", "colB"],       # every column the spec references (match SQL aliases exactly)
  "spec": { ... Vega-Lite ... },    # NO $schema / data / width / height / config  (build injects them)
  "w": 4, "h": 7,                   # OPTIONAL grid size (12-col grid). default w=4 h=7. wide charts: w=8/12
}
```

The build script injects into every spec: `$schema`, `"data": {"name": "databricks_query"}`,
`"width":"container"`, `"height":"container"`, and the Du Bois `config` (palette
ranges, recessive grid, rounded bars, etc.). **Do NOT set `config`, `data`,
`width`, `height`, `$schema`** — and do NOT set explicit categorical mark colors
unless the chart needs a specific highlight; let the injected palette color by
field. (You MAY set a single fixed color for a single-series mark.)

## HARD RULES (violating these breaks rendering)
1. **No faceting**: never use `facet`, `column`, `row`, or `"repeat"`. They do not
   size correctly inside a container-sized custom viz. For grouped bars use
   `xOffset`. For "small multiples" pick a different chart.
2. Every column in `fields` must be a real output column of `sql`. Alias columns in
   SQL to clean snake_case names and reference those exact names in the spec.
3. Bind temporal fields with `"type": "temporal"`; the SQL should return a real
   DATE/TIMESTAMP (use `to_date(...)` if the source column is a STRING).
4. Keep each chart to ONE dataset/query (layers may reuse the same `databricks_query`).
5. Prefer `xOffset`, `stack`, `layer`, `transform` (fold/window/joinaggregate/
   density/regression/quantile) — all supported.
6. Fully-qualify tables: `pb_demo.custom_gallery.<table>`.

## VALIDATE before finalizing
For EACH chart, run its SQL and confirm the returned columns equal `fields`:
```
databricks api post /api/2.0/sql/statements -p <your-profile> \
  --json '{"warehouse_id":"<your-warehouse>","statement":"<sql>","wait_timeout":"30s"}'
```
Check `.status.state == SUCCEEDED` and `.manifest.schema.columns[].name` == fields.
Fix any mismatch. Do not finalize a chart whose SQL FAILED.

## Two worked examples
See `specs/bar_column.py` and `specs/line_area.py` in this repo for the exact
style (simple bar, aggregate, stacked, normalized, layered, highlight, labels,
mean-rule; simple/multi/step line, area, stacked/normalized/streamgraph area,
band+line).

## Available tables (pb_demo.custom_gallery) and their columns

- **cars** (400): Name, Miles_per_Gallon, Cylinders, Displacement, Horsepower, Weight_in_lbs, Acceleration, Year(TIMESTAMP), Origin
- **movies** (~3200): Title, US_Gross, Worldwide_Gross, US_DVD_Sales, Production_Budget, Release_Date(STRING), MPAA_Rating, Running_Time_min, Distributor, Source, Major_Genre, Creative_Type, Director, Rotten_Tomatoes_Rating, IMDB_Rating, IMDB_Votes
- **seattle_weather** (1461): date(TIMESTAMP), precipitation, temp_max, temp_min, wind, weather
- **stocks** (560): symbol, date(TIMESTAMP), price
- **sp500** (~500): date(TIMESTAMP), price
- **barley** (120): yield, variety, year, site
- **population** (570): year, age, sex(1=male,2=female), people
- **disasters** (~800): Entity, Year, Deaths
- **wheat** (~50): year, wheat, wages
- **us_employment** (120): month(STRING), nonfarm, private, construction, manufacturing, information, financial_activities, government, ... (many industry LONG cols), nonfarm_change
- **iowa_electricity** (51): year(TIMESTAMP), source, net_generation
- **co2_concentration** (~700): Date(STRING -> to_date), CO2
- **gapminder** (693): year, country, cluster, pop, life_expect, fertility
- **github** (~1900): time(TIMESTAMP), count
- **driving** (55): side, year, miles, gas
- **ohlc** (~40): date(TIMESTAMP), open, high, low, close, signal, ret
- **jobs** (~7600): job, sex, year, count, perc
- **birdstrikes** (~10000): Airport_Name, Aircraft_Make_Model, Effect_Amount_of_damage, Flight_Date(STRING), Aircraft_Airline_Operator, Origin_State, When_Phase_of_flight, Wildlife_Size, Wildlife_Species, When_Time_of_day, Cost_Other, Cost_Repair, Cost_Total, Speed_IAS_in_knots
- **airports** (~3400): iata, name, city, state, country, latitude, longitude
- **unemployment_across_industries** (~1700): series, year, month, count, rate, date(TIMESTAMP)

## Category assignments (what goes in each module)
- **distributions**: histogram (movies IMDB_Rating; cars Horsepower), binned hist, density (transform density), stacked/overlaid histogram by group, cumulative frequency, box plot (cars MPG by Cylinders), violin-ish (density by group), 2D binned heatmap of counts (goes to heatmap module — skip here), dot/strip plot, mean+CI error bars.
- **correlation**: scatter (cars Horsepower vs MPG), colored scatter by Origin, bubble (size by Weight), scatter matrix -> AVOID (repeat); instead binned scatter, regression line (transform regression), residuals, connected scatter (driving miles vs gas over year), text-as-mark scatter, log-scale scatter (gapminder fertility vs life_expect, size pop).
- **part_to_whole**: pie, donut, arc with labels, stacked bar as part-to-whole, normalized area (already in line) -> pick pie/donut/nested; treemap NOT supported (skip), sunburst NOT supported (skip). Use pie (weather counts), donut (cars by Origin), pie with % labels.
- **radial**: radial (rose) bar, radial plot (radius encodes value), arc/progress gauge (2-row used/headroom), wind-rose-ish, pie already in part_to_whole. Keep 3-5.
- **heatmap_matrix**: rect heatmap (seattle_weather max temp by month x day-of-month via day()), github punchcard (time -> hour x weekday, size/color by count), correlation-ish matrix (movies genre x rating bucket counts), annual heatmap, 2D histogram heatmap (cars binned Horsepower x MPG count).
- **ranking**: sorted bar (top movies by gross), lollipop (rule+point), bump-ish (avoid), dot plot ranking, bar with rank labels, top-N (LIMIT in SQL).
- **tables**: text table via mark text (a small aggregated table rendered as text grid), heatmap-table (rect + text overlay), KPI/big-number (single value text), bullet-ish. Keep 3-5.
- **advanced**: layered bar+line combo (one y — do NOT dual-axis; index or share scale), ranged dot plot, error bars + mean, candlestick (ohlc: rule high-low + bar open-close, color by signal), waterfall, slope chart (two-year comparison via xOffset/line), interactive-looking (static) e.g. highlight condition. Keep 6-10.
