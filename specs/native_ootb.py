"""AI/BI Out-of-the-Box (native) chart widgets — NOT Vega-Lite.

These use AI/BI's built-in widgetTypes (bar, line, area, pie, counter, table,
scatter, heatmap, box, histogram, symbol-map, choropleth-map, combo). Schema was
reverse-engineered from real dashboards; the verified pattern is:

    spec = {"version": 2|3, "widgetType": <type>,
            "encodings": {<channel>: {"fieldName","scale":{"type"},"displayName"}},
            "frame": {"title","showTitle"}, "mark"?: {...}}

Native widgets tile evenly in the AI/BI grid (unlike custom-viz), so this gallery
uses a 2-column layout. Each chart here uses the build's `native` contract
(`native` + `query_fields`). SQL pre-aggregates; fields are plain columns.

ALL 14 types VERIFIED to render (schema confirmed from reference dashboards + the
AI/BI visualization editor): counter, bar, line, area, pie, scatter, heatmap, box,
histogram, table, symbol-map, choropleth-map. Two need a non-obvious schema:
  * box       — y is five box-stat sub-encodings (whiskerStart/boxStart/boxMid/
                boxEnd/whiskerEnd) fed by aggregation query fields, disaggregated=False.
  * symbol-map— markers via a single `coordinates` encoding (coordinateType
                "longitude-latitude"), NOT bare latitude/longitude; widget version 2.
"""

CATEGORY = "Out-of-the-Box"
T = "pb_demo.custom_gallery"


def _n(name, expr=None):
    return {"name": name, "expression": expr or f"`{name}`"}


CHARTS = [
    # --- KPIs (counter) ---
    {"id": "n_counter_cars", "title": "Total Cars", "w": 3, "h": 3,
     "sql": f"SELECT COUNT(*) AS total_cars FROM {T}.cars",
     "native": {"widgetType": "counter",
                "encodings": {"value": {"fieldName": "total_cars", "displayName": "Total cars"}}},
     "query_fields": [_n("total_cars")], "_version": 2},
    {"id": "n_counter_mpg", "title": "Average MPG", "w": 3, "h": 3,
     "sql": f"SELECT ROUND(AVG(Miles_per_Gallon),1) AS avg_mpg FROM {T}.cars",
     "native": {"widgetType": "counter",
                "encodings": {"value": {"fieldName": "avg_mpg", "displayName": "Avg MPG"}}},
     "query_fields": [_n("avg_mpg")], "_version": 2},

    # --- bar ---
    {"id": "n_bar", "title": "Bar — Avg MPG by Origin", "w": 3, "h": 6,
     "sql": f"SELECT Origin AS origin, ROUND(AVG(Miles_per_Gallon),1) AS avg_mpg FROM {T}.cars GROUP BY Origin",
     "native": {"widgetType": "bar",
                "encodings": {"x": {"fieldName": "avg_mpg", "scale": {"type": "quantitative"}, "displayName": "Avg MPG"},
                              "y": {"fieldName": "origin", "scale": {"type": "categorical", "sort": {"by": "x-reversed"}}, "displayName": "Origin"}}},
     "query_fields": [_n("origin"), _n("avg_mpg")]},

    # --- stacked bar (color) ---
    {"id": "n_bar_stacked", "title": "Stacked Bar — Weather Days by Month", "w": 3, "h": 6,
     "sql": f"SELECT month(date) AS month, weather, COUNT(*) AS n FROM {T}.seattle_weather GROUP BY month(date), weather",
     "native": {"widgetType": "bar",
                "encodings": {"x": {"fieldName": "month", "scale": {"type": "categorical"}, "displayName": "Month"},
                              "y": {"fieldName": "n", "scale": {"type": "quantitative"}, "displayName": "Days"},
                              "color": {"fieldName": "weather", "scale": {"type": "categorical"}, "displayName": "Weather"}}},
     "query_fields": [_n("month"), _n("weather"), _n("n")]},

    # --- line ---
    {"id": "n_line", "title": "Line — Stock Prices", "w": 3, "h": 6,
     "sql": f"SELECT symbol, date, price FROM {T}.stocks ORDER BY date",
     "native": {"widgetType": "line",
                "encodings": {"x": {"fieldName": "date", "scale": {"type": "temporal"}, "displayName": "Date"},
                              "y": {"fieldName": "price", "scale": {"type": "quantitative"}, "displayName": "Price ($)"},
                              "color": {"fieldName": "symbol", "scale": {"type": "categorical"}, "displayName": "Symbol"}}},
     "query_fields": [_n("symbol"), _n("date"), _n("price")]},

    # --- area ---
    {"id": "n_area", "title": "Stacked Area — Iowa Electricity", "w": 3, "h": 6,
     "sql": f"SELECT year, source, net_generation FROM {T}.iowa_electricity ORDER BY year",
     "native": {"widgetType": "area",
                "encodings": {"x": {"fieldName": "year", "scale": {"type": "temporal"}, "displayName": "Year"},
                              "y": {"fieldName": "net_generation", "scale": {"type": "quantitative"}, "displayName": "Net generation"},
                              "color": {"fieldName": "source", "scale": {"type": "categorical"}, "displayName": "Source"}}},
     "query_fields": [_n("year"), _n("source"), _n("net_generation")]},

    # --- pie ---
    {"id": "n_pie", "title": "Pie — Cars by Origin", "w": 3, "h": 6,
     "sql": f"SELECT Origin AS origin, COUNT(*) AS n FROM {T}.cars GROUP BY Origin",
     "native": {"widgetType": "pie",
                "encodings": {"angle": {"fieldName": "n", "scale": {"type": "quantitative"}, "displayName": "Count"},
                              "color": {"fieldName": "origin", "scale": {"type": "categorical"}, "displayName": "Origin"}}},
     "query_fields": [_n("origin"), _n("n")]},

    # --- scatter (DERIVED) ---
    {"id": "n_scatter", "title": "Scatter — Horsepower vs MPG", "w": 3, "h": 6,
     "sql": f"SELECT Name AS name, Horsepower AS hp, Miles_per_Gallon AS mpg, Origin AS origin, Weight_in_lbs AS wt FROM {T}.cars WHERE Horsepower IS NOT NULL AND Miles_per_Gallon IS NOT NULL",
     "native": {"widgetType": "scatter",
                "encodings": {"x": {"fieldName": "hp", "scale": {"type": "quantitative"}, "displayName": "Horsepower"},
                              "y": {"fieldName": "mpg", "scale": {"type": "quantitative"}, "displayName": "Miles per Gallon"},
                              "color": {"fieldName": "origin", "scale": {"type": "categorical"}, "displayName": "Origin"},
                              "size": {"fieldName": "wt", "scale": {"type": "quantitative"}, "displayName": "Weight"}}},
     "query_fields": [_n("name"), _n("hp"), _n("mpg"), _n("origin"), _n("wt")]},

    # --- heatmap (DERIVED) ---
    {"id": "n_heatmap", "title": "Heatmap — Avg Max Temp by Month × Year", "w": 3, "h": 6,
     "sql": f"SELECT month(date) AS month, year(date) AS yr, ROUND(AVG(temp_max),1) AS t FROM {T}.seattle_weather GROUP BY month(date), year(date)",
     "native": {"widgetType": "heatmap",
                "encodings": {"x": {"fieldName": "month", "scale": {"type": "categorical"}, "displayName": "Month"},
                              "y": {"fieldName": "yr", "scale": {"type": "categorical"}, "displayName": "Year"},
                              "color": {"fieldName": "t", "scale": {"type": "quantitative"}, "displayName": "Avg max °C"}}},
     "query_fields": [_n("month"), _n("yr"), _n("t")]},

    # --- box ---
    # A native box plot does NOT take a raw y field: it wants the five box
    # statistics as separate aggregated query fields (min / Q1 / median / Q3 /
    # max), mapped to whiskerStart/boxStart/boxMid/boxEnd/whiskerEnd, and the
    # query must be AGGREGATED (disaggregated=False). Schema confirmed from the
    # AI/BI visualization editor.
    {"id": "n_box", "title": "Box Plot — Horsepower by Cylinders", "w": 3, "h": 6,
     "sql": f"SELECT CAST(Cylinders AS STRING) AS cylinders, Horsepower AS hp FROM {T}.cars WHERE Horsepower IS NOT NULL",
     "disaggregated": False,
     "native": {"widgetType": "box",
                "encodings": {"x": {"fieldName": "cylinders", "scale": {"type": "categorical"}, "displayName": "Cylinders"},
                              "y": {"whiskerStart": {"fieldName": "min(hp)"},
                                    "boxStart": {"fieldName": "q1(hp)"},
                                    "boxMid": {"fieldName": "median(hp)"},
                                    "boxEnd": {"fieldName": "q3(hp)"},
                                    "whiskerEnd": {"fieldName": "max(hp)"},
                                    "scale": {"type": "quantitative"}}}},
     "query_fields": [_n("cylinders"),
                      _n("min(hp)", "MIN(`hp`)"),
                      _n("q1(hp)", "PERCENTILE(`hp`, 0.25)"),
                      _n("median(hp)", "MEDIAN(`hp`)"),
                      _n("q3(hp)", "PERCENTILE(`hp`, 0.75)"),
                      _n("max(hp)", "MAX(`hp`)")]},

    # --- histogram (DERIVED) ---
    {"id": "n_histogram", "title": "Histogram — Horsepower", "w": 3, "h": 6,
     "sql": f"SELECT Horsepower AS hp FROM {T}.cars WHERE Horsepower IS NOT NULL",
     "native": {"widgetType": "histogram",
                "encodings": {"x": {"fieldName": "hp", "scale": {"type": "quantitative"}, "displayName": "Horsepower"}}},
     "query_fields": [_n("hp")]},

    # --- table ---
    {"id": "n_table", "title": "Table — Top Movies by Worldwide Gross", "w": 3, "h": 6,
     "sql": f"SELECT Title AS title, Major_Genre AS genre, ROUND(Worldwide_Gross/1e6,1) AS gross_m, IMDB_Rating AS imdb FROM {T}.movies WHERE Worldwide_Gross IS NOT NULL ORDER BY Worldwide_Gross DESC LIMIT 25",
     "native": {"widgetType": "table",
                "encodings": {"columns": [{"fieldName": "title", "displayName": "Title"},
                                          {"fieldName": "genre", "displayName": "Genre"},
                                          {"fieldName": "gross_m", "displayName": "Worldwide Gross ($M)"},
                                          {"fieldName": "imdb", "displayName": "IMDB"}]}},
     "query_fields": [_n("title"), _n("genre"), _n("gross_m"), _n("imdb")], "_version": 2},

    # --- symbol (point) map ---
    # A native symbol/point map places markers via a single `coordinates`
    # encoding (coordinateType "longitude-latitude" wrapping latitude+longitude),
    # NOT bare latitude/longitude channels; `color` + `extra` are optional, and
    # `mark.size:0` uses the default marker size. Schema confirmed from the AI/BI
    # visualization editor (widget version 2).
    {"id": "n_symbol_map", "title": "Symbol Map — US Airports by State", "w": 3, "h": 8,
     "sql": f"SELECT city, state, latitude, longitude FROM {T}.airports WHERE country='USA' AND longitude BETWEEN -170 AND -65 AND latitude BETWEEN 18 AND 72",
     "native": {"widgetType": "symbol-map",
                "mark": {"opacity": 0.8, "size": 0},
                "encodings": {"coordinates": {"coordinateType": "longitude-latitude",
                                              "latitude": {"fieldName": "latitude", "displayName": "Latitude"},
                                              "longitude": {"fieldName": "longitude", "displayName": "Longitude"}},
                              "color": {"fieldName": "state", "displayName": "State", "scale": {"type": "categorical"}},
                              "extra": [{"fieldName": "city", "displayName": "City"},
                                        {"fieldName": "state", "displayName": "State"}]}},
     "query_fields": [_n("state"), _n("latitude"), _n("longitude"), _n("city")]},

    # --- choropleth (VERIFIED type; reuses geometry table) ---
    {"id": "n_choropleth", "title": "Choropleth — California Counties", "w": 3, "h": 8,
     "sql": f"SELECT name, value, geojson FROM {T}.ca_counties_geo",
     "native": {"widgetType": "choropleth-map",
                "encodings": {"color": {"fieldName": "value", "displayName": "Value",
                                        "scale": {"type": "quantitative", "colorRamp": {"mode": "scheme", "scheme": "blues"}}},
                              "extra": [{"fieldName": "name"}],
                              "region": {"regionType": "custom", "fieldName": "geojson"}},
                "mark": {"opacity": 0.85}},
     "query_fields": [_n("value"), _n("name"), _n("geojson")]},

    # === Flow / hierarchy / specialized native types ===
    # Schemas below confirmed from the AI/BI visualization editor (Genie Code).
    # Several use AGGREGATION query fields + disaggregated=False and a bespoke
    # encoding shape unique to the widget type.

    # --- sankey (v1): stages[] + a value measure; source/target are the node cols ---
    {"id": "n_sankey", "title": "Sankey — Energy Flow", "w": 3, "h": 6,
     "sql": "SELECT * FROM VALUES ('Coal','Electricity',40.0),('Natural Gas','Electricity',30.0),('Solar','Electricity',15.0),('Wind','Electricity',12.0),('Electricity','Residential',52.0),('Electricity','Industrial',45.0) AS t(source, target, value)",
     "disaggregated": False,
     "native": {"widgetType": "sankey",
                "encodings": {"value": {"fieldName": "sum(value)"},
                              "stages": [{"fieldName": "source"}, {"fieldName": "target"}]}},
     "query_fields": [_n("source"), _n("target"), _n("sum(value)", "SUM(`value`)")]},

    # --- gantt (v1): rows[] + a temporal range{start,end} (raw rows) ---
    {"id": "n_gantt", "title": "Gantt — Project Timeline", "w": 3, "h": 6,
     "sql": "SELECT * FROM VALUES ('Design',DATE'2026-01-05',DATE'2026-02-15'),('Build',DATE'2026-02-10',DATE'2026-04-10'),('Test',DATE'2026-03-25',DATE'2026-05-05'),('Launch',DATE'2026-05-05',DATE'2026-05-25') AS t(task, start_date, end_date)",
     "native": {"widgetType": "gantt",
                "encodings": {"rows": [{"fieldName": "task"}],
                              "range": {"scale": {"type": "temporal"},
                                        "start": {"fieldName": "start_date"},
                                        "end": {"fieldName": "end_date"}}}},
     "query_fields": [_n("task"), _n("start_date"), _n("end_date")]},

    # --- funnel (v3): quantitative x, categorical y sorted by a measure ---
    {"id": "n_funnel", "title": "Funnel — Signup Conversion", "w": 3, "h": 6,
     "sql": "SELECT * FROM VALUES (1,'Visited',10000),(2,'Signed up',4200),(3,'Trial',1800),(4,'Purchased',650) AS t(step, stage, value)",
     "disaggregated": False,
     "native": {"widgetType": "funnel",
                "encodings": {"x": {"fieldName": "sum(value)", "scale": {"type": "quantitative"}},
                              "y": {"fieldName": "stage", "scale": {"type": "categorical",
                                    "sort": {"by": "measure", "measure": {"fieldName": "sum(step)"}}}}}},
     "query_fields": [_n("sum(value)", "SUM(`value`)"), _n("stage"), _n("sum(step)", "SUM(`step`)")]},

    # --- waterfall (v3): categorical x sorted by a measure, quantitative delta y ---
    {"id": "n_waterfall", "title": "Waterfall — Quarterly Profit Changes", "w": 3, "h": 6,
     "sql": "SELECT * FROM VALUES (1,'Start',100.0),(2,'Q1',35.0),(3,'Q2',-20.0),(4,'Q3',45.0),(5,'Q4',-15.0) AS t(ord, category, delta)",
     "disaggregated": False,
     "native": {"widgetType": "waterfall",
                "encodings": {"x": {"fieldName": "category", "scale": {"type": "categorical",
                                    "sort": {"by": "measure", "measure": {"fieldName": "sum(ord)"}}}},
                              "y": {"fieldName": "sum(delta)", "scale": {"type": "quantitative"}}}},
     "query_fields": [_n("category"), _n("sum(delta)", "SUM(`delta`)"), _n("sum(ord)", "SUM(`ord`)")]},

    # --- combo (v1): shared x, y.primary (bars) + y.secondary (line, own axis) ---
    {"id": "n_combo", "title": "Combo — Revenue (bars) + Growth % (line)", "w": 3, "h": 6,
     "sql": "SELECT * FROM VALUES (1,120.0,0.0),(2,135.0,12.5),(3,128.0,-5.2),(4,150.0,17.2),(5,165.0,10.0),(6,158.0,-4.2) AS t(month, revenue, growth_pct)",
     "disaggregated": False,
     "native": {"widgetType": "combo",
                "encodings": {"x": {"fieldName": "month", "scale": {"type": "categorical"}},
                              "y": {"primary": {"fields": [{"fieldName": "sum(revenue)"}],
                                                "axis": {"title": "Revenue"}, "scale": {"type": "quantitative"}},
                                    "secondary": {"fields": [{"fieldName": "sum(growth_pct)"}],
                                                  "axis": {"title": "Growth %"}, "scale": {"type": "quantitative"}}}}},
     "query_fields": [_n("month"), _n("sum(revenue)", "SUM(`revenue`)"), _n("sum(growth_pct)", "SUM(`growth_pct`)")]},

    # --- pivot (v3): rows[] x columns[] with a cell measure ---
    {"id": "n_pivot", "title": "Pivot — Avg MPG by Origin × Cylinders", "w": 3, "h": 6,
     "sql": f"SELECT Origin AS origin, CAST(Cylinders AS STRING) AS cylinders, ROUND(AVG(Miles_per_Gallon),1) AS avg_mpg FROM {T}.cars WHERE Miles_per_Gallon IS NOT NULL GROUP BY Origin, CAST(Cylinders AS STRING)",
     "disaggregated": False,
     "native": {"widgetType": "pivot",
                "encodings": {"rows": [{"fieldName": "origin"}],
                              "columns": [{"fieldName": "cylinders", "scale": {"type": "categorical"}}],
                              "cell": {"type": "single-cell", "fieldName": "sum(avg_mpg)"}}},
     "query_fields": [_n("origin"), _n("cylinders"), _n("sum(avg_mpg)", "SUM(`avg_mpg`)")]},

    # --- pivot (6-level deep hierarchy): year > quarter > month > region > product > sku ---
    {"id": "n_pivot_6level", "title": "6-Level Pivot — Year > Qtr > Month > Region > Product > SKU", "w": 6, "h": 12,
     "sql": """SELECT
  CAST(year AS STRING) AS year, quarter, month, region, product, sku,
  CAST(revenue AS DOUBLE) AS revenue, CAST(deals AS DOUBLE) AS deals
FROM (
  SELECT 2024 as year,'Q1' as quarter,'Jan' as month,'East' as region,'Alpha' as product,'A-100' as sku,85000 as revenue,25 as deals
  UNION ALL SELECT 2024,'Q1','Jan','East','Alpha','A-200',72000,20
  UNION ALL SELECT 2024,'Q1','Jan','West','Alpha','A-100',65000,18
  UNION ALL SELECT 2024,'Q1','Jan','West','Beta','B-100',45000,15
  UNION ALL SELECT 2024,'Q1','Jan','East','Beta','B-100',38000,12
  UNION ALL SELECT 2024,'Q1','Feb','East','Alpha','A-100',92000,28
  UNION ALL SELECT 2024,'Q1','Feb','West','Alpha','A-100',71000,22
  UNION ALL SELECT 2024,'Q1','Feb','East','Beta','B-200',48000,16
  UNION ALL SELECT 2024,'Q1','Mar','East','Alpha','A-100',98000,30
  UNION ALL SELECT 2024,'Q1','Mar','West','Beta','B-100',44000,14
  UNION ALL SELECT 2024,'Q2','Apr','East','Alpha','A-100',88000,26
  UNION ALL SELECT 2024,'Q2','Apr','West','Alpha','A-200',68000,21
  UNION ALL SELECT 2024,'Q2','May','East','Alpha','A-100',105000,32
  UNION ALL SELECT 2024,'Q2','May','West','Beta','B-200',46000,15
  UNION ALL SELECT 2024,'Q2','Jun','East','Beta','B-100',55000,18
  UNION ALL SELECT 2024,'Q2','Jun','West','Alpha','A-100',82000,25
  UNION ALL SELECT 2024,'Q3','Jul','East','Alpha','A-100',95000,27
  UNION ALL SELECT 2024,'Q3','Aug','West','Beta','B-100',42000,13
  UNION ALL SELECT 2024,'Q3','Sep','East','Alpha','A-200',78000,23
  UNION ALL SELECT 2024,'Q4','Oct','West','Alpha','A-100',110000,33
  UNION ALL SELECT 2024,'Q4','Nov','East','Beta','B-200',52000,17
  UNION ALL SELECT 2024,'Q4','Dec','East','Alpha','A-100',125000,38
  UNION ALL SELECT 2025,'Q1','Jan','East','Alpha','A-100',95000,28
  UNION ALL SELECT 2025,'Q1','Feb','West','Alpha','A-200',78000,24
  UNION ALL SELECT 2025,'Q1','Mar','East','Beta','B-100',52000,16
  UNION ALL SELECT 2025,'Q2','Apr','West','Alpha','A-100',88000,27
  UNION ALL SELECT 2025,'Q2','May','East','Alpha','A-100',115000,35
  UNION ALL SELECT 2025,'Q2','Jun','East','Beta','B-200',58000,19
) t""",
     "disaggregated": False,
     "native": {"widgetType": "pivot",
                "encodings": {"rows": [{"fieldName": "year"},
                                       {"fieldName": "quarter"},
                                       {"fieldName": "month"},
                                       {"fieldName": "region"},
                                       {"fieldName": "product"},
                                       {"fieldName": "sku"}],
                              "columns": [],
                              "cell": {"type": "multi-cell",
                                       "fields": [{"fieldName": "sum(revenue)", "cellType": "bar", "displayName": "Revenue",
                                                    "style": {"type": "color-scale",
                                                              "backgroundColor": {"scale": {"type": "quantitative",
                                                                                            "colorRamp": {"mode": "custom-diverging",
                                                                                                          "colors": {"start": "#FFF3E0", "mid": "#FF9E1B", "end": "#E65100"}}}}}},
                                                   {"fieldName": "sum(deals)", "cellType": "text", "displayName": "Deals"}]}}},
     "query_fields": [_n("year"), _n("quarter"), _n("month"), _n("region"), _n("product"), _n("sku"),
                      _n("sum(revenue)", "SUM(`revenue`)"), _n("sum(deals)", "SUM(`deals`)")]},

    # --- forecast-line (v1): temporal x, y.original measure (auto-forecasts ahead) ---
    {"id": "n_forecast", "title": "Forecast Line — CO₂ Concentration", "w": 3,
     "sql": f"SELECT to_date(Date) AS date, CO2 AS co2 FROM {T}.co2_concentration WHERE Date IS NOT NULL ORDER BY date",
     "disaggregated": False,
     "native": {"widgetType": "forecast-line",
                "encodings": {"x": {"fieldName": "date", "scale": {"type": "temporal"}},
                              "y": {"original": {"fieldName": "sum(co2)"}, "scale": {"type": "quantitative"}}}},
     "query_fields": [_n("date"), _n("sum(co2)", "SUM(`co2`)")]},

    # ═══════════════════════════════════════════════════════════════════
    # ADDITIONAL VARIANTS — cover every feature customers ask about
    # ═══════════════════════════════════════════════════════════════════

    # --- counter with conditional formatting (green/red threshold) ---
    {"id": "n_counter_styled", "title": "Counter — Revenue vs Target (Conditional Color)", "w": 3, "h": 3,
     "sql": f"SELECT SUM(Worldwide_Gross) AS revenue FROM {T}.movies WHERE Worldwide_Gross IS NOT NULL",
     "native": {"widgetType": "counter",
                "encodings": {"value": {"fieldName": "revenue", "displayName": "Total Worldwide Gross",
                                        "style": {"rules": [{"condition": {"operator": ">=",
                                                                           "operand": {"type": "data-value", "value": "1000000000"}},
                                                              "color": "#00A972"},
                                                             {"condition": {"operator": "<",
                                                                           "operand": {"type": "data-value", "value": "1000000000"}},
                                                              "color": "#FF3621"}]}}}},
     "query_fields": [_n("revenue", "SUM(`revenue`)")]},

    # --- counter with target comparison ---
    {"id": "n_counter_target", "title": "Counter — Avg MPG vs 30 Target", "w": 3, "h": 3,
     "sql": f"SELECT ROUND(AVG(Miles_per_Gallon),1) AS avg_mpg, 30.0 AS target FROM {T}.cars WHERE Miles_per_Gallon IS NOT NULL",
     "native": {"widgetType": "counter",
                "encodings": {"value": {"fieldName": "avg_mpg", "displayName": "Avg MPG"},
                              "target": {"fieldName": "target", "displayName": "Target"}}},
     "query_fields": [_n("avg_mpg"), _n("target")]},

    # --- horizontal bar ---
    {"id": "n_bar_horizontal", "title": "Horizontal Bar — Film Count by Genre", "w": 3, "h": 6,
     "sql": f"SELECT Major_Genre AS genre, COUNT(*) AS n FROM {T}.movies WHERE Major_Genre IS NOT NULL AND Major_Genre <> '' GROUP BY Major_Genre ORDER BY n DESC LIMIT 10",
     "disaggregated": False,
     "native": {"widgetType": "bar",
                "encodings": {"x": {"fieldName": "sum(n)", "scale": {"type": "quantitative"}, "displayName": "Films"},
                              "y": {"fieldName": "genre", "scale": {"type": "categorical", "sort": {"by": "x-reversed"}}, "displayName": "Genre"}}},
     "query_fields": [_n("genre"), _n("sum(n)", "SUM(`n`)")]},

    # --- grouped bar ---
    {"id": "n_bar_grouped", "title": "Grouped Bar — Avg MPG by Origin × Cylinders", "w": 3, "h": 6,
     "sql": f"SELECT Origin AS origin, CAST(Cylinders AS STRING) AS cylinders, ROUND(AVG(Miles_per_Gallon),1) AS avg_mpg FROM {T}.cars WHERE Miles_per_Gallon IS NOT NULL AND Cylinders IN (4,6,8) GROUP BY Origin, Cylinders",
     "disaggregated": False,
     "native": {"widgetType": "bar",
                "encodings": {"x": {"fieldName": "cylinders", "scale": {"type": "categorical"}, "displayName": "Cylinders"},
                              "y": {"fieldName": "sum(avg_mpg)", "scale": {"type": "quantitative"}, "displayName": "Avg MPG"},
                              "color": {"fieldName": "origin", "scale": {"type": "categorical"}, "displayName": "Origin"}},
                "mark": {"layout": "group"}},
     "query_fields": [_n("cylinders"), _n("origin"), _n("sum(avg_mpg)", "SUM(`avg_mpg`)")]},

    # --- line with points ---
    {"id": "n_line_points", "title": "Line with Points — Monthly Precipitation", "w": 3, "h": 6,
     "sql": f"SELECT month(to_date(date)) AS month_num, ROUND(AVG(precipitation),2) AS avg_precip FROM {T}.seattle_weather GROUP BY month(to_date(date)) ORDER BY month_num",
     "disaggregated": False,
     "native": {"widgetType": "line",
                "encodings": {"x": {"fieldName": "month_num", "scale": {"type": "quantitative"}, "displayName": "Month"},
                              "y": {"fieldName": "sum(avg_precip)", "scale": {"type": "quantitative"}, "displayName": "Avg Precipitation"}},
                "mark": {"showPoints": True}},
     "query_fields": [_n("month_num"), _n("sum(avg_precip)", "SUM(`avg_precip`)")]},

    # --- donut (pie with inner radius) ---
    {"id": "n_donut", "title": "Donut — Weather Type Distribution", "w": 3, "h": 6,
     "sql": f"SELECT weather, COUNT(*) AS n FROM {T}.seattle_weather GROUP BY weather",
     "disaggregated": False,
     "native": {"widgetType": "pie",
                "encodings": {"angle": {"fieldName": "sum(n)", "scale": {"type": "quantitative"}, "displayName": "Days"},
                              "color": {"fieldName": "weather", "scale": {"type": "categorical"}, "displayName": "Weather"}},
                "mark": {"innerRadius": 60}},
     "query_fields": [_n("weather"), _n("sum(n)", "SUM(`n`)")]},

    # --- formatted table with number formats, alignment, row numbers ---
    {"id": "n_table_formatted", "title": "Formatted Table — Car Stats by Origin", "w": 6, "h": 6,
     "sql": f"SELECT Origin AS origin, COUNT(*) AS count, ROUND(AVG(Miles_per_Gallon),1) AS avg_mpg, ROUND(AVG(Horsepower),0) AS avg_hp, ROUND(AVG(Weight_in_lbs),0) AS avg_weight FROM {T}.cars WHERE Miles_per_Gallon IS NOT NULL GROUP BY Origin ORDER BY avg_mpg DESC",
     "disaggregated": False,
     "native": {"widgetType": "table",
                "encodings": {"columns": [
                    {"fieldName": "origin", "type": "string", "displayAs": "string", "displayName": "Origin", "title": "origin", "visible": True, "order": 100000},
                    {"fieldName": "sum(count)", "type": "integer", "displayAs": "number", "displayName": "Cars", "title": "count", "visible": True, "order": 100001, "numberFormat": "#,##0", "alignContent": "right"},
                    {"fieldName": "sum(avg_mpg)", "type": "number", "displayAs": "number", "displayName": "Avg MPG", "title": "avg_mpg", "visible": True, "order": 100002, "numberFormat": "#,##0.0", "alignContent": "right"},
                    {"fieldName": "sum(avg_hp)", "type": "integer", "displayAs": "number", "displayName": "Avg HP", "title": "avg_hp", "visible": True, "order": 100003, "numberFormat": "#,##0", "alignContent": "right"},
                    {"fieldName": "sum(avg_weight)", "type": "integer", "displayAs": "number", "displayName": "Avg Weight (lbs)", "title": "avg_weight", "visible": True, "order": 100004, "numberFormat": "#,##0", "alignContent": "right"}]},
                "condensed": True, "withRowNumber": True},
     "query_fields": [_n("origin"), _n("sum(count)", "SUM(`count`)"), _n("sum(avg_mpg)", "SUM(`avg_mpg`)"), _n("sum(avg_hp)", "SUM(`avg_hp`)"), _n("sum(avg_weight)", "SUM(`avg_weight`)")]},

    # --- pivot with COLUMN hierarchy + displayTotal ---
    {"id": "n_pivot_colhier", "title": "Pivot — Revenue by Region with Year > Quarter Columns", "w": 6, "h": 8,
     "sql": """SELECT region, CAST(year AS STRING) AS year, quarter,
  CAST(revenue AS DOUBLE) AS revenue
FROM (
  SELECT 'East' as region, 2024 as year, 'Q1' as quarter, 515000 as revenue
  UNION ALL SELECT 'East', 2024, 'Q2', 600000
  UNION ALL SELECT 'East', 2024, 'Q3', 580000
  UNION ALL SELECT 'East', 2024, 'Q4', 735000
  UNION ALL SELECT 'West', 2024, 'Q1', 420000
  UNION ALL SELECT 'West', 2024, 'Q2', 510000
  UNION ALL SELECT 'West', 2024, 'Q3', 470000
  UNION ALL SELECT 'West', 2024, 'Q4', 620000
  UNION ALL SELECT 'East', 2025, 'Q1', 595000
  UNION ALL SELECT 'East', 2025, 'Q2', 685000
  UNION ALL SELECT 'West', 2025, 'Q1', 480000
  UNION ALL SELECT 'West', 2025, 'Q2', 560000
) t""",
     "disaggregated": False,
     "native": {"widgetType": "pivot",
                "encodings": {"rows": [{"fieldName": "region", "displayName": "Region"}],
                              "columns": [{"fieldName": "year", "displayTotal": True, "displayName": "Year"},
                                          {"fieldName": "quarter", "displayTotal": True, "displayName": "Quarter"}],
                              "cell": {"type": "single-cell", "fieldName": "sum(revenue)", "cellType": "bar", "displayName": "Revenue",
                                       "style": {"type": "color-scale",
                                                 "backgroundColor": {"scale": {"type": "quantitative",
                                                                               "colorRamp": {"mode": "custom-diverging",
                                                                                             "colors": {"start": "#E8F5E9", "mid": "#66BB6A", "end": "#1B5E20"}}}}}}}},
     "query_fields": [_n("region"), _n("year"), _n("quarter"), _n("sum(revenue)", "SUM(`revenue`)")]},

    # --- filter-single-select ---
    {"id": "n_filter_single", "title": "Filter — Single Select (Origin)", "w": 2, "h": 1,
     "sql": f"SELECT DISTINCT Origin AS origin FROM {T}.cars WHERE Origin IS NOT NULL ORDER BY Origin",
     "native": {"widgetType": "filter-single-select",
                "encodings": {"fields": [{"fieldName": "origin", "displayName": "Origin"}]}},
     "query_fields": [_n("origin")]},

    # --- filter-multi-select ---
    {"id": "n_filter_multi", "title": "Filter — Multi Select (Cylinders)", "w": 2, "h": 1,
     "sql": f"SELECT DISTINCT CAST(Cylinders AS STRING) AS cylinders FROM {T}.cars WHERE Cylinders IS NOT NULL ORDER BY cylinders",
     "native": {"widgetType": "filter-multi-select",
                "encodings": {"fields": [{"fieldName": "cylinders", "displayName": "Cylinders"}]}},
     "query_fields": [_n("cylinders")]},

    # --- filter-date-range-picker ---
    {"id": "n_filter_date", "title": "Filter — Date Range Picker", "w": 2, "h": 1,
     "sql": f"SELECT to_date(date) AS date FROM {T}.seattle_weather WHERE date IS NOT NULL",
     "native": {"widgetType": "filter-date-range-picker",
                "encodings": {"fields": [{"fieldName": "date", "displayName": "Date Range"}]}},
     "query_fields": [_n("date")]},

    # --- normalized/100% stacked area ---
    {"id": "n_area_normalized", "title": "Normalized Area — Weather Share by Month", "w": 3, "h": 6,
     "sql": f"SELECT month(to_date(date)) AS month_num, weather, COUNT(*) AS n FROM {T}.seattle_weather GROUP BY month(to_date(date)), weather",
     "disaggregated": False,
     "native": {"widgetType": "area",
                "encodings": {"x": {"fieldName": "month_num", "scale": {"type": "quantitative"}, "displayName": "Month"},
                              "y": {"fieldName": "sum(n)", "scale": {"type": "quantitative"}, "displayName": "Days"},
                              "color": {"fieldName": "weather", "scale": {"type": "categorical"}, "displayName": "Weather"}},
                "mark": {"stacking": "normalize"}},
     "query_fields": [_n("month_num"), _n("weather"), _n("sum(n)", "SUM(`n`)")]},

    # --- scatter with size + color ---
    {"id": "n_scatter_bubble", "title": "Bubble Scatter — HP vs MPG, Size=Weight, Color=Origin", "w": 3, "h": 6,
     "sql": f"SELECT Horsepower AS hp, Miles_per_Gallon AS mpg, Weight_in_lbs AS weight, Origin AS origin FROM {T}.cars WHERE Horsepower IS NOT NULL AND Miles_per_Gallon IS NOT NULL",
     "native": {"widgetType": "scatter",
                "encodings": {"x": {"fieldName": "hp", "scale": {"type": "quantitative"}, "displayName": "Horsepower"},
                              "y": {"fieldName": "mpg", "scale": {"type": "quantitative"}, "displayName": "Miles per Gallon"},
                              "size": {"fieldName": "weight", "scale": {"type": "quantitative"}, "displayName": "Weight (lbs)"},
                              "color": {"fieldName": "origin", "scale": {"type": "categorical"}, "displayName": "Origin"}}},
     "query_fields": [_n("hp"), _n("mpg"), _n("weight"), _n("origin")]},
]
