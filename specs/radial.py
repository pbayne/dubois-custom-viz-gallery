"""Radial charts (rose/coxcomb bars, progress gauge, radial bars where radius
encodes value). Specs are Vega-Lite WITHOUT config/data/width/height (the build
script injects Du Bois config + databricks_query binding + container sizing).
Each chart binds to a dataset defined by `sql`; `fields` lists every column the
spec references (must match the SQL output aliases)."""

CATEGORY = "Radial"

CHARTS = [
    {
        "id": "rad_rose_deaths", "title": "Rose Chart — Deaths by Disaster (Top 8)",
        "sql": "SELECT Entity AS entity, SUM(Deaths) AS deaths FROM pb_demo.custom_gallery.disasters WHERE Entity <> 'All natural disasters' GROUP BY Entity ORDER BY deaths DESC LIMIT 8",
        "fields": ["entity", "deaths"],
        "spec": {"mark": {"type": "arc", "innerRadius": 20, "stroke": "#fff", "tooltip": True},
                 "encoding": {"theta": {"field": "entity", "type": "nominal"},
                              "radius": {"field": "deaths", "type": "quantitative",
                                         "scale": {"type": "sqrt", "zero": True}, "title": "Deaths"},
                              "color": {"field": "entity", "type": "nominal", "title": "Disaster"}}},
    },
    {
        "id": "rad_gauge", "title": "Progress Ring — Avg MPG vs 50 mpg Target",
        "sql": "SELECT 'Used' AS segment, ROUND(AVG(Miles_per_Gallon),1) AS value FROM pb_demo.custom_gallery.cars UNION ALL SELECT 'Headroom' AS segment, ROUND(50 - AVG(Miles_per_Gallon),1) AS value FROM pb_demo.custom_gallery.cars",
        "fields": ["segment", "value"],
        "spec": {"mark": {"type": "arc", "innerRadius": 65, "outerRadius": 95, "tooltip": True},
                 "encoding": {"theta": {"field": "value", "type": "quantitative", "stack": True},
                              "color": {"field": "segment", "type": "nominal",
                                        "scale": {"domain": ["Used", "Headroom"],
                                                  "range": ["#5593F7", "#E4E4E4"]},
                                        "title": None}}},
    },
    {
        "id": "rad_month_counts", "title": "Radial Bar — Weather Days by Month",
        "sql": "SELECT month(date) AS month, COUNT(*) AS count FROM pb_demo.custom_gallery.seattle_weather GROUP BY month(date) ORDER BY month",
        "fields": ["month", "count"],
        "spec": {"mark": {"type": "arc", "innerRadius": 20, "stroke": "#fff", "tooltip": True},
                 "encoding": {"theta": {"field": "month", "type": "ordinal"},
                              "radius": {"field": "count", "type": "quantitative",
                                         "scale": {"type": "sqrt", "zero": True}, "title": "Days"},
                              "color": {"field": "month", "type": "ordinal", "title": "Month"}}},
    },
    {
        "id": "rad_weather_radius", "title": "Radial Plot — Weather Type Frequency",
        "sql": "SELECT weather, COUNT(*) AS count FROM pb_demo.custom_gallery.seattle_weather GROUP BY weather",
        "fields": ["weather", "count"],
        "spec": {"mark": {"type": "arc", "innerRadius": 20, "stroke": "#fff", "tooltip": True},
                 "encoding": {"theta": {"field": "count", "type": "quantitative", "stack": True},
                              "radius": {"field": "count", "type": "quantitative",
                                         "scale": {"type": "sqrt", "zero": True, "rangeMin": 20}},
                              "color": {"field": "weather", "type": "nominal", "title": "Weather"}}},
    },
    {
        "id": "rad_temp_month", "title": "Radial Bar — Avg High Temp by Month",
        "sql": "SELECT month(date) AS month, ROUND(AVG(temp_max),1) AS avg_temp FROM pb_demo.custom_gallery.seattle_weather GROUP BY month(date) ORDER BY month",
        "fields": ["month", "avg_temp"],
        "spec": {"mark": {"type": "arc", "innerRadius": 20, "stroke": "#fff", "tooltip": True},
                 "encoding": {"theta": {"field": "month", "type": "ordinal"},
                              "radius": {"field": "avg_temp", "type": "quantitative",
                                         "scale": {"type": "linear", "zero": True}, "title": "Avg °C"},
                              "color": {"field": "avg_temp", "type": "quantitative", "title": "Avg °C"}}},
    },
]
