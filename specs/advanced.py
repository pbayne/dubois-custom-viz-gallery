"""Advanced & Layered. Specs are Vega-Lite WITHOUT config/data/width/height
(the build script injects Du Bois config + databricks_query binding + container
sizing). Candlestick, waterfall (window transform), bar+line on one shared y,
ranged dot plot, error bars, slope chart, histogram+rule, conditional highlight,
and a labeled annotation rule."""

CATEGORY = "Advanced & Layered"

CHARTS = [
    {
        "id": "adv_candlestick", "title": "Candlestick — OHLC with Signal",
        "sql": "SELECT date, CAST(open AS DOUBLE) AS open, CAST(high AS DOUBLE) AS high, CAST(low AS DOUBLE) AS low, CAST(close AS DOUBLE) AS close, signal FROM pb_demo.custom_gallery.ohlc ORDER BY date",
        "fields": ["date", "open", "high", "low", "close", "signal"],
        "w": 3,
        "spec": {"encoding": {"x": {"field": "date", "type": "temporal", "title": None},
                              "color": {"field": "signal", "type": "nominal", "title": "Signal"}},
                 "layer": [
                     {"mark": {"type": "rule"},
                      "encoding": {"y": {"field": "low", "type": "quantitative", "scale": {"zero": False}, "title": "Price ($)"},
                                   "y2": {"field": "high"}}},
                     {"mark": {"type": "bar", "size": 6},
                      "encoding": {"y": {"field": "open", "type": "quantitative"},
                                   "y2": {"field": "close"}}}
                 ]},
    },
    {
        "id": "adv_waterfall", "title": "Waterfall — Monthly Change with Running Total",
        "sql": "SELECT * FROM VALUES ('Jan',1,4000.0),('Feb',2,1707.0),('Mar',3,-1425.0),('Apr',4,-1030.0),('May',5,1812.0),('Jun',6,-1067.0),('Jul',7,-1481.0),('Aug',8,1228.0),('Sep',9,1176.0),('Oct',10,1146.0),('Nov',11,1205.0),('Dec',12,-1388.0) AS t(month, ord, amount)",
        "fields": ["month", "ord", "amount"],
        "w": 3,
        "spec": {"transform": [
                    {"window": [{"op": "sum", "field": "amount", "as": "cumulative"}],
                     "sort": [{"field": "ord"}], "frame": [None, 0]},
                    {"calculate": "datum.cumulative - datum.amount", "as": "previous"}],
                 "layer": [
                     {"mark": {"type": "bar", "size": 18},
                      "encoding": {"x": {"field": "month", "type": "nominal", "sort": {"field": "ord"}, "axis": {"labelAngle": 0}, "title": None},
                                   "y": {"field": "previous", "type": "quantitative", "title": "Cumulative"},
                                   "y2": {"field": "cumulative"},
                                   "color": {"condition": {"test": "datum.amount >= 0", "value": "#3E7D53"}, "value": "#DC4B34"}}},
                     {"mark": {"type": "text", "dy": -6, "fontSize": 10},
                      "encoding": {"x": {"field": "month", "type": "nominal", "sort": {"field": "ord"}},
                                   "y": {"field": "cumulative", "type": "quantitative"},
                                   "text": {"field": "cumulative", "type": "quantitative", "format": ".0f"}}}
                 ]},
    },
    {
        "id": "adv_bar_line", "title": "Bar + Line (Shared Y) — Rainy Days & Cumulative",
        "sql": "SELECT month(date) AS month, COUNT(*) AS n FROM pb_demo.custom_gallery.seattle_weather WHERE weather='rain' GROUP BY month(date) ORDER BY month",
        "fields": ["month", "n"],
        "w": 3,
        "spec": {"transform": [
                    {"window": [{"op": "sum", "field": "n", "as": "cumulative"}], "sort": [{"field": "month"}]}],
                 "encoding": {"x": {"field": "month", "type": "ordinal", "axis": {"labelAngle": 0}, "title": "Month"}},
                 "layer": [
                     {"mark": {"type": "bar", "color": "#8FB3C7"},
                      "encoding": {"y": {"field": "n", "type": "quantitative", "title": "Rainy days"}}},
                     {"mark": {"type": "line", "point": True, "color": "#DC4B34"},
                      "encoding": {"y": {"field": "cumulative", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "adv_ranged_dot", "title": "Ranged Dot Plot — Horsepower Range by Origin",
        "sql": "SELECT Origin AS origin, MIN(Horsepower) AS min_hp, MAX(Horsepower) AS max_hp FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL GROUP BY Origin",
        "fields": ["origin", "min_hp", "max_hp"],
        "w": 3,
        "spec": {"encoding": {"y": {"field": "origin", "type": "nominal", "title": None}},
                 "layer": [
                     {"mark": {"type": "rule", "color": "#B7A98F"},
                      "encoding": {"x": {"field": "min_hp", "type": "quantitative", "title": "Horsepower"},
                                   "x2": {"field": "max_hp"}}},
                     {"transform": [{"fold": ["min_hp", "max_hp"], "as": ["metric", "hp"]}],
                      "mark": {"type": "point", "filled": True, "size": 120},
                      "encoding": {"x": {"field": "hp", "type": "quantitative"},
                                   "color": {"field": "metric", "type": "nominal", "title": None}}}
                 ]},
    },
    {
        "id": "adv_error_bars", "title": "Error Bars — Mean MPG ± CI by Cylinders",
        "sql": "SELECT CAST(Cylinders AS STRING) AS cylinders, Miles_per_Gallon AS mpg FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL",
        "fields": ["cylinders", "mpg"],
        "w": 3,
        "spec": {"encoding": {"y": {"field": "cylinders", "type": "ordinal", "title": "Cylinders"}},
                 "layer": [
                     {"mark": {"type": "errorbar", "extent": "ci", "color": "#F4E3C9"},
                      "encoding": {"x": {"field": "mpg", "type": "quantitative", "title": "Miles per Gallon", "scale": {"zero": False}}}},
                     {"mark": {"type": "point", "filled": True, "size": 90, "color": "#DC4B34"},
                      "encoding": {"x": {"aggregate": "mean", "field": "mpg", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "adv_slope", "title": "Slope Chart — Life Expectancy 1955 vs 2005",
        "sql": "SELECT country, CAST(year AS STRING) AS year, life_expect FROM pb_demo.custom_gallery.gapminder WHERE year IN (1955,2005) AND country IN ('India','China','United States','Japan','Germany','Brazil') ORDER BY year",
        "fields": ["country", "year", "life_expect"],
        "w": 3,
        "spec": {"mark": {"type": "line", "point": True},
                 "encoding": {"x": {"field": "year", "type": "ordinal", "title": None, "axis": {"labelAngle": 0}},
                              "y": {"field": "life_expect", "type": "quantitative", "title": "Life expectancy", "scale": {"zero": False}},
                              "color": {"field": "country", "type": "nominal", "title": "Country"}}},
    },
    {
        "id": "adv_histogram_rule", "title": "Histogram + Mean Rule — Horsepower",
        "sql": "SELECT Horsepower AS horsepower FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["horsepower"],
        "w": 3,
        "spec": {"layer": [
            {"mark": {"type": "bar"},
             "encoding": {"x": {"field": "horsepower", "type": "quantitative", "bin": {"maxbins": 20}, "title": "Horsepower"},
                          "y": {"aggregate": "count", "type": "quantitative", "title": "Count"}}},
            {"mark": {"type": "rule", "color": "#DC4B34", "strokeWidth": 2},
             "encoding": {"x": {"aggregate": "mean", "field": "horsepower", "type": "quantitative"}}}
        ]},
    },
    {
        "id": "adv_highlight", "title": "Conditional Highlight — Genres Above 7.0",
        "sql": "SELECT Major_Genre AS genre, ROUND(AVG(IMDB_Rating),2) AS avg_rating FROM pb_demo.custom_gallery.movies WHERE Major_Genre IS NOT NULL AND Major_Genre <> '' AND IMDB_Rating IS NOT NULL GROUP BY Major_Genre",
        "fields": ["genre", "avg_rating"],
        "w": 3,
        "spec": {"mark": {"type": "bar"},
                 "encoding": {"y": {"field": "genre", "type": "nominal", "sort": "-x", "title": None},
                              "x": {"field": "avg_rating", "type": "quantitative", "title": "Avg IMDB rating", "scale": {"zero": False}},
                              "color": {"condition": {"test": "datum.avg_rating >= 7", "value": "#DC4B34"}, "value": "#B7A98F"}}},
    },
    {
        "id": "adv_annotation", "title": "Annotated Bar — Avg Horsepower with Target",
        "sql": "SELECT CAST(Cylinders AS STRING) AS cylinders, ROUND(AVG(Horsepower),0) AS avg_hp FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL GROUP BY Cylinders",
        "fields": ["cylinders", "avg_hp"],
        "w": 3,
        "spec": {"layer": [
            {"mark": {"type": "bar"},
             "encoding": {"x": {"field": "cylinders", "type": "ordinal", "axis": {"labelAngle": 0}, "title": "Cylinders"},
                          "y": {"field": "avg_hp", "type": "quantitative", "title": "Avg horsepower"}}},
            {"mark": {"type": "rule", "color": "#DC4B34", "strokeDash": [4, 4], "strokeWidth": 2},
             "encoding": {"y": {"datum": 100}}},
            {"mark": {"type": "text", "align": "left", "dx": 4, "dy": -6, "color": "#DC4B34", "fontWeight": "bold", "text": "Target 100 hp"},
             "encoding": {"y": {"datum": 100}, "x": {"datum": "3"}}}
        ]},
    },
    {
        "id": "adv2_diff_from_avg", "title": "Difference from Average — Wheat Price vs Overall Mean",
        "sql": "SELECT CAST(year AS INT) AS year, wheat FROM pb_demo.custom_gallery.wheat WHERE wheat IS NOT NULL ORDER BY year",
        "fields": ["year", "wheat"],
        "w": 3,
        "spec": {"transform": [
                    {"joinaggregate": [{"op": "mean", "field": "wheat", "as": "avg_wheat"}]},
                    {"calculate": "datum.wheat - datum.avg_wheat", "as": "diff"}],
                 "mark": {"type": "bar"},
                 "encoding": {"x": {"field": "year", "type": "ordinal", "axis": {"labelAngle": -45, "labelOverlap": True}, "title": "Year"},
                              "y": {"field": "diff", "type": "quantitative", "title": "Wheat price − overall mean (shillings)"},
                              "color": {"condition": {"test": "datum.diff >= 0", "value": "#3E7D53"}, "value": "#DC4B34"}}},
    },
    {
        "id": "adv2_diff_group_avg", "title": "Difference from Group Average — Price vs Per-Symbol Mean",
        "sql": "SELECT symbol, date, CAST(price AS DOUBLE) AS price FROM pb_demo.custom_gallery.stocks ORDER BY symbol, date",
        "fields": ["symbol", "date", "price"],
        "w": 3,
        "spec": {"transform": [
                    {"joinaggregate": [{"op": "mean", "field": "price", "as": "avg_price"}], "groupby": ["symbol"]},
                    {"calculate": "datum.price - datum.avg_price", "as": "diff"}],
                 "mark": {"type": "area", "opacity": 0.6},
                 "encoding": {"x": {"field": "date", "type": "temporal", "title": None},
                              "y": {"field": "diff", "type": "quantitative", "title": "Price − symbol mean ($)"},
                              "color": {"field": "symbol", "type": "nominal", "title": "Symbol"}}},
    },
    {
        "id": "adv2_top_movies", "title": "Top 10 Movies by Worldwide Gross",
        "sql": "SELECT Title AS title, CAST(Worldwide_Gross AS DOUBLE) AS gross FROM pb_demo.custom_gallery.movies WHERE Worldwide_Gross IS NOT NULL ORDER BY gross DESC LIMIT 10",
        "fields": ["title", "gross"],
        "w": 3,
        "spec": {"mark": {"type": "bar", "color": "#8FB3C7"},
                 "encoding": {"y": {"field": "title", "type": "nominal", "sort": "-x", "title": None},
                              "x": {"field": "gross", "type": "quantitative", "title": "Worldwide gross ($)", "axis": {"format": "~s"}}}},
    },
    {
        "id": "adv2_topk_others", "title": "Top 6 Genres + Other",
        "sql": "WITH counts AS (SELECT Major_Genre AS genre, COUNT(*) AS n FROM pb_demo.custom_gallery.movies WHERE Major_Genre IS NOT NULL AND Major_Genre <> '' GROUP BY Major_Genre), ranked AS (SELECT genre, n, ROW_NUMBER() OVER (ORDER BY n DESC) AS rn FROM counts) SELECT genre, n, rn AS ord FROM ranked WHERE rn <= 6 UNION ALL SELECT 'Other' AS genre, SUM(n) AS n, 999 AS ord FROM ranked WHERE rn > 6",
        "fields": ["genre", "n", "ord"],
        "w": 3,
        "spec": {"mark": {"type": "bar"},
                 "encoding": {"y": {"field": "genre", "type": "nominal", "sort": {"field": "ord", "op": "min", "order": "ascending"}, "title": None},
                              "x": {"field": "n", "type": "quantitative", "title": "Number of movies"},
                              "color": {"condition": {"test": "datum.genre == 'Other'", "value": "#B7A98F"}, "value": "#4E79A7"}}},
    },
    {
        "id": "adv2_layer_mean", "title": "Layering Average over Raw — GOOG Price + Mean Rule",
        "sql": "SELECT date, CAST(price AS DOUBLE) AS price FROM pb_demo.custom_gallery.stocks WHERE symbol='GOOG' ORDER BY date",
        "fields": ["date", "price"],
        "w": 3,
        "spec": {"encoding": {"x": {"field": "date", "type": "temporal", "title": None}},
                 "layer": [
                     {"mark": {"type": "line", "color": "#4E79A7"},
                      "encoding": {"y": {"field": "price", "type": "quantitative", "title": "Price ($)"}}},
                     {"mark": {"type": "rule", "color": "#DC4B34", "strokeWidth": 2},
                      "encoding": {"y": {"aggregate": "mean", "field": "price", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "adv2_rolling_avg", "title": "Rolling Average over Raw — S&P 500 with 30-Point MA",
        "sql": "SELECT date, CAST(price AS DOUBLE) AS price FROM pb_demo.custom_gallery.sp500 ORDER BY date",
        "fields": ["date", "price"],
        "w": 3,
        "spec": {"encoding": {"x": {"field": "date", "type": "temporal", "title": None}},
                 "layer": [
                     {"mark": {"type": "line", "color": "#C9C0B1", "opacity": 0.7},
                      "encoding": {"y": {"field": "price", "type": "quantitative", "title": "Price"}}},
                     {"transform": [
                          {"window": [{"op": "mean", "field": "price", "as": "rolling_mean"}],
                           "frame": [-15, 15], "sort": [{"field": "date"}]}],
                      "mark": {"type": "line", "color": "#DC4B34", "strokeWidth": 2},
                      "encoding": {"y": {"field": "rolling_mean", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "adv2_ci_band", "title": "Line with Confidence Band — Monthly Max Temperature",
        "sql": "SELECT month(date) AS month, temp_max FROM pb_demo.custom_gallery.seattle_weather WHERE temp_max IS NOT NULL",
        "fields": ["month", "temp_max"],
        "w": 3,
        "spec": {"encoding": {"x": {"field": "month", "type": "ordinal", "axis": {"labelAngle": 0}, "title": "Month"}},
                 "layer": [
                     {"mark": {"type": "errorband", "extent": "ci", "borders": False, "color": "#8FB3C7"},
                      "encoding": {"y": {"field": "temp_max", "type": "quantitative", "title": "Max temperature (°C)", "scale": {"zero": False}}}},
                     {"mark": {"type": "line", "color": "#F4E3C9"},
                      "encoding": {"y": {"aggregate": "mean", "field": "temp_max", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "adv2_bullet", "title": "Bullet Chart — Revenue vs Target (US$ thousands)",
        "sql": "SELECT * FROM VALUES ('Revenue', 150.0, 225.0, 300.0, 275.0, 250.0) AS t(category, poor, ok, good, measure, target)",
        "fields": ["category", "poor", "ok", "good", "measure", "target"],
        "w": 3, "h": 4,
        "spec": {"encoding": {"y": {"field": "category", "type": "nominal", "title": None}},
                 "layer": [
                     {"mark": {"type": "bar", "color": "#E5E0D8"},
                      "encoding": {"x": {"field": "good", "type": "quantitative", "title": "US$ (thousands)"}}},
                     {"mark": {"type": "bar", "color": "#C9C0B1"},
                      "encoding": {"x": {"field": "ok", "type": "quantitative"}}},
                     {"mark": {"type": "bar", "color": "#B7A98F"},
                      "encoding": {"x": {"field": "poor", "type": "quantitative"}}},
                     {"mark": {"type": "bar", "color": "#F4E3C9", "size": 12},
                      "encoding": {"x": {"field": "measure", "type": "quantitative"}}},
                     {"mark": {"type": "tick", "color": "#DC4B34", "thickness": 3, "size": 34},
                      "encoding": {"x": {"field": "target", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "adv2_wheat_wages", "title": "Wheat and Wages — Shared Axis (Playfair)",
        "sql": "SELECT CAST(year AS INT) AS year, wheat, wages FROM pb_demo.custom_gallery.wheat WHERE wheat IS NOT NULL ORDER BY year",
        "fields": ["year", "wheat", "wages"],
        "w": 3,
        "spec": {"encoding": {"x": {"field": "year", "type": "quantitative", "axis": {"format": "d"}, "title": "Year"}},
                 "layer": [
                     {"mark": {"type": "area", "color": "#B7A98F", "opacity": 0.7},
                      "encoding": {"y": {"field": "wheat", "type": "quantitative", "title": "Shillings"}}},
                     {"mark": {"type": "line", "color": "#DC4B34", "strokeWidth": 2},
                      "encoding": {"y": {"field": "wages", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "adv2_highlight_rect", "title": "Highlighted Range — GOOG Price with 2008–09 Rect",
        "sql": "SELECT date, CAST(price AS DOUBLE) AS price FROM pb_demo.custom_gallery.stocks WHERE symbol='GOOG' ORDER BY date",
        "fields": ["date", "price"],
        "w": 3,
        "spec": {"layer": [
                     {"mark": {"type": "rect", "color": "#DC4B34", "opacity": 0.12},
                      "encoding": {"x": {"datum": {"expr": "datetime(2008, 0, 1)"}, "type": "temporal"},
                                   "x2": {"datum": {"expr": "datetime(2010, 0, 1)"}}}},
                     {"mark": {"type": "line", "color": "#4E79A7"},
                      "encoding": {"x": {"field": "date", "type": "temporal", "title": None},
                                   "y": {"field": "price", "type": "quantitative", "title": "Price ($)"}}}
                 ]},
    },
    {
        "id": "adv2_likert", "title": "Likert Ratings — Distribution with Median",
        "sql": "SELECT * FROM VALUES ('Ease of use',4),('Ease of use',5),('Ease of use',4),('Ease of use',3),('Ease of use',5),('Ease of use',4),('Value',3),('Value',3),('Value',4),('Value',2),('Value',3),('Value',4),('Support',5),('Support',4),('Support',5),('Support',5),('Support',3),('Support',4),('Docs',2),('Docs',3),('Docs',2),('Docs',4),('Docs',3),('Docs',1) AS t(question, rating)",
        "fields": ["question", "rating"],
        "w": 3,
        "spec": {"encoding": {"y": {"field": "question", "type": "nominal", "title": None},
                              "x": {"field": "rating", "type": "quantitative", "scale": {"domain": [1, 5]}, "axis": {"values": [1, 2, 3, 4, 5]}, "title": "Rating (1–5)"}},
                 "layer": [
                     {"mark": {"type": "tick", "color": "#B7A98F", "opacity": 0.5, "thickness": 2, "size": 22},
                      "encoding": {"x": {"field": "rating", "type": "quantitative"}}},
                     {"mark": {"type": "point", "filled": True, "color": "#DC4B34", "size": 130},
                      "encoding": {"x": {"aggregate": "median", "field": "rating", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "g3_lookup", "title": "Lookup Join — Stock Prices by Company Name",
        "sql": "SELECT s.date AS date, CAST(s.price AS DOUBLE) AS price, c.company AS company FROM pb_demo.custom_gallery.stocks s JOIN (VALUES ('AAPL','Apple'),('AMZN','Amazon'),('GOOG','Google'),('IBM','IBM'),('MSFT','Microsoft')) AS c(symbol, company) ON s.symbol = c.symbol ORDER BY c.company, s.date",
        "fields": ["date", "price", "company"],
        "w": 3,
        "spec": {"mark": {"type": "line", "strokeWidth": 1.5},
                 "encoding": {"x": {"field": "date", "type": "temporal", "title": None},
                              "y": {"field": "price", "type": "quantitative", "title": "Price ($)"},
                              "color": {"field": "company", "type": "nominal", "title": "Company"}}},
    },
    {
        "id": "g3_window_impute_null", "title": "Impute Nulls — Window Mean of Neighbors",
        "sql": "SELECT * FROM VALUES (1, 5.0),(2, 7.0),(3, CAST(NULL AS DOUBLE)),(4, 8.0),(5, CAST(NULL AS DOUBLE)),(6, 6.0),(7, 9.0),(8, CAST(NULL AS DOUBLE)),(9, 11.0),(10, 10.0),(11, 12.0),(12, CAST(NULL AS DOUBLE)),(13, 14.0),(14, 13.0),(15, 15.0) AS t(t, value)",
        "fields": ["t", "value"],
        "w": 3,
        "spec": {"transform": [
                    {"window": [{"op": "mean", "field": "value", "as": "neighbor_mean"}],
                     "frame": [-1, 1], "sort": [{"field": "t"}]},
                    {"calculate": "isValid(datum.value) ? datum.value : datum.neighbor_mean", "as": "imputed"}],
                 "encoding": {"x": {"field": "t", "type": "quantitative", "axis": {"tickMinStep": 1}, "title": "Sequence"}},
                 "layer": [
                     {"mark": {"type": "line", "color": "#DC4B34", "strokeDash": [4, 3]},
                      "encoding": {"y": {"field": "imputed", "type": "quantitative", "title": "Value (imputed dashed)"}}},
                     {"mark": {"type": "line", "point": True, "color": "#4E79A7"},
                      "encoding": {"y": {"field": "value", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "g3_layer_scatter_errorband_1D_stdev_global_mean", "title": "1D Strip + Global Mean ± Std Dev Band — Horsepower",
        "sql": "SELECT Horsepower AS horsepower FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["horsepower"],
        "w": 3, "h": 4,
        "spec": {"encoding": {"x": {"field": "horsepower", "type": "quantitative", "title": "Horsepower"}},
                 "layer": [
                     {"mark": {"type": "errorband", "extent": "stdev", "color": "#8FB3C7", "borders": True},
                      "encoding": {"x": {"field": "horsepower", "type": "quantitative"}}},
                     {"mark": {"type": "tick", "opacity": 0.4, "color": "#F4E3C9", "thickness": 1},
                      "encoding": {"x": {"field": "horsepower", "type": "quantitative"}}},
                     {"mark": {"type": "rule", "color": "#DC4B34", "strokeWidth": 2},
                      "encoding": {"x": {"aggregate": "mean", "field": "horsepower", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "g3_layer_bar_fruit", "title": "Labeled Bars — Fruit Counts",
        "sql": "SELECT * FROM VALUES ('Apple',28),('Banana',55),('Cherry',43),('Grape',91),('Orange',81),('Peach',53),('Plum',19) AS t(fruit, count)",
        "fields": ["fruit", "count"],
        "w": 3,
        "spec": {"encoding": {"y": {"field": "fruit", "type": "nominal", "sort": "-x", "title": None},
                              "x": {"field": "count", "type": "quantitative", "title": "Count"}},
                 "layer": [
                     {"mark": {"type": "bar", "color": "#8FB3C7"}},
                     {"mark": {"type": "text", "align": "left", "dx": 4, "color": "#F4E3C9"},
                      "encoding": {"text": {"field": "count", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "g3_layer_precipitation_mean", "title": "Mean Precipitation by Month + Overall Mean Rule",
        "sql": "SELECT month(date) AS month, precipitation FROM pb_demo.custom_gallery.seattle_weather WHERE precipitation IS NOT NULL",
        "fields": ["month", "precipitation"],
        "w": 3,
        "spec": {"encoding": {"x": {"field": "month", "type": "ordinal", "axis": {"labelAngle": 0}, "title": "Month"}},
                 "layer": [
                     {"mark": {"type": "bar", "color": "#8FB3C7"},
                      "encoding": {"y": {"aggregate": "mean", "field": "precipitation", "type": "quantitative", "title": "Mean precipitation (mm)"}}},
                     {"mark": {"type": "rule", "color": "#DC4B34", "strokeWidth": 2},
                      "encoding": {"y": {"aggregate": "mean", "field": "precipitation", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "g3_layer_falkensee", "title": "S&P 500 with Annotated Historical Ranges",
        "sql": "SELECT date, CAST(price AS DOUBLE) AS price FROM pb_demo.custom_gallery.sp500 ORDER BY date",
        "fields": ["date", "price"],
        "w": 3,
        "spec": {"layer": [
                     {"mark": {"type": "rect", "color": "#B7A98F", "opacity": 0.18},
                      "encoding": {"x": {"datum": {"expr": "datetime(2000, 2, 1)"}, "type": "temporal"},
                                   "x2": {"datum": {"expr": "datetime(2002, 9, 1)"}}}},
                     {"mark": {"type": "rect", "color": "#DC4B34", "opacity": 0.15},
                      "encoding": {"x": {"datum": {"expr": "datetime(2007, 9, 1)"}, "type": "temporal"},
                                   "x2": {"datum": {"expr": "datetime(2009, 5, 1)"}}}},
                     {"mark": {"type": "text", "color": "#8A7B5C", "align": "left", "dx": 3, "dy": 8, "fontSize": 10, "text": "Dot-com bust"},
                      "encoding": {"x": {"datum": {"expr": "datetime(2000, 2, 1)"}, "type": "temporal"},
                                   "y": {"datum": 1500}}},
                     {"mark": {"type": "text", "color": "#DC4B34", "align": "left", "dx": 3, "dy": 8, "fontSize": 10, "text": "2008 crisis"},
                      "encoding": {"x": {"datum": {"expr": "datetime(2007, 9, 1)"}, "type": "temporal"},
                                   "y": {"datum": 1500}}},
                     {"mark": {"type": "line", "color": "#F4E3C9", "strokeWidth": 1.5},
                      "encoding": {"x": {"field": "date", "type": "temporal", "title": None},
                                   "y": {"field": "price", "type": "quantitative", "title": "S&P 500 index"}}}
                 ]},
    },
    # ── NEW: Ternary Chart ──────────────────────────────────────────
    {
        "id": "adv_ternary", "title": "Ternary Chart — 3-Variable Composition",
        "sql": "SELECT * FROM VALUES ('Luminar',5,50,30),('Crystalport',35,60,20),('Stellaheim',115,40,70),('Mistral Heights',30,45,252),('Verdancia',120,35,2),('Aurelian City',28,48,32),('Solaris Bay',32,458,55),('Sandspire',12,30,55),('Azureon',40,50,15),('Goldcrest',18,28,35) AS t(city, high_val, medium_val, low_val)",
        "fields": ["city", "high_val", "medium_val", "low_val"],
        "w": 6,
        "spec": {
            "title": {"text": "Population by Socioeconomic Level", "anchor": "start", "offset": 20},
            "layer": [
                {"data": {"values": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 0.5, "y": 0.866}]},
                 "mark": {"type": "line", "fill": "#c8edf1", "interpolate": "linear-closed", "stroke": "#888", "strokeWidth": 1, "opacity": 0.3},
                 "encoding": {"x": {"field": "x", "type": "quantitative", "axis": None, "scale": {"domain": [-0.1, 1.1]}},
                              "y": {"field": "y", "type": "quantitative", "axis": None, "scale": {"domain": [-0.1, 0.97]}}}},
                {"data": {"values": [{"x": -0.05, "y": -0.05, "label": "High 100%"}, {"x": 1.05, "y": -0.05, "label": "Low 100%"}, {"x": 0.5, "y": 0.92, "label": "Medium 100%"}]},
                 "mark": {"type": "text", "fontSize": 11},
                 "encoding": {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"}, "text": {"field": "label", "type": "nominal"}}},
                {"data": {"values": [
                    {"x": 0.1, "y": 0, "x2": 0.05, "y2": 0.0866}, {"x": 0.2, "y": 0, "x2": 0.1, "y2": 0.1732},
                    {"x": 0.3, "y": 0, "x2": 0.15, "y2": 0.2598}, {"x": 0.4, "y": 0, "x2": 0.2, "y2": 0.3464},
                    {"x": 0.5, "y": 0, "x2": 0.25, "y2": 0.433}, {"x": 0.6, "y": 0, "x2": 0.3, "y2": 0.5196},
                    {"x": 0.7, "y": 0, "x2": 0.35, "y2": 0.6062}, {"x": 0.8, "y": 0, "x2": 0.4, "y2": 0.6928},
                    {"x": 0.9, "y": 0, "x2": 0.95, "y2": 0.0866}, {"x": 0.8, "y": 0, "x2": 0.9, "y2": 0.1732},
                    {"x": 0.7, "y": 0, "x2": 0.85, "y2": 0.2598}, {"x": 0.6, "y": 0, "x2": 0.8, "y2": 0.3464},
                    {"x": 0.5, "y": 0, "x2": 0.75, "y2": 0.433}, {"x": 0.4, "y": 0, "x2": 0.7, "y2": 0.5196},
                    {"x": 0.3, "y": 0, "x2": 0.65, "y2": 0.6062}, {"x": 0.2, "y": 0, "x2": 0.6, "y2": 0.6928},
                    {"x": 0.05, "y": 0.0866, "x2": 0.95, "y2": 0.0866}, {"x": 0.1, "y": 0.1732, "x2": 0.9, "y2": 0.1732},
                    {"x": 0.15, "y": 0.2598, "x2": 0.85, "y2": 0.2598}, {"x": 0.2, "y": 0.3464, "x2": 0.8, "y2": 0.3464},
                    {"x": 0.25, "y": 0.433, "x2": 0.75, "y2": 0.433}, {"x": 0.3, "y": 0.5196, "x2": 0.7, "y2": 0.5196},
                    {"x": 0.35, "y": 0.6062, "x2": 0.65, "y2": 0.6062}, {"x": 0.4, "y": 0.6928, "x2": 0.6, "y2": 0.6928}]},
                 "mark": {"type": "rule", "stroke": "#aaa", "strokeDash": [2, 2], "opacity": 0.5},
                 "encoding": {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"}, "x2": {"field": "x2"}, "y2": {"field": "y2"}}},
                {"transform": [
                    {"calculate": "datum.high_val + datum.medium_val + datum.low_val", "as": "total"},
                    {"calculate": "datum.high_val / datum.total", "as": "hp"},
                    {"calculate": "datum.medium_val / datum.total", "as": "mp"},
                    {"calculate": "datum.low_val / datum.total", "as": "lp"},
                    {"calculate": "0.5 * (2 * datum.lp + datum.mp)", "as": "x"},
                    {"calculate": "0.866 * datum.mp", "as": "y"},
                    {"calculate": "toString(datum.high_val) + ' (' + toString(round(datum.hp*100,1)) + '%)'", "as": "th"},
                    {"calculate": "toString(datum.medium_val) + ' (' + toString(round(datum.mp*100,1)) + '%)'", "as": "tm"},
                    {"calculate": "toString(datum.low_val) + ' (' + toString(round(datum.lp*100,1)) + '%)'", "as": "tl"},
                    {"calculate": "datum.hp > 0.5 ? '#DC4B34' : datum.mp > 0.5 ? '#D4A017' : datum.lp > 0.5 ? '#3E7D53' : '#5B9BD5'", "as": "clr"}],
                 "encoding": {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"},
                              "tooltip": [{"field": "city", "title": "City"}, {"field": "th", "title": "\u0048igh"}, {"field": "tm", "title": "Medium"}, {"field": "tl", "title": "Low"}]},
                 "layer": [
                    {"mark": {"type": "point", "opacity": 1, "stroke": "#555555", "strokeWidth": 1.5},
                     "encoding": {"fill": {"field": "clr", "type": "nominal", "scale": None, "legend": None},
                                  "size": {"field": "total", "type": "quantitative", "legend": None, "scale": {"range": [50, 500]}}}},
                    {"mark": {"type": "text", "dy": -14, "fontSize": 11},
                     "encoding": {"text": {"field": "city", "type": "nominal"}}}]}
            ]
        },
    },
    # ── NEW: Diverging Stacked Bar with Neutral ─────────────────────
    {
        "id": "adv_diverging_neutral", "title": "Diverging Stacked Bar with Neutral Center",
        "sql": "SELECT * FROM VALUES ('Quality',5,15,30,35,15),('Value',10,20,25,30,15),('Service',3,8,20,40,29),('Speed',15,25,20,25,15),('Support',8,12,35,30,15) AS t(question, strongly_disagree, disagree, neutral, agree, strongly_agree)",
        "fields": ["question", "strongly_disagree", "disagree", "neutral", "agree", "strongly_agree"],
        "w": 6,
        "spec": {
            "transform": [
                {"calculate": "-(datum.strongly_disagree + datum.disagree + datum.neutral/2)", "as": "neg_start"},
                {"calculate": "-(datum.disagree + datum.neutral/2)", "as": "neg_mid"},
                {"calculate": "-datum.neutral/2", "as": "neg_end"},
                {"calculate": "datum.neutral/2", "as": "pos_start"},
                {"calculate": "datum.neutral/2 + datum.agree", "as": "pos_mid"},
                {"calculate": "datum.neutral/2 + datum.agree + datum.strongly_agree", "as": "pos_end"},
                {"fold": ["strongly_disagree", "disagree", "neutral", "agree", "strongly_agree"], "as": ["response", "pct"]}
            ],
            "encoding": {"y": {"field": "question", "type": "nominal", "axis": {"title": None}}},
            "layer": [
                {"mark": {"type": "bar", "height": 20}, "encoding": {
                    "x": {"field": "neg_start", "type": "quantitative", "title": "← Disagree | Agree →", "axis": {"format": ".0f"}},
                    "x2": {"field": "neg_mid"}, "color": {"value": "#DC4B34"}}},
                {"mark": {"type": "bar", "height": 20}, "encoding": {
                    "x": {"field": "neg_mid", "type": "quantitative"}, "x2": {"field": "neg_end"}, "color": {"value": "#F4A582"}}},
                {"mark": {"type": "bar", "height": 20}, "encoding": {
                    "x": {"field": "neg_end", "type": "quantitative"}, "x2": {"field": "pos_start"}, "color": {"value": "#B7A98F"}}},
                {"mark": {"type": "bar", "height": 20}, "encoding": {
                    "x": {"field": "pos_start", "type": "quantitative"}, "x2": {"field": "pos_mid"}, "color": {"value": "#92C5DE"}}},
                {"mark": {"type": "bar", "height": 20}, "encoding": {
                    "x": {"field": "pos_mid", "type": "quantitative"}, "x2": {"field": "pos_end"}, "color": {"value": "#2166AC"}}},
                {"mark": {"type": "rule", "strokeDash": [2, 2], "stroke": "#555555"}, "encoding": {"x": {"datum": 0}}}
            ]
        },
    },
    # ── NEW: Wind Vector Map ────────────────────────────────────────
    {
        "id": "adv_wind_vector", "title": "Wind Vector Map — Point Angle Encoding",
        "sql": "SELECT * FROM VALUES (1,1,45,8),(1,2,90,12),(1,3,135,6),(2,1,180,10),(2,2,225,15),(2,3,270,9),(3,1,315,7),(3,2,0,11),(3,3,60,14),(1,4,120,5),(2,4,200,13),(3,4,340,8) AS t(grid_x, grid_y, wind_dir, wind_speed)",
        "fields": ["grid_x", "grid_y", "wind_dir", "wind_speed"],
        "w": 3,
        "spec": {
            "mark": {"type": "point", "shape": "wedge", "filled": True},
            "encoding": {
                "x": {"field": "grid_x", "type": "quantitative", "title": "Longitude Grid", "axis": {"grid": True}},
                "y": {"field": "grid_y", "type": "quantitative", "title": "Latitude Grid", "axis": {"grid": True}},
                "angle": {"field": "wind_dir", "type": "quantitative", "scale": {"domain": [0, 360]}},
                "size": {"field": "wind_speed", "type": "quantitative", "title": "Speed (kt)", "scale": {"range": [50, 400]}},
                "color": {"field": "wind_speed", "type": "quantitative", "scale": {"scheme": "turbo"}, "title": "Speed"},
                "tooltip": [{"field": "wind_dir", "title": "Direction (°)"}, {"field": "wind_speed", "title": "Speed (kt)"}]
            }
        },
    },
    # ── NEW: Weekly Weather Plot ────────────────────────────────────
    {
        "id": "adv_weekly_weather", "title": "Weekly Weather — Temp Range + Precip + Wind",
        "sql": "SELECT date_format(date, 'd') as day_num, temp_max, temp_min, precipitation, wind, weather FROM pb_demo.custom_gallery.seattle_weather WHERE date_format(date, 'yyyy-MM') = '2012-07' ORDER BY date",
        "fields": ["day_num", "temp_max", "temp_min", "precipitation", "wind", "weather"],
        "w": 6,
        "spec": {
            "encoding": {"x": {"field": "day_num", "type": "ordinal", "title": "Day of Month", "axis": {"labelAngle": 0}}},
            "layer": [
                {"mark": {"type": "bar", "width": 10, "opacity": 0.3},
                 "encoding": {"y": {"field": "temp_min", "type": "quantitative", "title": "Temperature (°F)", "scale": {"zero": False}},
                              "y2": {"field": "temp_max"},
                              "color": {"value": "#B7A98F"},
                              "tooltip": [{"field": "day_num", "title": "Day"}, {"field": "temp_max", "title": "High"}, {"field": "temp_min", "title": "Low"}, {"field": "weather", "title": "Condition"}]}},
                {"mark": {"type": "bar", "width": 3},
                 "encoding": {"y": {"field": "precipitation", "type": "quantitative"},
                              "color": {"value": "#5B9BD5"}}},
                {"mark": {"type": "tick", "thickness": 2},
                 "encoding": {"y": {"field": "wind", "type": "quantitative"},
                              "color": {"value": "#DC4B34"}}}
            ]
        },
    },
    # ── NEW: Dual Axis ──────────────────────────────────────────────
    {
        "id": "adv_dual_axis", "title": "Dual Axis — Bar + Line on Independent Y Scales",
        "sql": "SELECT * FROM VALUES ('Jan',45000,12.5),('Feb',52000,14.2),('Mar',48000,13.1),('Apr',61000,16.8),('May',58000,15.9),('Jun',67000,18.4),('Jul',72000,19.7),('Aug',69000,18.9),('Sep',64000,17.5),('Oct',71000,19.4),('Nov',78000,21.3),('Dec',85000,23.2) AS t(month, revenue, growth_pct)",
        "fields": ["month", "revenue", "growth_pct"],
        "w": 6,
        "spec": {
            "encoding": {"x": {"field": "month", "type": "nominal", "axis": {"labelAngle": 0}, "title": None,
                                "sort": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]}},
            "layer": [
                {"mark": {"type": "bar", "opacity": 0.7},
                 "encoding": {"y": {"field": "revenue", "type": "quantitative", "axis": {"title": "Revenue ($)", "titleColor": "#5B9BD5"}, "scale": {"zero": True}},
                              "color": {"value": "#5B9BD5"}}},
                {"mark": {"type": "line", "point": True, "strokeWidth": 2.5},
                 "encoding": {"y": {"field": "growth_pct", "type": "quantitative",
                                     "axis": {"title": "Growth %", "titleColor": "#DC4B34", "orient": "right"},
                                     "scale": {"zero": True}},
                              "color": {"value": "#DC4B34"}}}
            ],
            "resolve": {"scale": {"y": "independent"}}
        },
    },
    # ── NEW: Gapminder Bubble ───────────────────────────────────────
    {
        "id": "adv_gapminder", "title": "Gapminder Bubble — Life Expectancy vs GDP",
        "sql": "SELECT * FROM VALUES ('US',76.8,37648,282,'Americas'),('China',71.4,3119,1263,'Asia'),('India',63.0,2678,1015,'Asia'),('Japan',81.5,26755,127,'Asia'),('Germany',78.3,25103,82,'Europe'),('Brazil',71.0,7982,174,'Americas'),('UK',78.0,27147,60,'Europe'),('France',79.1,24364,61,'Europe'),('Nigeria',46.6,1089,114,'Africa'),('S. Africa',53.4,7710,45,'Africa'),('Indonesia',68.0,3531,212,'Asia'),('Mexico',74.0,9531,101,'Americas'),('Russia',65.5,7677,146,'Europe'),('Egypt',69.3,4042,68,'Africa'),('Australia',80.4,25370,19,'Oceania') AS t(country, life_exp, gdp_cap, pop_m, continent)",
        "fields": ["country", "life_exp", "gdp_cap", "pop_m", "continent"],
        "w": 6,
        "spec": {
            "mark": {"type": "circle", "opacity": 0.7, "stroke": "#555555", "strokeWidth": 0.5},
            "encoding": {
                "x": {"field": "gdp_cap", "type": "quantitative", "title": "GDP per Capita ($)", "scale": {"type": "log"}, "axis": {"format": "$,d"}},
                "y": {"field": "life_exp", "type": "quantitative", "title": "Life Expectancy (years)", "scale": {"zero": False}},
                "size": {"field": "pop_m", "type": "quantitative", "title": "Population (M)", "scale": {"range": [50, 2000]}},
                "color": {"field": "continent", "type": "nominal", "title": "Continent"},
                "tooltip": [{"field": "country"}, {"field": "life_exp", "title": "Life Exp"}, {"field": "gdp_cap", "title": "GDP/Cap", "format": "$,.0f"}, {"field": "pop_m", "title": "Pop (M)"}]
            }
        },
    },
    # ── NEW: CO2 Dual Period Overlay ────────────────────────────────
    {
        "id": "adv_co2_dual", "title": "CO2 Concentration — Seasonal Cycle Overlay",
        "sql": "SELECT month_num, year_group, co2 FROM (SELECT * FROM VALUES (1,'2020-2022',416.2),(2,'2020-2022',417.1),(3,'2020-2022',418.3),(4,'2020-2022',419.4),(5,'2020-2022',420.8),(6,'2020-2022',419.5),(7,'2020-2022',416.7),(8,'2020-2022',414.8),(9,'2020-2022',414.2),(10,'2020-2022',416.1),(11,'2020-2022',418.0),(12,'2020-2022',419.3),(1,'2023-2025',418.5),(2,'2023-2025',419.8),(3,'2023-2025',421.1),(4,'2023-2025',422.6),(5,'2023-2025',424.1),(6,'2023-2025',422.4),(7,'2023-2025',419.3),(8,'2023-2025',417.2),(9,'2023-2025',416.9),(10,'2023-2025',418.6),(11,'2023-2025',420.5),(12,'2023-2025',421.8) AS t(month_num, year_group, co2)) sub",
        "fields": ["month_num", "year_group", "co2"],
        "w": 3,
        "spec": {
            "encoding": {"x": {"field": "month_num", "type": "ordinal", "title": "Month", "axis": {"labelAngle": 0}}},
            "layer": [
                {"mark": {"type": "area", "opacity": 0.15, "line": True},
                 "encoding": {
                    "y": {"field": "co2", "type": "quantitative", "title": "CO₂ (ppm)", "scale": {"zero": False}},
                    "color": {"field": "year_group", "type": "nominal", "title": "Period"}}},
                {"mark": {"type": "point", "filled": True, "size": 40},
                 "encoding": {
                    "y": {"field": "co2", "type": "quantitative"},
                    "color": {"field": "year_group", "type": "nominal"},
                    "tooltip": [{"field": "year_group", "title": "Period"}, {"field": "month_num", "title": "Month"}, {"field": "co2", "title": "CO₂ ppm"}]}}
            ]
        },
    },

    # ── EXTREME: Beeswarm, Spiral, Periodic Table, Radial Network, Emoji ──
    {'fields': ['origin', 'mpg', 'mpg_bin', 'stack_pos'],
     'id': 'adv_beeswarm',
     'spec': {'layer': [{'encoding': {'color': {'field': 'origin',
                                                'legend': {'orient': 'top-right', 'title': 'Origin'},
                                                'scale': {'domain': ['USA', 'Europe', 'Japan'], 'range': ['#DC4B34', '#3E7D53', '#5B9BD5']},
                                                'type': 'nominal'},
                                      'tooltip': [{'field': 'origin', 'type': 'nominal'}, {'field': 'mpg', 'title': 'MPG', 'type': 'quantitative'},
                                                  {'field': 'stack_pos', 'title': 'Stack Position', 'type': 'quantitative'}],
                                      'x': {'axis': {'grid': False, 'tickCount': 10}, 'field': 'bin', 'scale': {'domain': [8, 42]}, 'title': 'Miles per Gallon', 'type': 'quantitative'},
                                      'y': {'axis': None, 'field': 'y_pos', 'scale': {'domain': [0, 44]}, 'title': None, 'type': 'quantitative'}},
                         'mark': {'opacity': 0.85, 'size': 70, 'stroke': '#F4E3C9', 'strokeWidth': 0.5, 'type': 'circle'}},
                        {'data': {'values': [{'label': 'USA', 'label_y': 7}, {'label': 'Europe', 'label_y': 21}, {'label': 'Japan', 'label_y': 35}]},
                         'encoding': {'color': {'value': '#F4E3C9'}, 'text': {'field': 'label', 'type': 'nominal'}, 'x': {'value': 0}, 'y': {'field': 'label_y', 'type': 'quantitative'}},
                         'mark': {'align': 'right', 'dx': -10, 'fontSize': 11, 'fontWeight': 'bold', 'type': 'text'}}],
              'title': {'anchor': 'start', 'text': 'Beeswarm – MPG Distribution by Origin'},
              'transform': [{'as': 'bin', 'calculate': 'toNumber(datum.mpg_bin)'}, {'as': 'spos', 'calculate': 'toNumber(datum.stack_pos)'}, {'as': 'origin_idx', 'calculate': "datum.origin == 'USA' ? 0 : datum.origin == 'Europe' ? 1 : 2"}, {'as': 'y_pos', 'calculate': 'datum.origin_idx * 14 + datum.spos'}]},
     'sql': '\n'
            'WITH raw_cars AS (\n'
            '  SELECT * FROM VALUES\n'
            "    ('USA', 18), ('USA', 15), ('USA', 16), ('USA', 17), ('USA', 20),\n"
            "    ('USA', 22), ('USA', 14), ('USA', 19), ('USA', 21), ('USA', 25),\n"
            "    ('USA', 13), ('USA', 24), ('USA', 26), ('USA', 12), ('USA', 23),\n"
            "    ('USA', 27), ('USA', 28), ('USA', 11), ('USA', 29), ('USA', 30),\n"
            "    ('Europe', 25), ('Europe', 28), ('Europe', 30), ('Europe', 27),\n"
            "    ('Europe', 32), ('Europe', 26), ('Europe', 29), ('Europe', 31),\n"
            "    ('Europe', 33), ('Europe', 24), ('Europe', 34), ('Europe', 35),\n"
            "    ('Europe', 23), ('Europe', 22), ('Europe', 36),\n"
            "    ('Japan', 30), ('Japan', 33), ('Japan', 35), ('Japan', 28),\n"
            "    ('Japan', 31), ('Japan', 36), ('Japan', 34), ('Japan', 32),\n"
            "    ('Japan', 29), ('Japan', 37), ('Japan', 38), ('Japan', 27),\n"
            "    ('Japan', 39), ('Japan', 40), ('Japan', 26)\n"
            '  AS t(origin, mpg)\n'
            '),\n'
            'binned AS (\n'
            '    SELECT origin, mpg,\n'
            '      FLOOR(mpg / 2) * 2 AS mpg_bin\n'
            '    FROM raw_cars\n'
            '  ),\n'
            '  stacked AS (\n'
            '    SELECT origin, mpg, mpg_bin,\n'
            '      ROW_NUMBER() OVER (PARTITION BY origin, mpg_bin ORDER BY mpg) AS stack_pos\n'
            '    FROM binned\n'
            '  )\n'
            'SELECT origin, mpg, mpg_bin, stack_pos\n'
            'FROM stacked\n',
     'title': 'Beeswarm – MPG by Origin (Force-Packed Dots)',
     'w': 6},
    {'fields': ['seq', 'month_label', 'revenue_k'],
     'id': 'adv_spiral',
     'spec': {'layer': [{'encoding': {'order': {'field': 'seq', 'type': 'quantitative'},
                                      'x': {'axis': None, 'field': 'x', 'type': 'quantitative'},
                                      'y': {'axis': None, 'field': 'y', 'type': 'quantitative'}},
                         'mark': {'color': '#8A7B5C', 'interpolate': 'cardinal', 'opacity': 0.4, 'strokeWidth': 1.5, 'type': 'line'}},
                        {'encoding': {'color': {'field': 'year',
                                                'legend': {'title': 'Year'},
                                                'scale': {'domain': ['2020', '2021', '2022', '2023', '2024'], 'range': ['#B7A98F', '#3E7D53', '#5B9BD5', '#D4A017', '#DC4B34']},
                                                'type': 'nominal'},
                                      'size': {'field': 'revenue_k', 'legend': {'title': 'Revenue ($K)'}, 'scale': {'range': [30, 350]}, 'type': 'quantitative'},
                                      'tooltip': [{'field': 'month_label', 'title': 'Month', 'type': 'nominal'}, {'field': 'revenue_k', 'title': 'Revenue ($K)', 'type': 'quantitative'},
                                                  {'field': 'year', 'title': 'Year', 'type': 'nominal'}],
                                      'x': {'axis': None, 'field': 'x', 'type': 'quantitative'},
                                      'y': {'axis': None, 'field': 'y', 'type': 'quantitative'}},
                         'mark': {'opacity': 0.9, 'stroke': '#555555', 'strokeWidth': 0.5, 'type': 'circle'}},
                        {'encoding': {'color': {'value': '#F4E3C9'},
                                      'text': {'field': 'month_label', 'type': 'nominal'},
                                      'x': {'field': 'x', 'type': 'quantitative'},
                                      'y': {'field': 'y', 'type': 'quantitative'}},
                         'mark': {'dy': -12, 'fontSize': 9, 'fontWeight': 'bold', 'type': 'text'},
                         'transform': [{'filter': 'datum.seq % 6 == 1'}]}],
              'title': {'anchor': 'start', 'text': 'Spiral Timeline – Monthly Revenue ($K)'},
              'transform': [{'as': 'angle', 'calculate': '(datum.seq - 1) * (2 * PI / 12)'}, {'as': 'radius', 'calculate': '50 + datum.seq * 3.2'},
                            {'as': 'x', 'calculate': 'datum.radius * cos(datum.angle)'}, {'as': 'y', 'calculate': 'datum.radius * sin(datum.angle)'},
                            {'as': 'year', 'calculate': 'substring(datum.month_label, 0, 4)'}]},
     'sql': '\n'
            'SELECT * FROM VALUES\n'
            "  (1,  '2020-01', 120), (2,  '2020-02', 135), (3,  '2020-03', 142),\n"
            "  (4,  '2020-04', 98),  (5,  '2020-05', 110), (6,  '2020-06', 155),\n"
            "  (7,  '2020-07', 168), (8,  '2020-08', 172), (9,  '2020-09', 160),\n"
            "  (10, '2020-10', 148), (11, '2020-11', 190), (12, '2020-12', 210),\n"
            "  (13, '2021-01', 145), (14, '2021-02', 158), (15, '2021-03', 170),\n"
            "  (16, '2021-04', 130), (17, '2021-05', 155), (18, '2021-06', 185),\n"
            "  (19, '2021-07', 195), (20, '2021-08', 200), (21, '2021-09', 188),\n"
            "  (22, '2021-10', 175), (23, '2021-11', 220), (24, '2021-12', 250),\n"
            "  (25, '2022-01', 180), (26, '2022-02', 195), (27, '2022-03', 210),\n"
            "  (28, '2022-04', 165), (29, '2022-05', 190), (30, '2022-06', 225),\n"
            "  (31, '2022-07', 240), (32, '2022-08', 248), (33, '2022-09', 230),\n"
            "  (34, '2022-10', 215), (35, '2022-11', 270), (36, '2022-12', 300),\n"
            "  (37, '2023-01', 220), (38, '2023-02', 240), (39, '2023-03', 260),\n"
            "  (40, '2023-04', 200), (41, '2023-05', 235), (42, '2023-06', 275),\n"
            "  (43, '2023-07', 290), (44, '2023-08', 298), (45, '2023-09', 280),\n"
            "  (46, '2023-10', 265), (47, '2023-11', 320), (48, '2023-12', 355),\n"
            "  (49, '2024-01', 270), (50, '2024-02', 290), (51, '2024-03', 315),\n"
            "  (52, '2024-04', 250), (53, '2024-05', 285), (54, '2024-06', 330),\n"
            "  (55, '2024-07', 345), (56, '2024-08', 358), (57, '2024-09', 340),\n"
            "  (58, '2024-10', 325), (59, '2024-11', 380), (60, '2024-12', 420)\n"
            'AS t(seq, month_label, revenue_k)\n',
     'title': 'Spiral Timeline – Monthly Revenue 2020-2024',
     'w': 6},
    {'fields': ['symbol', 'name', 'category', 'health_score', 'grid_row', 'grid_col'],
     'id': 'adv_periodic_table',
     'spec': {'layer': [{'encoding': {'color': {'field': 'health_score',
                                                'legend': {'title': 'Health Score'},
                                                'scale': {'domain': [60, 80, 100], 'range': ['#DC4B34', '#D4A017', '#3E7D53']},
                                                'type': 'quantitative'},
                                      'tooltip': [{'field': 'symbol', 'title': 'Code', 'type': 'nominal'}, {'field': 'name', 'title': 'Product', 'type': 'nominal'},
                                                  {'field': 'category', 'title': 'Category', 'type': 'nominal'}, {'field': 'health_score', 'title': 'Health Score', 'type': 'quantitative'}],
                                      'x': {'axis': None, 'field': 'grid_col', 'type': 'ordinal'},
                                      'y': {'axis': None, 'field': 'grid_row', 'type': 'ordinal'}},
                         'mark': {'cornerRadius': 4, 'stroke': '#555555', 'strokeWidth': 1.5, 'type': 'rect'}},
                        {'encoding': {'color': {'value': '#F4E3C9'},
                                      'text': {'field': 'symbol', 'type': 'nominal'},
                                      'x': {'field': 'grid_col', 'type': 'ordinal'},
                                      'y': {'field': 'grid_row', 'type': 'ordinal'}},
                         'mark': {'dy': -8, 'fontSize': 18, 'fontWeight': 'bold', 'type': 'text'}},
                        {'encoding': {'color': {'value': '#F4E3C9'},
                                      'text': {'field': 'name', 'type': 'nominal'},
                                      'x': {'field': 'grid_col', 'type': 'ordinal'},
                                      'y': {'field': 'grid_row', 'type': 'ordinal'}},
                         'mark': {'dy': 8, 'fontSize': 8, 'opacity': 0.7, 'type': 'text'}},
                        {'encoding': {'color': {'value': '#F4E3C9'},
                                      'text': {'field': 'health_score', 'format': '.0f', 'type': 'quantitative'},
                                      'x': {'field': 'grid_col', 'type': 'ordinal'},
                                      'y': {'field': 'grid_row', 'type': 'ordinal'}},
                         'mark': {'dy': 22, 'fontSize': 10, 'fontWeight': 'bold', 'type': 'text'}}],
              'title': {'anchor': 'start', 'text': 'Product KPI Periodic Table'}},
     'sql': '\n'
            'SELECT * FROM VALUES\n'
            "  ('CRM', 'CRM Suite',    'Sales',     92, 1, 1),\n"
            "  ('ERP', 'ERP Core',     'Ops',       87, 1, 2),\n"
            "  ('HCM', 'HR Cloud',     'HR',        78, 1, 3),\n"
            "  ('FIN', 'FinOps',       'Finance',   95, 1, 4),\n"
            "  ('MKT', 'Marketing',    'Sales',     81, 1, 5),\n"
            "  ('SEC', 'Security',     'Infra',     99, 1, 6),\n"
            "  ('DWH', 'Data Warehouse','Data',     88, 2, 1),\n"
            "  ('ETL', 'ETL Pipelines','Data',      74, 2, 2),\n"
            "  ('ML',  'ML Platform',  'Data',      83, 2, 3),\n"
            "  ('BI',  'Analytics',    'Data',      91, 2, 4),\n"
            "  ('API', 'API Gateway',  'Infra',     96, 2, 5),\n"
            "  ('CDN', 'CDN Edge',     'Infra',     97, 2, 6),\n"
            "  ('MOB', 'Mobile App',   'Product',   72, 3, 1),\n"
            "  ('WEB', 'Web Portal',   'Product',   85, 3, 2),\n"
            "  ('IOT', 'IoT Hub',      'Infra',     68, 3, 3),\n"
            "  ('DEV', 'DevOps',       'Infra',     90, 3, 4),\n"
            "  ('GOV', 'Governance',   'Compliance',94, 3, 5),\n"
            "  ('AUD', 'Audit Trail',  'Compliance',89, 3, 6),\n"
            "  ('SUP', 'Support',      'Ops',       76, 4, 1),\n"
            "  ('DOC', 'Docs Hub',     'Product',   82, 4, 2)\n"
            'AS t(symbol, name, category, health_score, grid_row, grid_col)\n',
     'title': 'Periodic Table – Product KPI Dashboard',
     'w': 6},
    {'fields': ['record_type', 'node_id', 'node_name', 'nx', 'ny', 'source_id', 'target_id', 'weight', 'sx', 'sy', 'tx', 'ty', 'source_name', 'target_name'],
     'id': 'adv_radial_network',
     'spec': {'layer': [{'encoding': {'strokeWidth': {'field': 'weight', 'legend': None, 'scale': {'range': [1, 6]}, 'type': 'quantitative'},
                                      'tooltip': [{'field': 'source_name', 'title': 'From', 'type': 'nominal'}, {'field': 'target_name', 'title': 'To', 'type': 'nominal'},
                                                  {'field': 'weight', 'title': 'Flow Strength', 'type': 'quantitative'}],
                                      'x': {'axis': None, 'field': 'sx', 'scale': {'domain': [-280, 280]}, 'type': 'quantitative'},
                                      'x2': {'field': 'tx'},
                                      'y': {'axis': None, 'field': 'sy', 'scale': {'domain': [-280, 280]}, 'type': 'quantitative'},
                                      'y2': {'field': 'ty'}},
                         'mark': {'color': '#8A7B5C', 'opacity': 0.4, 'type': 'rule'},
                         'transform': [{'filter': "datum.record_type == 'edge'"}]},
                        {'encoding': {'color': {'field': 'node_id',
                                                'legend': None,
                                                'scale': {'domain': [0, 1, 2, 3, 4, 5, 6, 7], 'range': ['#DC4B34', '#3E7D53', '#5B9BD5', '#D4A017', '#B7A98F', '#8A7B5C', '#241E1E', '#9B59B6']},
                                                'type': 'nominal'},
                                      'tooltip': [{'field': 'node_name', 'title': 'Team', 'type': 'nominal'}],
                                      'x': {'field': 'nx', 'type': 'quantitative'},
                                      'y': {'field': 'ny', 'type': 'quantitative'}},
                         'mark': {'opacity': 0.9, 'size': 500, 'stroke': '#555555', 'strokeWidth': 2, 'type': 'circle'},
                         'transform': [{'filter': "datum.record_type == 'node'"}]},
                        {'encoding': {'color': {'value': '#F4E3C9'},
                                      'text': {'field': 'node_name', 'type': 'nominal'},
                                      'x': {'field': 'nx', 'type': 'quantitative'},
                                      'y': {'field': 'ny', 'type': 'quantitative'}},
                         'mark': {'dy': -18, 'fontSize': 10, 'fontWeight': 'bold', 'type': 'text'},
                         'transform': [{'filter': "datum.record_type == 'node'"}]}],
              'title': {'anchor': 'start', 'text': 'Data Flow Between Teams'}},
     'sql': '\n'
            'WITH nodes AS (\n'
            '  SELECT * FROM VALUES\n'
            "    (0, 'Engineering'), (1, 'Data Science'), (2, 'Marketing'),\n"
            "    (3, 'Sales'), (4, 'Finance'), (5, 'Product'), (6, 'Support'), (7, 'Legal')\n"
            '  AS t(node_id, node_name)\n'
            '),\n'
            'edges AS (\n'
            '  SELECT * FROM VALUES\n'
            '    (0, 1, 8), (0, 5, 6), (1, 2, 4), (1, 5, 7),\n'
            '    (2, 3, 9), (3, 4, 5), (4, 7, 3), (5, 6, 6),\n'
            '    (6, 0, 4), (0, 3, 3), (2, 4, 2), (1, 6, 5)\n'
            '  AS t(source_id, target_id, weight)\n'
            '),\n'
            'node_positions AS (\n'
            '  SELECT node_id, node_name,\n'
            '    200 * COS(node_id * 2 * PI() / 8) AS nx,\n'
            '    200 * SIN(node_id * 2 * PI() / 8) AS ny\n'
            '  FROM nodes\n'
            '),\n'
            'edge_positions AS (\n'
            '  SELECT\n'
            '    e.source_id, e.target_id, e.weight,\n'
            '    s.nx AS sx, s.ny AS sy, s.node_name AS source_name,\n'
            '    t.nx AS tx, t.ny AS ty, t.node_name AS target_name\n'
            '  FROM edges e\n'
            '  JOIN node_positions s ON e.source_id = s.node_id\n'
            '  JOIN node_positions t ON e.target_id = t.node_id\n'
            ')\n'
            "SELECT 'node' AS record_type,\n"
            '  node_id, node_name, nx, ny,\n'
            '  NULL AS source_id, NULL AS target_id, NULL AS weight,\n'
            '  NULL AS sx, NULL AS sy, NULL AS tx, NULL AS ty,\n'
            '  NULL AS source_name, NULL AS target_name\n'
            'FROM node_positions\n'
            'UNION ALL\n'
            "SELECT 'edge' AS record_type,\n"
            '  NULL, NULL, NULL, NULL,\n'
            '  source_id, target_id, weight,\n'
            '  sx, sy, tx, ty, source_name, target_name\n'
            'FROM edge_positions\n',
     'title': 'Radial Network – Data Flow Between Teams',
     'w': 3},
    {'fields': ['country', 'emoji', 'region', 'satisfaction', 'population_m', 'nps_score'],
     'id': 'adv_emoji_scatter',
     'spec': {'layer': [{'encoding': {'size': {'field': 'nps_score', 'legend': {'title': 'NPS Score'}, 'scale': {'range': [20, 45]}, 'type': 'quantitative'},
                                      'text': {'field': 'emoji', 'type': 'nominal'},
                                      'tooltip': [{'field': 'country', 'title': 'Country', 'type': 'nominal'}, {'field': 'emoji', 'title': 'Flag', 'type': 'nominal'},
                                                  {'field': 'region', 'title': 'Region', 'type': 'nominal'}, {'field': 'satisfaction', 'title': 'Satisfaction', 'type': 'quantitative'},
                                                  {'field': 'population_m', 'title': 'Population (M)', 'type': 'quantitative'}, {'field': 'nps_score', 'title': 'NPS Score', 'type': 'quantitative'}],
                                      'x': {'axis': {'grid': True, 'gridOpacity': 0.2}, 'field': 'population_m', 'scale': {'type': 'log'}, 'title': 'Population (millions)', 'type': 'quantitative'},
                                      'y': {'axis': {'grid': True, 'gridOpacity': 0.2}, 'field': 'satisfaction', 'scale': {'domain': [50, 100]}, 'title': 'Customer Satisfaction', 'type': 'quantitative'}},
                         'mark': {'align': 'center', 'baseline': 'middle', 'type': 'text'}},
                        {'encoding': {'color': {'field': 'region',
                                                'legend': {'title': 'Region'},
                                                'scale': {'domain': ['Americas', 'Europe', 'Asia', 'Oceania', 'Africa', 'Middle East'],
                                                          'range': ['#DC4B34', '#5B9BD5', '#3E7D53', '#B7A98F', '#D4A017', '#8A7B5C']},
                                                'type': 'nominal'},
                                      'text': {'field': 'country', 'type': 'nominal'},
                                      'x': {'field': 'population_m', 'scale': {'type': 'log'}, 'type': 'quantitative'},
                                      'y': {'field': 'satisfaction', 'type': 'quantitative'}},
                         'mark': {'dy': 14, 'fontSize': 8, 'opacity': 0.7, 'type': 'text'}}],
              'title': {'anchor': 'start', 'text': 'Global Product Satisfaction 🌍'}},
     'sql': '\n'
            'SELECT * FROM VALUES\n'
            "  ('United States',  '🇺🇸', 'Americas',  82, 330, 95),\n"
            "  ('Brazil',         '🇧🇷', 'Americas',  74, 210, 78),\n"
            "  ('Canada',         '🇨🇦', 'Americas',  88, 52,  92),\n"
            "  ('Mexico',         '🇲🇽', 'Americas',  71, 128, 70),\n"
            "  ('Germany',        '🇩🇪', 'Europe',    90, 84,  94),\n"
            "  ('France',         '🇫🇷', 'Europe',    85, 67,  88),\n"
            "  ('UK',             '🇬🇧', 'Europe',    87, 68,  91),\n"
            "  ('Spain',          '🇪🇸', 'Europe',    76, 47,  75),\n"
            "  ('Italy',          '🇮🇹', 'Europe',    78, 60,  80),\n"
            "  ('Japan',          '🇯🇵', 'Asia',      93, 126, 97),\n"
            "  ('South Korea',    '🇰🇷', 'Asia',      91, 52,  95),\n"
            "  ('India',          '🇮🇳', 'Asia',      69, 1400, 65),\n"
            "  ('China',          '🇨🇳', 'Asia',      75, 1412, 72),\n"
            "  ('Australia',      '🇦🇺', 'Oceania',   89, 26,  93),\n"
            "  ('Nigeria',        '🇳🇬', 'Africa',    62, 220, 55),\n"
            "  ('South Africa',   '🇿🇦', 'Africa',    68, 60,  63),\n"
            "  ('Egypt',          '🇪🇬', 'Africa',    65, 105, 60),\n"
            "  ('UAE',            '🇦🇪', 'Middle East',86, 10, 90)\n"
            'AS t(country, emoji, region, satisfaction, population_m, nps_score)\n',
     'title': 'Emoji Scatter – Global Product Satisfaction',
     'w': 3},
]
