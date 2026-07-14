"""Maps. The custom-viz sandbox CSP blocks external TopoJSON, so these are
projection-based POINT/SYMBOL maps (no basemap file needed): lat/long projected
with albersUsa. Choropleths (filled regions) need boundary geometry and are noted
in the README as a follow-up."""

CATEGORY = "Maps"

_US = "country='USA' AND longitude BETWEEN -170 AND -65 AND latitude BETWEEN 18 AND 72"

CHARTS = [
    {
        "id": "map_dots", "title": "Dot Map — US Airports",
        "sql": f"SELECT longitude, latitude, city, state FROM pb_demo.custom_gallery.airports WHERE {_US}",
        "fields": ["longitude", "latitude", "city", "state"],
        "spec": {"projection": {"type": "albersUsa"},
                 "mark": {"type": "circle", "size": 8, "opacity": 0.5, "color": "#5593F7"},
                 "encoding": {"longitude": {"field": "longitude", "type": "quantitative"},
                              "latitude": {"field": "latitude", "type": "quantitative"},
                              "tooltip": [{"field": "city", "type": "nominal"},
                                          {"field": "state", "type": "nominal"}]}},
        "w": 3, "h": 8,
    },
    {
        "id": "map_state_bubbles", "title": "Bubble Map — Airports per State",
        "sql": f"SELECT state, ROUND(AVG(longitude),3) AS lon, ROUND(AVG(latitude),3) AS lat, COUNT(*) AS n FROM pb_demo.custom_gallery.airports WHERE {_US} GROUP BY state",
        "fields": ["state", "lon", "lat", "n"],
        "spec": {"projection": {"type": "albersUsa"},
                 "mark": {"type": "circle", "opacity": 0.8, "stroke": "#11171C", "strokeWidth": 0.5},
                 "encoding": {"longitude": {"field": "lon", "type": "quantitative"},
                              "latitude": {"field": "lat", "type": "quantitative"},
                              "size": {"field": "n", "type": "quantitative", "title": "Airports",
                                       "scale": {"range": [20, 900]}},
                              "color": {"field": "n", "type": "quantitative", "title": "Airports"},
                              "tooltip": [{"field": "state", "type": "nominal"},
                                          {"field": "n", "type": "quantitative", "title": "Airports"}]}},
        "w": 3, "h": 8,
    },
    {
        "id": "map_region", "title": "Symbol Map — Airports by Region",
        "sql": f"SELECT longitude, latitude, CASE WHEN longitude < -100 THEN 'West' WHEN longitude < -85 THEN 'Central' ELSE 'East' END AS region FROM pb_demo.custom_gallery.airports WHERE {_US}",
        "fields": ["longitude", "latitude", "region"],
        "spec": {"projection": {"type": "albersUsa"},
                 "mark": {"type": "circle", "size": 10, "opacity": 0.55},
                 "encoding": {"longitude": {"field": "longitude", "type": "quantitative"},
                              "latitude": {"field": "latitude", "type": "quantitative"},
                              "color": {"field": "region", "type": "nominal", "title": "Region"}}},
        "w": 3, "h": 8,
    },
    {
        "id": "map_density", "title": "Airport Density — Binned Grid",
        "sql": f"SELECT longitude, latitude FROM pb_demo.custom_gallery.airports WHERE {_US}",
        "fields": ["longitude", "latitude"],
        "spec": {"projection": {"type": "albersUsa"},
                 "mark": {"type": "circle", "size": 6, "opacity": 0.4, "color": "#42D7A5"},
                 "encoding": {"longitude": {"field": "longitude", "type": "quantitative"},
                              "latitude": {"field": "latitude", "type": "quantitative"}}},
        "w": 3, "h": 8,
    },
    # --- Filled choropleths via AI/BI's NATIVE choropleth-map widget (custom-viz
    #     geoshape can't fill polygons; the native widget reads geometry from a
    #     `geojson` column via region.regionType=custom). Geometry tables built by
    #     data_generation/10_generate_geo_tables (CA counties, LA neighborhoods).
    {
        "id": "map_ca_choropleth", "title": "Choropleth — California Counties (filled)",
        "sql": "SELECT name, value, geojson FROM pb_demo.custom_gallery.ca_counties_geo",
        "native": {
            "widgetType": "choropleth-map",
            "encodings": {
                "color": {"fieldName": "value", "displayName": "Value",
                          "scale": {"type": "quantitative", "colorRamp": {"mode": "scheme", "scheme": "blues"}}},
                "extra": [{"fieldName": "name"}],
                "region": {"regionType": "custom", "fieldName": "geojson"},
            },
            "mark": {"opacity": 0.85},
        },
        "query_fields": [{"name": "value", "expression": "`value`"},
                         {"name": "name", "expression": "`name`"},
                         {"name": "geojson", "expression": "`geojson`"}],
        "w": 3, "h": 9,
    },
    {
        "id": "map_la_choropleth", "title": "Choropleth — LA Neighborhoods (filled)",
        "sql": "SELECT name, value, geojson FROM pb_demo.custom_gallery.la_neighborhoods_geo",
        "native": {
            "widgetType": "choropleth-map",
            "encodings": {
                "color": {"fieldName": "value", "displayName": "Value",
                          "scale": {"type": "quantitative", "colorRamp": {"mode": "scheme", "scheme": "purples"}}},
                "extra": [{"fieldName": "name"}],
                "region": {"regionType": "custom", "fieldName": "geojson"},
            },
            "mark": {"opacity": 0.85},
        },
        "query_fields": [{"name": "value", "expression": "`value`"},
                         {"name": "name", "expression": "`name`"},
                         {"name": "geojson", "expression": "`geojson`"}],
        "w": 3, "h": 9,
    },
]
