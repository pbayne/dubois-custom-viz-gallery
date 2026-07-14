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

    # --- forecast-line (v1): temporal x, y.original measure (auto-forecasts ahead) ---
    {"id": "n_forecast", "title": "Forecast Line — CO₂ Concentration", "w": 3,
     "sql": f"SELECT to_date(Date) AS date, CO2 AS co2 FROM {T}.co2_concentration WHERE Date IS NOT NULL ORDER BY date",
     "disaggregated": False,
     "native": {"widgetType": "forecast-line",
                "encodings": {"x": {"fieldName": "date", "scale": {"type": "temporal"}},
                              "y": {"original": {"fieldName": "sum(co2)"}, "scale": {"type": "quantitative"}}}},
     "query_fields": [_n("date"), _n("sum(co2)", "SUM(`co2`)")]},
]
