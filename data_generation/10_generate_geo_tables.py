#!/usr/bin/env python3
"""Build the geometry tables that back the filled choropleth-map widgets.

AI/BI's native `choropleth-map` widget reads region geometry from a table column
of GeoJSON text (referenced via `region: {regionType: "custom", fieldName: ...}`).
Custom-viz Vega-Lite `geoshape` does NOT render filled polygons in the sandbox, so
choropleths must use the native widget.

This script fetches public boundary GeoJSON, simplifies it (rounds coordinates and
keeps only name + a demo `value`), and writes one table per region set into the
target `<catalog>.<schema>` (via --schema / $VEGA_SCHEMA, default
`pb_demo.custom_gallery`) using the SQL Statement Execution API (CREATE TABLE AS
SELECT ... FROM VALUES). Run locally with the Databricks CLI configured; it needs
internet to fetch the GeoJSON. The schema must already exist.

  python data_generation/10_generate_geo_tables.py --profile <p> --warehouse <id> \
      [--schema <catalog.schema>]

Tables produced (in the target schema):
  <schema>.ca_counties_geo        (name, value, geojson)   58 rows
  <schema>.la_neighborhoods_geo   (name, value, geojson)  272 rows
"""
import argparse, hashlib, json, os, subprocess, urllib.request

SOURCES = {
    "ca_counties_geo": "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/california-counties.geojson",
    "la_neighborhoods_geo": "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/los-angeles-county.geojson",
}


def round_coords(c, nd=3):
    if isinstance(c[0], (int, float)):
        return [round(c[0], nd), round(c[1], nd)]
    return [round_coords(x, nd) for x in c]


def build_table(table, url, profile, warehouse, schema, nd=3):
    gj = json.loads(urllib.request.urlopen(url).read())
    rows = []
    for f in gj["features"]:
        name = f["properties"].get("name", "")
        f["geometry"]["coordinates"] = round_coords(f["geometry"]["coordinates"], nd)
        # deterministic demo value 0-100 so the choropleth has color variation
        val = round(int(hashlib.md5(name.encode()).hexdigest(), 16) % 1000 / 10.0, 1)
        rows.append("('{}',{},'{}')".format(
            name.replace("'", "''"), val, json.dumps(f["geometry"]).replace("'", "''")))
    sql = (f"CREATE OR REPLACE TABLE {schema}.{table} AS SELECT * FROM VALUES\n"
           + ",\n".join(rows) + "\nAS t(name, value, geojson)")
    out = subprocess.run(
        ["databricks", "api", "post", "/api/2.0/sql/statements", "-p", profile,
         "--json", json.dumps({"warehouse_id": warehouse, "statement": sql, "wait_timeout": "50s"})],
        capture_output=True, text=True)
    state = json.loads(out.stdout).get("status", {}).get("state")
    print(f"{schema}.{table}: {len(rows)} rows -> {state}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--warehouse", required=True)
    ap.add_argument("--schema", default=os.environ.get("VEGA_SCHEMA", "pb_demo.custom_gallery"),
                    help="target <catalog>.<schema> (must already exist)")
    a = ap.parse_args()
    for table, url in SOURCES.items():
        build_table(table, url, a.profile, a.warehouse, a.schema)
