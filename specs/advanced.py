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
                     {"mark": {"type": "errorbar", "extent": "ci", "color": "#241E1E"},
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
                     {"mark": {"type": "line", "color": "#241E1E"},
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
                     {"mark": {"type": "bar", "color": "#241E1E", "size": 12},
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
                     {"mark": {"type": "tick", "opacity": 0.4, "color": "#241E1E", "thickness": 1},
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
                     {"mark": {"type": "text", "align": "left", "dx": 4, "color": "#241E1E"},
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
                     {"mark": {"type": "line", "color": "#241E1E", "strokeWidth": 1.5},
                      "encoding": {"x": {"field": "date", "type": "temporal", "title": None},
                                   "y": {"field": "price", "type": "quantitative", "title": "S&P 500 index"}}}
                 ]},
    },
]
