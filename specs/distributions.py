"""Distribution charts. Specs are Vega-Lite WITHOUT config/data/width/height
(the build script injects Du Bois config + databricks_query binding + container
sizing). Each chart binds to a dataset defined by `sql`; `fields` lists every
column the SQL outputs (must match the SQL aliases exactly). Histograms bin in
the Vega-Lite spec (`"bin": true` / `{"step": N}`) over raw columns selected in
SQL; density/cumulative use `transform` so the spec references derived fields
(`value`, `density`, `cumulative_count`) that are NOT SQL columns."""

CATEGORY = "Distributions"

CHARTS = [
    {
        "id": "dist_hist_simple", "title": "Histogram — IMDB Rating",
        "sql": "SELECT IMDB_Rating AS imdb_rating FROM pb_demo.custom_gallery.movies WHERE IMDB_Rating IS NOT NULL",
        "fields": ["imdb_rating"],
        "spec": {"mark": "bar",
                 "encoding": {"x": {"field": "imdb_rating", "type": "quantitative", "bin": True, "title": "IMDB Rating"},
                              "y": {"aggregate": "count", "type": "quantitative", "title": "Count of films"}}},
    },
    {
        "id": "dist_hist_binstep", "title": "Binned Histogram — Horsepower (step 25)",
        "sql": "SELECT Horsepower AS horsepower FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["horsepower"],
        "spec": {"mark": "bar",
                 "encoding": {"x": {"field": "horsepower", "type": "quantitative", "bin": {"step": 25}, "title": "Horsepower"},
                              "y": {"aggregate": "count", "type": "quantitative", "title": "Count of cars"}}},
    },
    {
        "id": "dist_cumulative", "title": "Cumulative Frequency — IMDB Rating",
        "sql": "SELECT IMDB_Rating AS imdb_rating FROM pb_demo.custom_gallery.movies WHERE IMDB_Rating IS NOT NULL",
        "fields": ["imdb_rating"],
        "spec": {"transform": [
                     {"sort": [{"field": "imdb_rating"}],
                      "window": [{"op": "count", "field": "imdb_rating", "as": "cumulative_count"}],
                      "frame": [None, 0]}
                 ],
                 "mark": "area",
                 "encoding": {"x": {"field": "imdb_rating", "type": "quantitative", "title": "IMDB Rating"},
                              "y": {"field": "cumulative_count", "type": "quantitative", "title": "Cumulative count"}}},
    },
    {
        "id": "dist_hist_overlaid", "title": "Overlaid Histogram — Horsepower by Origin",
        "sql": "SELECT Horsepower AS horsepower, Origin AS origin FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["horsepower", "origin"],
        "spec": {"mark": {"type": "bar", "opacity": 0.55},
                 "encoding": {"x": {"field": "horsepower", "type": "quantitative", "bin": {"maxbins": 20}, "title": "Horsepower"},
                              "y": {"aggregate": "count", "type": "quantitative", "stack": None, "title": "Count"},
                              "color": {"field": "origin", "type": "nominal", "title": "Origin"}}},
    },
    {
        "id": "dist_hist_stacked", "title": "Stacked Histogram — Horsepower by Origin",
        "sql": "SELECT Horsepower AS horsepower, Origin AS origin FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["horsepower", "origin"],
        "spec": {"mark": "bar",
                 "encoding": {"x": {"field": "horsepower", "type": "quantitative", "bin": {"maxbins": 20}, "title": "Horsepower"},
                              "y": {"aggregate": "count", "type": "quantitative", "title": "Count"},
                              "color": {"field": "origin", "type": "nominal", "title": "Origin"}}},
    },
    {
        "id": "dist_density", "title": "Density Plot — Horsepower",
        "sql": "SELECT Horsepower AS horsepower FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["horsepower"],
        "spec": {"transform": [{"density": "horsepower", "bandwidth": 12}],
                 "mark": {"type": "area", "opacity": 0.6, "line": {"color": "#5593F7"}},
                 "encoding": {"x": {"field": "value", "type": "quantitative", "title": "Horsepower"},
                              "y": {"field": "density", "type": "quantitative", "title": "Density"}}},
    },
    {
        "id": "dist_density_grouped", "title": "Grouped Density — MPG by Origin",
        "sql": "SELECT Miles_per_Gallon AS miles_per_gallon, Origin AS origin FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL",
        "fields": ["miles_per_gallon", "origin"],
        "spec": {"transform": [{"density": "miles_per_gallon", "groupby": ["origin"], "bandwidth": 2}],
                 "mark": {"type": "area", "opacity": 0.5},
                 "encoding": {"x": {"field": "value", "type": "quantitative", "title": "Miles per Gallon"},
                              "y": {"field": "density", "type": "quantitative", "stack": None, "title": "Density"},
                              "color": {"field": "origin", "type": "nominal", "title": "Origin"}}},
    },
    {
        "id": "dist_boxplot", "title": "Box Plot — MPG by Cylinders",
        "sql": "SELECT CAST(Cylinders AS STRING) AS cylinders, Miles_per_Gallon AS miles_per_gallon FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL",
        "fields": ["cylinders", "miles_per_gallon"],
        "spec": {"mark": {"type": "boxplot", "extent": "min-max"},
                 "encoding": {"x": {"field": "cylinders", "type": "ordinal", "title": "Cylinders", "axis": {"labelAngle": 0}},
                              "y": {"field": "miles_per_gallon", "type": "quantitative", "title": "Miles per Gallon"}}},
    },
    {
        "id": "dist_strip", "title": "Strip Plot — Horsepower by Cylinders",
        "sql": "SELECT CAST(Cylinders AS STRING) AS cylinders, Horsepower AS horsepower FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["cylinders", "horsepower"],
        "spec": {"mark": {"type": "tick", "opacity": 0.6},
                 "encoding": {"x": {"field": "horsepower", "type": "quantitative", "title": "Horsepower"},
                              "y": {"field": "cylinders", "type": "ordinal", "title": "Cylinders"}}},
    },
    {
        "id": "dist_mean_error", "title": "Mean MPG with 95% CI Error Bars — by Origin",
        "sql": "SELECT Origin AS origin, Miles_per_Gallon AS miles_per_gallon FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL",
        "fields": ["origin", "miles_per_gallon"],
        "spec": {"layer": [
                     {"mark": {"type": "errorbar", "extent": "ci", "ticks": True},
                      "encoding": {"x": {"field": "miles_per_gallon", "type": "quantitative", "scale": {"zero": False}, "title": "Miles per Gallon"},
                                   "y": {"field": "origin", "type": "nominal", "title": None}}},
                     {"mark": {"type": "point", "filled": True, "color": "#EC516D", "size": 60},
                      "encoding": {"x": {"aggregate": "mean", "field": "miles_per_gallon", "type": "quantitative"},
                                   "y": {"field": "origin", "type": "nominal"}}}
                 ]},
    },
    {
        "id": "dist2_hist_log", "title": "Log-Scaled Histogram — IMDB Votes",
        "sql": "SELECT IMDB_Votes AS imdb_votes FROM pb_demo.custom_gallery.movies WHERE IMDB_Votes IS NOT NULL AND IMDB_Votes > 0",
        "fields": ["imdb_votes"],
        "spec": {"mark": "bar",
                 "encoding": {"x": {"field": "imdb_votes", "type": "quantitative", "bin": {"maxbins": 30}, "title": "IMDB Votes"},
                              "y": {"aggregate": "count", "type": "quantitative", "scale": {"type": "log"}, "title": "Count of films (log)"}}},
    },
    {
        "id": "dist2_rel_freq", "title": "Relative Frequency Histogram — Horsepower",
        "sql": "SELECT Horsepower AS horsepower FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["horsepower"],
        "spec": {"transform": [
                     {"bin": {"maxbins": 20}, "field": "horsepower", "as": ["bin_hp", "bin_hp_end"]},
                     {"aggregate": [{"op": "count", "as": "cnt"}], "groupby": ["bin_hp", "bin_hp_end"]},
                     {"joinaggregate": [{"op": "sum", "field": "cnt", "as": "total"}]},
                     {"calculate": "datum.cnt / datum.total", "as": "pct"}
                 ],
                 "mark": "bar",
                 "encoding": {"x": {"field": "bin_hp", "type": "quantitative", "bin": {"binned": True}, "title": "Horsepower"},
                              "x2": {"field": "bin_hp_end"},
                              "y": {"field": "pct", "type": "quantitative", "axis": {"format": "%"}, "title": "Percent of cars"}}},
    },
    {
        "id": "dist2_2d_hist", "title": "2D Histogram — Rotten Tomatoes vs IMDB",
        "sql": "SELECT Rotten_Tomatoes_Rating AS rotten_tomatoes, IMDB_Rating AS imdb_rating FROM pb_demo.custom_gallery.movies WHERE Rotten_Tomatoes_Rating IS NOT NULL AND IMDB_Rating IS NOT NULL",
        "fields": ["rotten_tomatoes", "imdb_rating"],
        "spec": {"mark": "circle",
                 "encoding": {"x": {"field": "rotten_tomatoes", "type": "quantitative", "bin": {"maxbins": 20}, "title": "Rotten Tomatoes"},
                              "y": {"field": "imdb_rating", "type": "quantitative", "bin": {"maxbins": 20}, "title": "IMDB Rating"},
                              "size": {"aggregate": "count", "type": "quantitative", "title": "Count of films"}}},
    },
    {
        "id": "dist2_hist_cumulative", "title": "Histogram + Cumulative — Horsepower",
        "sql": "SELECT Horsepower AS horsepower FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["horsepower"],
        "spec": {"transform": [
                     {"bin": {"maxbins": 20}, "field": "horsepower", "as": ["bin_hp", "bin_hp_end"]},
                     {"aggregate": [{"op": "count", "as": "cnt"}], "groupby": ["bin_hp", "bin_hp_end"]},
                     {"sort": [{"field": "bin_hp"}], "window": [{"op": "sum", "field": "cnt", "as": "cumulative"}], "frame": [None, 0]}
                 ],
                 "layer": [
                     {"mark": "bar",
                      "encoding": {"x": {"field": "bin_hp", "type": "quantitative", "bin": {"binned": True}, "title": "Horsepower"},
                                   "x2": {"field": "bin_hp_end"},
                                   "y": {"field": "cnt", "type": "quantitative", "title": "Count of cars"}}},
                     {"mark": {"type": "line", "color": "#EC516D", "point": True},
                      "encoding": {"x": {"field": "bin_hp", "type": "quantitative", "title": "Horsepower"},
                                   "y": {"field": "cumulative", "type": "quantitative", "title": "Count of cars"}}}
                 ]},
    },
    {
        "id": "dist2_wilkinson", "title": "Wilkinson Dot Plot — Cars by Cylinders",
        "sql": "SELECT CAST(Cylinders AS STRING) AS cylinders FROM pb_demo.custom_gallery.cars WHERE Cylinders IS NOT NULL",
        "fields": ["cylinders"],
        "spec": {"transform": [
                     {"window": [{"op": "rank", "as": "dot_id"}], "groupby": ["cylinders"], "sort": [{"field": "cylinders"}]}
                 ],
                 "mark": {"type": "circle", "opacity": 0.9, "size": 90},
                 "encoding": {"x": {"field": "cylinders", "type": "ordinal", "title": "Cylinders", "axis": {"labelAngle": 0}},
                              "y": {"field": "dot_id", "type": "quantitative", "title": "Count of cars"}}},
    },
    {
        "id": "dist2_isotype", "title": "Isotype Dot Plot — Cars by Origin",
        "sql": "SELECT Origin AS origin, COUNT(*) AS car_count FROM pb_demo.custom_gallery.cars WHERE Origin IS NOT NULL GROUP BY Origin",
        "fields": ["origin", "car_count"],
        "spec": {"mark": {"type": "text", "baseline": "middle", "align": "left"},
                 "encoding": {"y": {"field": "origin", "type": "nominal", "title": None, "axis": {"labelAngle": 0}},
                              "x": {"field": "car_count", "type": "quantitative", "title": "Count of cars"},
                              "size": {"field": "car_count", "type": "quantitative", "legend": None, "scale": {"range": [200, 900]}},
                              "text": {"value": "\U0001F697"}}},
    },
    {
        "id": "dist2_errorbar_stdev", "title": "Mean MPG with Std-Dev Error Bars — by Origin",
        "sql": "SELECT Origin AS origin, Miles_per_Gallon AS miles_per_gallon FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL",
        "fields": ["origin", "miles_per_gallon"],
        "spec": {"layer": [
                     {"mark": {"type": "errorbar", "extent": "stdev", "ticks": True},
                      "encoding": {"x": {"field": "miles_per_gallon", "type": "quantitative", "scale": {"zero": False}, "title": "Miles per Gallon"},
                                   "y": {"field": "origin", "type": "nominal", "title": None}}},
                     {"mark": {"type": "point", "filled": True, "color": "#EC516D", "size": 60},
                      "encoding": {"x": {"aggregate": "mean", "field": "miles_per_gallon", "type": "quantitative"},
                                   "y": {"field": "origin", "type": "nominal"}}}
                 ]},
    },
    {
        "id": "dist2_boxplot_tukey", "title": "Tukey Box Plot (1.5 IQR) — Horsepower by Cylinders",
        "sql": "SELECT CAST(Cylinders AS STRING) AS cylinders, Horsepower AS horsepower FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL",
        "fields": ["cylinders", "horsepower"],
        "spec": {"mark": {"type": "boxplot", "extent": 1.5},
                 "encoding": {"x": {"field": "cylinders", "type": "ordinal", "title": "Cylinders", "axis": {"labelAngle": 0}},
                              "y": {"field": "horsepower", "type": "quantitative", "title": "Horsepower"}}},
    },
    {
        "id": "g3_bar_binned_data", "title": "Histogram from Pre-Binned Data — Horsepower",
        "sql": "SELECT FLOOR(Horsepower/25)*25 AS bin_start, FLOOR(Horsepower/25)*25+25 AS bin_end, COUNT(*) AS cnt FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL GROUP BY FLOOR(Horsepower/25)*25, FLOOR(Horsepower/25)*25+25 ORDER BY bin_start",
        "fields": ["bin_start", "bin_end", "cnt"],
        "spec": {"mark": "bar",
                 "encoding": {"x": {"field": "bin_start", "type": "quantitative", "bin": {"binned": True}, "title": "Horsepower"},
                              "x2": {"field": "bin_end"},
                              "y": {"field": "cnt", "type": "quantitative", "title": "Count of cars"}}},
    },
    {
        "id": "g3_histogram_nonlinear", "title": "Nonlinear-Bin Histogram — IMDB Votes",
        "sql": "SELECT CASE WHEN IMDB_Votes < 1000 THEN '0-1K' WHEN IMDB_Votes < 10000 THEN '1K-10K' WHEN IMDB_Votes < 100000 THEN '10K-100K' WHEN IMDB_Votes < 500000 THEN '100K-500K' ELSE '500K+' END AS votes_bucket, COUNT(*) AS cnt FROM pb_demo.custom_gallery.movies WHERE IMDB_Votes IS NOT NULL AND IMDB_Votes > 0 GROUP BY 1",
        "fields": ["votes_bucket", "cnt"],
        "spec": {"mark": "bar",
                 "encoding": {"x": {"field": "votes_bucket", "type": "ordinal", "title": "IMDB Votes (nonlinear bins)",
                                    "sort": ["0-1K", "1K-10K", "10K-100K", "100K-500K", "500K+"],
                                    "axis": {"labelAngle": 0}},
                              "y": {"field": "cnt", "type": "quantitative", "title": "Count of films"}}},
    },
    {
        "id": "g3_area_density_stacked", "title": "Stacked Density — MPG by Origin",
        "sql": "SELECT Miles_per_Gallon AS miles_per_gallon, Origin AS origin FROM pb_demo.custom_gallery.cars WHERE Miles_per_Gallon IS NOT NULL",
        "fields": ["miles_per_gallon", "origin"],
        "spec": {"transform": [{"density": "miles_per_gallon", "groupby": ["origin"], "bandwidth": 2, "counts": True}],
                 "mark": {"type": "area"},
                 "encoding": {"x": {"field": "value", "type": "quantitative", "title": "Miles per Gallon"},
                              "y": {"field": "density", "type": "quantitative", "stack": "zero", "title": "Estimated count"},
                              "color": {"field": "origin", "type": "nominal", "title": "Origin"}}},
    },
    {
        "id": "g3_isotype_bar_chart", "title": "Isotype Unit Chart — Cars by Origin (1 square ≈ 10 cars)",
        "sql": "WITH c AS (SELECT Origin AS origin, COUNT(*) AS cnt FROM pb_demo.custom_gallery.cars GROUP BY Origin) SELECT origin, unit FROM c LATERAL VIEW explode(sequence(1, CAST(ROUND(cnt/10.0) AS INT))) e AS unit",
        "fields": ["origin", "unit"],
        "spec": {"mark": {"type": "square", "size": 90, "filled": True},
                 "encoding": {"y": {"field": "origin", "type": "nominal", "title": None, "axis": {"labelAngle": 0}},
                              "x": {"field": "unit", "type": "ordinal", "title": "Cars (1 square ≈ 10)", "axis": {"labels": False, "ticks": False}},
                              "color": {"field": "origin", "type": "nominal", "legend": None}}},
    },
    {
        "id": "g3_bar_percent_of_total", "title": "Percent of Total — Weather Days",
        "sql": "SELECT weather, COUNT(*) AS cnt FROM pb_demo.custom_gallery.seattle_weather GROUP BY weather",
        "fields": ["weather", "cnt"],
        "spec": {"transform": [
                     {"joinaggregate": [{"op": "sum", "field": "cnt", "as": "total"}]},
                     {"calculate": "datum.cnt / datum.total", "as": "pct"}
                 ],
                 "mark": "bar",
                 "encoding": {"x": {"field": "weather", "type": "nominal", "title": "Weather", "axis": {"labelAngle": 0}},
                              "y": {"field": "pct", "type": "quantitative", "axis": {"format": "%"}, "title": "Percent of days"}}},
    },
    {
        "id": "g3_boxplot_preaggregated", "title": "Pre-Aggregated Box Plot — Horsepower by Cylinders",
        "sql": "SELECT CAST(Cylinders AS STRING) AS cylinders, MIN(Horsepower) AS lo, percentile(Horsepower,0.25) AS q1, percentile(Horsepower,0.5) AS median, percentile(Horsepower,0.75) AS q3, MAX(Horsepower) AS hi FROM pb_demo.custom_gallery.cars WHERE Horsepower IS NOT NULL GROUP BY CAST(Cylinders AS STRING)",
        "fields": ["cylinders", "lo", "q1", "median", "q3", "hi"],
        "spec": {"layer": [
                     {"mark": {"type": "rule"},
                      "encoding": {"x": {"field": "cylinders", "type": "ordinal", "title": "Cylinders", "axis": {"labelAngle": 0}},
                                   "y": {"field": "lo", "type": "quantitative", "title": "Horsepower"},
                                   "y2": {"field": "hi"}}},
                     {"mark": {"type": "bar", "size": 24, "color": "#5593F7"},
                      "encoding": {"x": {"field": "cylinders", "type": "ordinal"},
                                   "y": {"field": "q1", "type": "quantitative"},
                                   "y2": {"field": "q3"}}},
                     {"mark": {"type": "tick", "size": 24, "color": "#12100B", "thickness": 2},
                      "encoding": {"x": {"field": "cylinders", "type": "ordinal"},
                                   "y": {"field": "median", "type": "quantitative"}}}
                 ]},
    },
]
