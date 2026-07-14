"""Indicators & Dials. Specs are Vega-Lite WITHOUT config/data/width/height
(the build script injects Du Bois config + databricks_query binding + container
sizing). These are the non-chart, "at-a-glance" ways to read data: a bullet
chart (actual vs target vs qualitative bands), a needle DIAL/speedometer, a
radial progress ring vs a goal, a linear progress meter, a KPI big-number with a
delta/trend arrow, a sparkline with a labeled last value, and a KPI stat strip.
Each chart binds to one dataset defined by `sql`; `fields` lists every column the
spec references (must match the SQL output aliases)."""

CATEGORY = "Indicators & Dials"

CHARTS = [
    {
        "id": "ind_bullet", "title": "Bullet Chart — On-Time Delivery % vs Target",
        "sql": "SELECT * FROM VALUES ('On-Time %', 70.0, 85.0, 95.0, 88.0, 90.0) AS t(category, poor, ok, good, measure, target)",
        "fields": ["category", "poor", "ok", "good", "measure", "target"],
        "w": 3, "h": 4,
        "spec": {"encoding": {"y": {"field": "category", "type": "nominal", "title": None}},
                 "layer": [
                     {"mark": {"type": "bar", "color": "#E5E0D8"},
                      "encoding": {"x": {"field": "good", "type": "quantitative", "title": "Percent", "scale": {"domain": [0, 100]}}}},
                     {"mark": {"type": "bar", "color": "#C9C0B1"},
                      "encoding": {"x": {"field": "ok", "type": "quantitative"}}},
                     {"mark": {"type": "bar", "color": "#B7A98F"},
                      "encoding": {"x": {"field": "poor", "type": "quantitative"}}},
                     {"mark": {"type": "bar", "color": "#241E1E", "size": 12},
                      "encoding": {"x": {"field": "measure", "type": "quantitative"}}},
                     {"mark": {"type": "tick", "color": "#DC4B34", "thickness": 3, "size": 34},
                      "encoding": {"x": {"field": "target", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "ind_radial_dial", "title": "Dial — Share of Cars Over 25 MPG (Speedometer)",
        "sql": "SELECT ROUND(100.0*SUM(CASE WHEN Miles_per_Gallon>=25 THEN 1 ELSE 0 END)/COUNT(*),1) AS value, 0 AS zero, 100 AS full, ROUND(100.0*SUM(CASE WHEN Miles_per_Gallon>=25 THEN 1 ELSE 0 END)/COUNT(*),1)-1.5 AS needle_lo, ROUND(100.0*SUM(CASE WHEN Miles_per_Gallon>=25 THEN 1 ELSE 0 END)/COUNT(*),1)+1.5 AS needle_hi FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL",
        "fields": ["value", "zero", "full", "needle_lo", "needle_hi"],
        "w": 3, "h": 6,
        "spec": {"transform": [{"calculate": "format(datum.value,'.0f') + '%'", "as": "label"}],
                 "layer": [
                     {"mark": {"type": "arc", "innerRadius": 55, "outerRadius": 82, "cornerRadius": 2},
                      "encoding": {"theta": {"field": "zero", "type": "quantitative", "scale": {"domain": [0, 100], "range": [-1.5708, 1.5708]}},
                                   "theta2": {"field": "full"},
                                   "color": {"value": "#E4E4E4"}}},
                     {"mark": {"type": "arc", "innerRadius": 55, "outerRadius": 82, "cornerRadius": 2},
                      "encoding": {"theta": {"field": "zero", "type": "quantitative", "scale": {"domain": [0, 100], "range": [-1.5708, 1.5708]}},
                                   "theta2": {"field": "value"},
                                   "color": {"value": "#5593F7"}}},
                     {"mark": {"type": "arc", "innerRadius": 0, "outerRadius": 74},
                      "encoding": {"theta": {"field": "needle_lo", "type": "quantitative", "scale": {"domain": [0, 100], "range": [-1.5708, 1.5708]}},
                                   "theta2": {"field": "needle_hi"},
                                   "color": {"value": "#241E1E"}}},
                     {"mark": {"type": "arc", "innerRadius": 0, "outerRadius": 8},
                      "encoding": {"theta": {"field": "zero", "type": "quantitative", "scale": {"domain": [0, 100], "range": [-1.5708, 1.5708]}},
                                   "theta2": {"field": "full"},
                                   "color": {"value": "#241E1E"}}},
                     {"mark": {"type": "text", "fontSize": 26, "fontWeight": "bold", "color": "#241E1E", "dy": 34},
                      "encoding": {"text": {"field": "label", "type": "nominal"}}}
                 ]},
    },
    {
        "id": "ind_progress_ring", "title": "Progress Ring — Avg MPG Toward 40 mpg Goal",
        "sql": "WITH a AS (SELECT AVG(Miles_per_Gallon) AS m FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL) SELECT 'Used' AS segment, ROUND(m,1) AS value, 1 AS ord, ROUND(100*m/40,0) AS pct FROM a UNION ALL SELECT 'Remaining' AS segment, ROUND(40-m,1) AS value, 2 AS ord, ROUND(100*m/40,0) AS pct FROM a",
        "fields": ["segment", "value", "ord", "pct"],
        "w": 3, "h": 6,
        "spec": {"transform": [{"calculate": "format(datum.pct,'.0f') + '%'", "as": "label"}],
                 "layer": [
                     {"mark": {"type": "arc", "innerRadius": 62, "outerRadius": 92, "tooltip": True},
                      "encoding": {"theta": {"field": "value", "type": "quantitative", "stack": True, "sort": {"field": "ord"}},
                                   "order": {"field": "ord", "type": "ordinal"},
                                   "color": {"field": "segment", "type": "nominal",
                                             "scale": {"domain": ["Used", "Remaining"], "range": ["#DC4B34", "#E4E4E4"]},
                                             "title": None}}},
                     {"transform": [{"filter": "datum.segment == 'Used'"}],
                      "mark": {"type": "text", "fontSize": 30, "fontWeight": "bold", "color": "#241E1E"},
                      "encoding": {"text": {"field": "label", "type": "nominal"}}}
                 ]},
    },
    {
        "id": "ind_linear_meter", "title": "Linear Meter — Avg Horsepower vs 120 hp Target",
        "sql": "SELECT 'Avg Horsepower' AS metric, ROUND(AVG(Horsepower),0) AS value, 120 AS target, 240 AS scale_max FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["metric", "value", "target", "scale_max"],
        "w": 3, "h": 4,
        "spec": {"encoding": {"y": {"field": "metric", "type": "nominal", "title": None}},
                 "layer": [
                     {"mark": {"type": "bar", "color": "#E5E0D8"},
                      "encoding": {"x": {"field": "scale_max", "type": "quantitative", "title": "Horsepower", "scale": {"domain": [0, 240]}}}},
                     {"mark": {"type": "bar", "color": "#5593F7", "size": 22},
                      "encoding": {"x": {"field": "value", "type": "quantitative"}}},
                     {"mark": {"type": "tick", "color": "#DC4B34", "thickness": 3, "size": 40},
                      "encoding": {"x": {"field": "target", "type": "quantitative"}}},
                     {"mark": {"type": "text", "align": "left", "dx": 6, "fontWeight": "bold", "color": "#241E1E"},
                      "encoding": {"x": {"field": "value", "type": "quantitative"},
                                   "text": {"field": "value", "type": "quantitative", "format": ".0f"}}}
                 ]},
    },
    {
        "id": "ind_kpi_delta", "title": "KPI + Delta — GOOG Price vs First Close",
        "sql": "WITH g AS (SELECT CAST(price AS DOUBLE) AS price, ROW_NUMBER() OVER (ORDER BY date DESC) AS rn_desc, ROW_NUMBER() OVER (ORDER BY date ASC) AS rn_asc FROM pb_demo.custom_gallery.stocks WHERE symbol='GOOG'), c AS (SELECT MAX(CASE WHEN rn_desc=1 THEN price END) AS current_val, MAX(CASE WHEN rn_asc=1 THEN price END) AS prior_val FROM g) SELECT ROUND(current_val,2) AS current_val, ROUND(current_val-prior_val,2) AS delta, ROUND(100.0*(current_val-prior_val)/prior_val,1) AS delta_pct FROM c",
        "fields": ["current_val", "delta", "delta_pct"],
        "w": 3, "h": 5,
        "spec": {"transform": [
                    {"calculate": "'$' + format(datum.current_val,',.0f')", "as": "big_label"},
                    {"calculate": "(datum.delta_pct >= 0 ? '▲ +' : '▼ ') + format(datum.delta_pct,'.1f') + '%'", "as": "delta_label"}],
                 "layer": [
                     {"mark": {"type": "text", "fontSize": 56, "fontWeight": "bold", "color": "#241E1E", "dy": -14},
                      "encoding": {"text": {"field": "big_label", "type": "nominal"}}},
                     {"mark": {"type": "text", "fontSize": 20, "fontWeight": "bold", "dy": 34},
                      "encoding": {"text": {"field": "delta_label", "type": "nominal"},
                                   "color": {"condition": {"test": "datum.delta_pct >= 0", "value": "#3E7D53"}, "value": "#DC4B34"}}}
                 ]},
    },
    {
        "id": "ind_sparkline", "title": "Sparkline — GOOG Price Trend (Last Labeled)",
        "sql": "SELECT date, CAST(price AS DOUBLE) AS price FROM pb_demo.custom_gallery.stocks WHERE symbol='GOOG' ORDER BY date",
        "fields": ["date", "price"],
        "w": 3, "h": 3,
        "spec": {"layer": [
                     {"mark": {"type": "line", "color": "#5593F7", "strokeWidth": 2},
                      "encoding": {"x": {"field": "date", "type": "temporal", "axis": None, "title": None},
                                   "y": {"field": "price", "type": "quantitative", "axis": None, "title": None, "scale": {"zero": False}}}},
                     {"transform": [{"window": [{"op": "row_number", "as": "rn"}], "sort": [{"field": "date", "order": "descending"}]},
                                    {"filter": "datum.rn == 1"}],
                      "mark": {"type": "point", "filled": True, "color": "#DC4B34", "size": 60},
                      "encoding": {"x": {"field": "date", "type": "temporal"},
                                   "y": {"field": "price", "type": "quantitative"}}},
                     {"transform": [{"window": [{"op": "row_number", "as": "rn"}], "sort": [{"field": "date", "order": "descending"}]},
                                    {"filter": "datum.rn == 1"}],
                      "mark": {"type": "text", "align": "left", "dx": 6, "fontWeight": "bold", "color": "#DC4B34"},
                      "encoding": {"x": {"field": "date", "type": "temporal"},
                                   "y": {"field": "price", "type": "quantitative"},
                                   "text": {"field": "price", "type": "quantitative", "format": "$,.0f"}}}
                 ]},
    },
    {
        "id": "ind_kpi_row", "title": "KPI Strip — Fleet Stats at a Glance",
        "sql": "SELECT 'Avg MPG' AS label, CAST(ROUND(AVG(Miles_per_Gallon),1) AS STRING) AS value, 1 AS ord FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL UNION ALL SELECT 'Avg HP' AS label, CAST(ROUND(AVG(Horsepower),0) AS STRING) AS value, 2 AS ord FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL UNION ALL SELECT 'Cars' AS label, CAST(COUNT(*) AS STRING) AS value, 3 AS ord FROM pb_demo.custom_gallery.cars UNION ALL SELECT 'Avg Wt (klbs)' AS label, CAST(ROUND(AVG(Weight_in_lbs)/1000,1) AS STRING) AS value, 4 AS ord FROM pb_demo.custom_gallery.cars WHERE Weight_in_lbs IS NOT NULL",
        "fields": ["label", "value", "ord"],
        "w": 3, "h": 3,
        "spec": {"encoding": {"x": {"field": "ord", "type": "ordinal", "axis": None, "title": None, "scale": {"paddingOuter": 0.4}}},
                 "layer": [
                     {"mark": {"type": "text", "fontSize": 30, "fontWeight": "bold", "color": "#DC4B34", "dy": -8},
                      "encoding": {"text": {"field": "value", "type": "nominal"}}},
                     {"mark": {"type": "text", "fontSize": 13, "color": "#6B4E3D", "dy": 20},
                      "encoding": {"text": {"field": "label", "type": "nominal"}}}
                 ]},
    },
]
