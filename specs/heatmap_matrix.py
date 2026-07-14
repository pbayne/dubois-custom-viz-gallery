"""Heatmap & Matrix charts. Specs are Vega-Lite WITHOUT config/data/width/height
(the build script injects Du Bois config + databricks_query binding + container
sizing). Each chart binds to a dataset defined by `sql`; `fields` lists every
column the spec references (must match the SQL output aliases)."""

CATEGORY = "Heatmap & Matrix"

CHARTS = [
    {
        "id": "hm_weather_temp", "title": "Heatmap — Avg Max Temp by Month & Year",
        "sql": "SELECT month(date) AS month, year(date) AS year, ROUND(AVG(temp_max),1) AS avg_temp FROM pb_demo.custom_gallery.seattle_weather GROUP BY month(date), year(date)",
        "fields": ["month", "year", "avg_temp"],
        "w": 3, "h": 7,
        "spec": {"mark": {"type": "rect"},
                 "encoding": {"x": {"field": "year", "type": "ordinal", "title": "Year", "axis": {"labelAngle": 0}},
                              "y": {"field": "month", "type": "ordinal", "title": "Month"},
                              "color": {"field": "avg_temp", "type": "quantitative", "title": "Avg °C"}}},
    },
    {
        "id": "hm_github_punchcard", "title": "GitHub Punchcard — Activity by Hour & Weekday",
        "sql": "SELECT hour(time) AS hour, dayofweek(time) AS dow, SUM(count) AS total FROM pb_demo.custom_gallery.github GROUP BY hour(time), dayofweek(time)",
        "fields": ["hour", "dow", "total"],
        "w": 3, "h": 7,
        "spec": {"mark": {"type": "circle"},
                 "encoding": {"x": {"field": "hour", "type": "ordinal", "title": "Hour of Day", "axis": {"labelAngle": 0}},
                              "y": {"field": "dow", "type": "ordinal", "title": "Day of Week"},
                              "size": {"field": "total", "type": "quantitative", "title": "Commits", "legend": None},
                              "color": {"field": "total", "type": "quantitative", "title": "Commits"}}},
    },
    {
        "id": "hm_cars_2dhist", "title": "2D Histogram — Horsepower vs MPG",
        "sql": "SELECT Horsepower AS horsepower, Miles_per_Gallon AS mpg FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL AND Miles_per_Gallon IS NOT NULL",
        "fields": ["horsepower", "mpg"],
        "spec": {"mark": {"type": "rect"},
                 "encoding": {"x": {"field": "horsepower", "type": "quantitative", "bin": {"maxbins": 12}, "title": "Horsepower"},
                              "y": {"field": "mpg", "type": "quantitative", "bin": {"maxbins": 12}, "title": "Miles per Gallon"},
                              "color": {"aggregate": "count", "type": "quantitative", "title": "Count"}}},
    },
    {
        "id": "hm_precip_calendar", "title": "Calendar Heatmap — Avg Precipitation by Day",
        "sql": "SELECT month(date) AS month, day(date) AS day, ROUND(AVG(precipitation),1) AS avg_precip FROM pb_demo.custom_gallery.seattle_weather GROUP BY month(date), day(date)",
        "fields": ["month", "day", "avg_precip"],
        "w": 3, "h": 7,
        "spec": {"mark": {"type": "rect"},
                 "encoding": {"x": {"field": "day", "type": "ordinal", "title": "Day of Month", "axis": {"labelAngle": 0}},
                              "y": {"field": "month", "type": "ordinal", "title": "Month"},
                              "color": {"field": "avg_precip", "type": "quantitative", "title": "Precip (mm)"}}},
    },
    {
        "id": "hm_movies_genre_rating", "title": "Movie Count — Genre × MPAA Rating",
        "sql": "SELECT Major_Genre AS genre, MPAA_Rating AS rating, COUNT(*) AS count FROM pb_demo.custom_gallery.movies WHERE Major_Genre IS NOT NULL AND MPAA_Rating IS NOT NULL GROUP BY Major_Genre, MPAA_Rating",
        "fields": ["genre", "rating", "count"],
        "w": 3, "h": 7,
        "spec": {"layer": [
            {"mark": {"type": "rect"},
             "encoding": {"x": {"field": "rating", "type": "nominal", "title": "MPAA Rating", "axis": {"labelAngle": 0}},
                          "y": {"field": "genre", "type": "nominal", "title": None},
                          "color": {"field": "count", "type": "quantitative", "title": "Films"}}},
            {"mark": {"type": "text", "fontSize": 10},
             "encoding": {"x": {"field": "rating", "type": "nominal"},
                          "y": {"field": "genre", "type": "nominal"},
                          "text": {"field": "count", "type": "quantitative"},
                          "color": {"condition": {"test": "datum.count > 60", "value": "white"}, "value": "black"}}}
        ]},
    },
    {
        "id": "hm_corr_matrix", "title": "Count Matrix — Cylinders × Origin",
        "sql": "SELECT CAST(Cylinders AS STRING) AS cylinders, Origin AS origin, COUNT(*) AS count FROM pb_demo.custom_gallery.cars GROUP BY Cylinders, Origin",
        "fields": ["cylinders", "origin", "count"],
        "spec": {"layer": [
            {"mark": {"type": "rect"},
             "encoding": {"x": {"field": "cylinders", "type": "ordinal", "title": "Cylinders", "axis": {"labelAngle": 0}},
                          "y": {"field": "origin", "type": "nominal", "title": None},
                          "color": {"field": "count", "type": "quantitative", "title": "Count"}}},
            {"mark": {"type": "text", "fontSize": 11},
             "encoding": {"x": {"field": "cylinders", "type": "ordinal"},
                          "y": {"field": "origin", "type": "nominal"},
                          "text": {"field": "count", "type": "quantitative"},
                          "color": {"condition": {"test": "datum.count > 100", "value": "white"}, "value": "black"}}}
        ]},
    },
    {
        "id": "hm_weather_type", "title": "Weather Days — Type × Month",
        "sql": "SELECT month(date) AS month, weather, COUNT(*) AS count FROM pb_demo.custom_gallery.seattle_weather GROUP BY month(date), weather",
        "fields": ["month", "weather", "count"],
        "w": 3, "h": 7,
        "spec": {"layer": [
            {"mark": {"type": "rect"},
             "encoding": {"x": {"field": "month", "type": "ordinal", "title": "Month", "axis": {"labelAngle": 0}},
                          "y": {"field": "weather", "type": "nominal", "title": None},
                          "color": {"field": "count", "type": "quantitative", "title": "Days"}}},
            {"mark": {"type": "text", "fontSize": 10},
             "encoding": {"x": {"field": "month", "type": "ordinal"},
                          "y": {"field": "weather", "type": "nominal"},
                          "text": {"field": "count", "type": "quantitative"},
                          "color": {"condition": {"test": "datum.count > 60", "value": "white"}, "value": "black"}}}
        ]},
    },
    {
        "id": "hm2_stocks_lasagna", "title": "Lasagna Plot — Stock Price by Month & Symbol",
        "sql": "SELECT date_format(date, 'yyyy-MM') AS month, symbol, ROUND(AVG(price),2) AS avg_price FROM pb_demo.custom_gallery.stocks GROUP BY date_format(date, 'yyyy-MM'), symbol",
        "fields": ["month", "symbol", "avg_price"],
        "w": 3, "h": 7,
        "spec": {"mark": {"type": "rect"},
                 "encoding": {"x": {"field": "month", "type": "ordinal", "title": "Month", "axis": {"labelAngle": -90, "labelOverlap": True}},
                              "y": {"field": "symbol", "type": "nominal", "title": None},
                              "color": {"field": "avg_price", "type": "quantitative", "title": "Avg Price"}}},
    },
    {
        "id": "hm2_precip_annual", "title": "Annual Heatmap — Total Precipitation by Month & Year",
        "sql": "SELECT month(date) AS month, year(date) AS year, ROUND(SUM(precipitation),1) AS total_precip FROM pb_demo.custom_gallery.seattle_weather GROUP BY month(date), year(date)",
        "fields": ["month", "year", "total_precip"],
        "w": 3, "h": 7,
        "spec": {"mark": {"type": "rect"},
                 "encoding": {"x": {"field": "year", "type": "ordinal", "title": "Year", "axis": {"labelAngle": 0}},
                              "y": {"field": "month", "type": "ordinal", "title": "Month"},
                              "color": {"field": "total_precip", "type": "quantitative", "title": "Precip (mm)"}}},
    },
]
