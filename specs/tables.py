"""Tables & Text. Specs are Vega-Lite WITHOUT config/data/width/height
(the build script injects Du Bois config + databricks_query binding + container
sizing). Text-mark "tables", a heatmap-table (rect + text overlay), a big-number
KPI, a bar-in-table, and a colored-text ranking table."""

CATEGORY = "Tables & Text"

CHARTS = [
    {
        "id": "tbl_heatmap_table", "title": "Heatmap Table — Avg MPG by Origin × Cylinders",
        "sql": "SELECT Origin AS origin, CAST(Cylinders AS STRING) AS cylinders, ROUND(AVG(Miles_per_Gallon),1) AS avg_mpg FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL GROUP BY Origin, Cylinders",
        "fields": ["origin", "cylinders", "avg_mpg"],
        "w": 3,
        "spec": {"layer": [
            {"mark": {"type": "rect"},
             "encoding": {"x": {"field": "cylinders", "type": "ordinal", "title": "Cylinders", "axis": {"labelAngle": 0}},
                          "y": {"field": "origin", "type": "nominal", "title": None},
                          "color": {"field": "avg_mpg", "type": "quantitative", "title": "Avg MPG"}}},
            {"mark": {"type": "text", "fontWeight": "bold"},
             "encoding": {"x": {"field": "cylinders", "type": "ordinal"},
                          "y": {"field": "origin", "type": "nominal"},
                          "text": {"field": "avg_mpg", "type": "quantitative"},
                          "color": {"condition": {"test": "datum.avg_mpg > 25", "value": "#241E1E"}, "value": "#F2E9DC"}}}
        ]},
    },
    {
        "id": "tbl_kpi", "title": "KPI — Average Fuel Economy",
        "sql": "SELECT ROUND(AVG(Miles_per_Gallon),1) AS avg_mpg, 'Average MPG · all cars' AS label FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL",
        "fields": ["avg_mpg", "label"],
        "w": 3, "h": 5,
        "spec": {"layer": [
            {"mark": {"type": "text", "fontSize": 72, "fontWeight": "bold", "color": "#DC4B34", "dy": -6},
             "encoding": {"text": {"field": "avg_mpg", "type": "quantitative"}}},
            {"mark": {"type": "text", "fontSize": 15, "dy": 48, "color": "#6B4E3D"},
             "encoding": {"text": {"field": "label", "type": "nominal"}}}
        ]},
    },
    {
        "id": "tbl_bar_in_table", "title": "Bar-in-Table — Top Distributors by Film Count",
        "sql": "SELECT Distributor AS distributor, COUNT(*) AS n FROM pb_demo.custom_gallery.movies WHERE Distributor IS NOT NULL AND Distributor <> '' GROUP BY Distributor ORDER BY n DESC LIMIT 10",
        "fields": ["distributor", "n"],
        "w": 3,
        "spec": {"layer": [
            {"mark": {"type": "bar"},
             "encoding": {"y": {"field": "distributor", "type": "nominal", "sort": "-x", "title": None},
                          "x": {"field": "n", "type": "quantitative", "title": "Films"}}},
            {"mark": {"type": "text", "align": "left", "dx": 4, "fontWeight": "bold"},
             "encoding": {"y": {"field": "distributor", "type": "nominal", "sort": "-x"},
                          "x": {"field": "n", "type": "quantitative"},
                          "text": {"field": "n", "type": "quantitative"}}}
        ]},
    },
    {
        "id": "tbl_colored_text", "title": "Colored-Text Table — Top Films by Worldwide Gross",
        "sql": "SELECT Title AS title, ROUND(Worldwide_Gross/1e6,0) AS gross_m FROM pb_demo.custom_gallery.movies WHERE Worldwide_Gross IS NOT NULL AND Title IS NOT NULL ORDER BY Worldwide_Gross DESC LIMIT 12",
        "fields": ["title", "gross_m"],
        "w": 3,
        "spec": {"mark": {"type": "text", "fontSize": 13, "fontWeight": "bold"},
                 "encoding": {"y": {"field": "title", "type": "nominal", "sort": {"field": "gross_m", "order": "descending"}, "title": None},
                              "text": {"field": "gross_m", "type": "quantitative", "format": ",.0f", "title": "$M"},
                              "color": {"field": "gross_m", "type": "quantitative", "title": "Gross ($M)"}}},
    },
    {
        "id": "tbl_text_grid", "title": "Text Grid — Metrics by Origin",
        "sql": "SELECT Origin AS origin, COUNT(*) AS cars, ROUND(AVG(Miles_per_Gallon),1) AS avg_mpg, ROUND(AVG(Horsepower),0) AS avg_hp FROM pb_demo.custom_gallery.cars GROUP BY Origin",
        "fields": ["origin", "cars", "avg_mpg", "avg_hp"],
        "w": 3,
        "spec": {"transform": [{"fold": ["cars", "avg_mpg", "avg_hp"], "as": ["metric", "value"]}],
                 "mark": {"type": "text", "fontSize": 15, "fontWeight": "bold", "color": "#241E1E"},
                 "encoding": {"x": {"field": "metric", "type": "nominal", "title": None, "axis": {"labelAngle": 0, "orient": "top"}},
                              "y": {"field": "origin", "type": "nominal", "title": None},
                              "text": {"field": "value", "type": "quantitative"}}},
    },
    {
        "id": "tbl2_mosaic_count", "title": "Mosaic — Car Count by Origin × Cylinders",
        "sql": "SELECT Origin AS origin, CAST(Cylinders AS STRING) AS cylinders, COUNT(*) AS count FROM pb_demo.custom_gallery.cars GROUP BY Origin, Cylinders",
        "fields": ["origin", "cylinders", "count"],
        "w": 3,
        "spec": {"layer": [
            {"mark": {"type": "rect", "stroke": "#F2E9DC", "strokeWidth": 2},
             "encoding": {"x": {"field": "cylinders", "type": "ordinal", "title": "Cylinders", "axis": {"labelAngle": 0}},
                          "y": {"field": "origin", "type": "nominal", "title": None},
                          "color": {"field": "count", "type": "quantitative", "title": "Cars"}}},
            {"mark": {"type": "text", "fontSize": 13, "fontWeight": "bold"},
             "encoding": {"x": {"field": "cylinders", "type": "ordinal"},
                          "y": {"field": "origin", "type": "nominal"},
                          "text": {"field": "count", "type": "quantitative"},
                          "color": {"condition": {"test": "datum.count > 50", "value": "#F2E9DC"}, "value": "#241E1E"}}}
        ]},
    },
    {
        "id": "tbl2_heatmap_hp", "title": "Heatmap Table — Avg Horsepower by Origin × Cylinders",
        "sql": "SELECT Origin AS origin, CAST(Cylinders AS STRING) AS cylinders, ROUND(AVG(Horsepower),0) AS avg_hp FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL GROUP BY Origin, Cylinders",
        "fields": ["origin", "cylinders", "avg_hp"],
        "w": 3,
        "spec": {"layer": [
            {"mark": {"type": "rect"},
             "encoding": {"x": {"field": "cylinders", "type": "ordinal", "title": "Cylinders", "axis": {"labelAngle": 0}},
                          "y": {"field": "origin", "type": "nominal", "title": None},
                          "color": {"field": "avg_hp", "type": "quantitative", "title": "Avg HP"}}},
            {"mark": {"type": "text", "fontWeight": "bold"},
             "encoding": {"x": {"field": "cylinders", "type": "ordinal"},
                          "y": {"field": "origin", "type": "nominal"},
                          "text": {"field": "avg_hp", "type": "quantitative"},
                          "color": {"condition": {"test": "datum.avg_hp > 130", "value": "#F2E9DC"}, "value": "#241E1E"}}}
        ]},
    },
]
