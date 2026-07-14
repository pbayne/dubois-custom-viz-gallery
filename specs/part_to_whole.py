"""Part-to-Whole charts (pie, donut, arc with labels, radius-encoded arc,
normalized stacked bar). Specs are Vega-Lite WITHOUT config/data/width/height
(the build script injects Du Bois config + databricks_query binding + container
sizing). Each chart binds to a dataset defined by `sql`; `fields` lists every
column the spec references (must match the SQL output aliases)."""

CATEGORY = "Part-to-Whole"

CHARTS = [
    {
        "id": "ptw_pie", "title": "Pie — Weather Days by Type",
        "sql": "SELECT weather, COUNT(*) AS count FROM pb_demo.custom_gallery.seattle_weather GROUP BY weather",
        "fields": ["weather", "count"],
        "spec": {"mark": {"type": "arc", "tooltip": True},
                 "encoding": {"theta": {"field": "count", "type": "quantitative", "stack": True},
                              "color": {"field": "weather", "type": "nominal", "title": "Weather"}}},
    },
    {
        "id": "ptw_donut", "title": "Donut — Cars by Origin",
        "sql": "SELECT Origin AS origin, COUNT(*) AS count FROM pb_demo.custom_gallery.cars GROUP BY Origin",
        "fields": ["origin", "count"],
        "spec": {"mark": {"type": "arc", "innerRadius": 60, "tooltip": True},
                 "encoding": {"theta": {"field": "count", "type": "quantitative", "stack": True},
                              "color": {"field": "origin", "type": "nominal", "title": "Origin"}}},
    },
    {
        "id": "ptw_pie_pct", "title": "Pie with % Labels — Cars by Origin",
        "sql": "SELECT Origin AS origin, COUNT(*) AS count FROM pb_demo.custom_gallery.cars GROUP BY Origin",
        "fields": ["origin", "count"],
        "spec": {"transform": [
                    {"joinaggregate": [{"op": "sum", "field": "count", "as": "total"}]},
                    {"calculate": "datum.count / datum.total", "as": "pct"}],
                 "encoding": {"theta": {"field": "count", "type": "quantitative", "stack": True},
                              "color": {"field": "origin", "type": "nominal", "title": "Origin"}},
                 "layer": [
                    {"mark": {"type": "arc", "outerRadius": 90, "tooltip": True}},
                    {"mark": {"type": "text", "radius": 110, "fontWeight": "bold"},
                     "encoding": {"text": {"field": "pct", "type": "quantitative", "format": ".0%"}}}
                 ]},
    },
    {
        "id": "ptw_arc_radius", "title": "Radius-Encoded Arc — Cars by Cylinders",
        "sql": "SELECT CAST(Cylinders AS STRING) AS cylinders, COUNT(*) AS count FROM pb_demo.custom_gallery.cars GROUP BY Cylinders",
        "fields": ["cylinders", "count"],
        "spec": {"mark": {"type": "arc", "innerRadius": 20, "stroke": "#fff", "tooltip": True},
                 "encoding": {"theta": {"field": "count", "type": "quantitative", "stack": True},
                              "radius": {"field": "count", "type": "quantitative",
                                         "scale": {"type": "sqrt", "zero": True, "rangeMin": 20}},
                              "color": {"field": "cylinders", "type": "nominal", "title": "Cylinders"}}},
    },
    {
        "id": "ptw_norm_bar", "title": "Normalized Bar — Cylinder Mix within Origin",
        "sql": "SELECT Origin AS origin, CAST(Cylinders AS STRING) AS cylinders, COUNT(*) AS count FROM pb_demo.custom_gallery.cars GROUP BY Origin, Cylinders",
        "fields": ["origin", "cylinders", "count"],
        "spec": {"mark": "bar",
                 "encoding": {"y": {"field": "origin", "type": "nominal", "title": None},
                              "x": {"field": "count", "type": "quantitative", "stack": "normalize", "title": "Share"},
                              "color": {"field": "cylinders", "type": "nominal", "title": "Cylinders"}}},
    },
    {
        "id": "ptw_donut_genre", "title": "Donut — Top 6 Movie Genres",
        "sql": "SELECT Major_Genre AS genre, COUNT(*) AS count FROM pb_demo.custom_gallery.movies WHERE Major_Genre IS NOT NULL AND Major_Genre <> 'None' GROUP BY Major_Genre ORDER BY count DESC LIMIT 6",
        "fields": ["genre", "count"],
        "spec": {"mark": {"type": "arc", "innerRadius": 60, "tooltip": True},
                 "encoding": {"theta": {"field": "count", "type": "quantitative", "stack": True},
                              "color": {"field": "genre", "type": "nominal", "title": "Genre"}}},
    },
    {
        "id": "ptw2_pyramid_pie", "title": "Pyramid Pie — Weather Days (equal angle, radius = count)",
        "sql": "SELECT weather, COUNT(*) AS count FROM pb_demo.custom_gallery.seattle_weather GROUP BY weather",
        "fields": ["weather", "count"],
        "spec": {"transform": [{"calculate": "1", "as": "one"}],
                 "mark": {"type": "arc", "stroke": "#fff", "tooltip": True},
                 "encoding": {"theta": {"field": "one", "type": "quantitative", "stack": True},
                              "radius": {"field": "count", "type": "quantitative",
                                         "scale": {"type": "sqrt", "zero": True, "rangeMin": 20}},
                              "color": {"field": "weather", "type": "nominal", "title": "Weather"}}},
    },
    {
        "id": "g3_arc_pie_normalize_tooltip", "title": "Pie — Films by MPAA Rating (normalized, tooltip)",
        "sql": "SELECT MPAA_Rating AS rating, COUNT(*) AS count FROM pb_demo.custom_gallery.movies WHERE MPAA_Rating IN ('G','PG','PG-13','R','NC-17') GROUP BY MPAA_Rating",
        "fields": ["rating", "count"],
        "spec": {"mark": {"type": "arc", "tooltip": True},
                 "encoding": {"theta": {"field": "count", "type": "quantitative", "stack": "normalize"},
                              "color": {"field": "rating", "type": "nominal", "title": "MPAA Rating"},
                              "tooltip": [{"field": "rating", "type": "nominal", "title": "Rating"},
                                          {"field": "count", "type": "quantitative", "title": "Films"}]}},
    },
    {
        "id": "ptw2_pie_labels", "title": "Pie with Labels — Weather Days by Type",
        "sql": "SELECT weather, COUNT(*) AS count FROM pb_demo.custom_gallery.seattle_weather GROUP BY weather",
        "fields": ["weather", "count"],
        "spec": {"encoding": {"theta": {"field": "count", "type": "quantitative", "stack": True},
                              "color": {"field": "weather", "type": "nominal", "title": "Weather"}},
                 "layer": [
                    {"mark": {"type": "arc", "outerRadius": 90, "tooltip": True}},
                    {"mark": {"type": "text", "radius": 110, "fontWeight": "bold"},
                     "encoding": {"text": {"field": "count", "type": "quantitative"}}}
                 ]},
    },
]
