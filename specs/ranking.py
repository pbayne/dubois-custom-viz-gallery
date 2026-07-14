"""Ranking charts. Specs are Vega-Lite WITHOUT config/data/width/height
(the build script injects Du Bois config + databricks_query binding + container
sizing). Each chart binds to a dataset defined by `sql`; `fields` lists every
column the spec references (must match the SQL output aliases)."""

CATEGORY = "Ranking"

CHARTS = [
    {
        "id": "rank_top_movies", "title": "Top 15 Movies by Worldwide Gross",
        "sql": "SELECT Title AS title, Worldwide_Gross AS gross FROM pb_demo.custom_gallery.movies WHERE Worldwide_Gross IS NOT NULL ORDER BY Worldwide_Gross DESC LIMIT 15",
        "fields": ["title", "gross"],
        "w": 3, "h": 7,
        "spec": {"mark": {"type": "bar"},
                 "encoding": {"y": {"field": "title", "type": "nominal", "sort": "-x", "title": None},
                              "x": {"field": "gross", "type": "quantitative", "title": "Worldwide Gross ($)"}}},
    },
    {
        "id": "rank_lollipop", "title": "Lollipop — Avg IMDB Rating by Genre",
        "sql": "SELECT Major_Genre AS genre, ROUND(AVG(IMDB_Rating),2) AS avg_rating FROM pb_demo.custom_gallery.movies WHERE Major_Genre IS NOT NULL AND IMDB_Rating IS NOT NULL GROUP BY Major_Genre",
        "fields": ["genre", "avg_rating"],
        "spec": {"encoding": {"y": {"field": "genre", "type": "nominal", "sort": "-x", "title": None}},
                 "layer": [
                     {"mark": {"type": "rule", "color": "#7A7A7A"},
                      "encoding": {"x": {"field": "avg_rating", "type": "quantitative", "title": "Avg IMDB Rating"},
                                   "x2": {"datum": 0}}},
                     {"mark": {"type": "point", "filled": True, "size": 120, "color": "#EC516D"},
                      "encoding": {"x": {"field": "avg_rating", "type": "quantitative"}}}
                 ]},
    },
    {
        "id": "rank_dotplot", "title": "Dot Plot — Avg Rotten Tomatoes by Genre",
        "sql": "SELECT Major_Genre AS genre, ROUND(AVG(Rotten_Tomatoes_Rating),1) AS avg_rt FROM pb_demo.custom_gallery.movies WHERE Major_Genre IS NOT NULL AND Rotten_Tomatoes_Rating IS NOT NULL GROUP BY Major_Genre",
        "fields": ["genre", "avg_rt"],
        "spec": {"mark": {"type": "point", "filled": True, "size": 140, "color": "#5593F7"},
                 "encoding": {"y": {"field": "genre", "type": "nominal", "sort": "-x", "title": None},
                              "x": {"field": "avg_rt", "type": "quantitative", "title": "Avg Rotten Tomatoes", "scale": {"zero": False}}}},
    },
    {
        "id": "rank_bar_labels", "title": "Film Count by Genre — with Labels",
        "sql": "SELECT Major_Genre AS genre, COUNT(*) AS count FROM pb_demo.custom_gallery.movies WHERE Major_Genre IS NOT NULL GROUP BY Major_Genre",
        "fields": ["genre", "count"],
        "spec": {"layer": [
            {"mark": {"type": "bar"},
             "encoding": {"y": {"field": "genre", "type": "nominal", "sort": "-x", "title": None},
                          "x": {"field": "count", "type": "quantitative", "title": "Films"}}},
            {"mark": {"type": "text", "align": "left", "dx": 4},
             "encoding": {"y": {"field": "genre", "type": "nominal", "sort": "-x"},
                          "x": {"field": "count", "type": "quantitative"},
                          "text": {"field": "count", "type": "quantitative"}}}
        ]},
    },
    {
        "id": "rank_top_directors", "title": "Top 15 Directors by Film Count",
        "sql": "SELECT Director AS director, COUNT(*) AS count FROM pb_demo.custom_gallery.movies WHERE Director IS NOT NULL GROUP BY Director ORDER BY count DESC LIMIT 15",
        "fields": ["director", "count"],
        "w": 3, "h": 7,
        "spec": {"mark": {"type": "bar"},
                 "encoding": {"y": {"field": "director", "type": "nominal", "sort": "-x", "title": None},
                              "x": {"field": "count", "type": "quantitative", "title": "Films"}}},
    },
    {
        "id": "rank_gapminder_life", "title": "Top 15 Countries by Life Expectancy (2005)",
        "sql": "SELECT country, ROUND(life_expect,1) AS life_expect FROM pb_demo.custom_gallery.gapminder WHERE year=2005 ORDER BY life_expect DESC LIMIT 15",
        "fields": ["country", "life_expect"],
        "w": 3, "h": 7,
        "spec": {"mark": {"type": "bar"},
                 "encoding": {"y": {"field": "country", "type": "nominal", "sort": "-x", "title": None},
                              "x": {"field": "life_expect", "type": "quantitative", "title": "Life Expectancy (yrs)", "scale": {"zero": False}}}},
    },
    {
        "id": "rank_diverging", "title": "Diverging — Genre IMDB vs Overall Mean",
        "sql": "SELECT genre, ROUND(avg_rating - overall,2) AS deviation FROM (SELECT Major_Genre AS genre, AVG(IMDB_Rating) AS avg_rating, (SELECT AVG(IMDB_Rating) FROM pb_demo.custom_gallery.movies WHERE IMDB_Rating IS NOT NULL) AS overall FROM pb_demo.custom_gallery.movies WHERE Major_Genre IS NOT NULL AND IMDB_Rating IS NOT NULL GROUP BY Major_Genre)",
        "fields": ["genre", "deviation"],
        "spec": {"mark": {"type": "bar"},
                 "encoding": {"y": {"field": "genre", "type": "nominal", "sort": "-x", "title": None},
                              "x": {"field": "deviation", "type": "quantitative", "title": "Deviation from Mean IMDB"},
                              "color": {"condition": {"test": "datum.deviation >= 0", "value": "#5593F7"},
                                        "value": "#EC516D"}}},
    },
]
