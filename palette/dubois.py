"""Du Bois design-system palette for Vega-Lite charts.

Tokens sourced from Databricks' own Du Bois / AppKit implementations:
  - Du Bois brand hues + status + surfaces: databricks/app-templates index.css
  - AppKit structured viz ramps (categorical / sequential / diverging):
    databricks/appkit packages/appkit-ui (HSLA -> hex).

Validated with the dataviz skill's validate_palette.js:
  - categorical CVD separation: 23.6 (light) / 14.6 (dark)  [target >= 12]  PASS
  - contrast flags on a few light fills are handled by always shipping a legend /
    direct labels (identity is never color-alone).

The AI/BI dashboard canvas in this workspace renders dark, so `mode="dark"` is the
default. `dubois_config()` sets only color RANGES + mark/view defaults and leaves
axis/legend/title text colors unset, so AI/BI's own theme keeps text readable in
whichever mode the viewer picks.
"""

# ---- Categorical (fixed order; assign in order, never cycle) ----
CATEGORICAL_LIGHT = ["#2463EB", "#2EB88A", "#AB47BD", "#F69E23",
                     "#DD2C4D", "#1BA3BB", "#9B61D1", "#34B262"]
CATEGORICAL_DARK  = ["#5593F7", "#42D7A5", "#CB70DB", "#FAB338",
                     "#EC516D", "#1DCDED", "#B481E4", "#47D17A"]

# Du Bois brand chart-1..5 (on-brand alternate categorical)
DUBOIS_BRAND_5 = ["#2272B4", "#277C43", "#BE501E", "#C82D4C", "#9B6AE8"]

# ---- Sequential single-hue blue (low -> high) ----
SEQUENTIAL_LIGHT = ["#E5ECFA", "#BDCFF4", "#8CABEE", "#5986E8",
                    "#2562E4", "#154CC1", "#0F3995", "#0A2A71"]
SEQUENTIAL_DARK  = ["#204079", "#2B5199", "#2E6BC4", "#4F87DB",
                    "#62A0E9", "#7DBAF2", "#A6D1F8", "#C6E4FB"]

# ---- Diverging (blue <-> red, neutral middle) ----
DIVERGING = ["#123FA1", "#265FD9", "#7594D7", "#C1CBE1",
             "#E1C6C1", "#DB8270", "#DB4224", "#B83014"]

# ---- Status / semantic (Du Bois) ----
STATUS = {"success": "#277C43", "warning": "#BE501E",
          "danger": "#C82D4C", "info": "#2272B4"}

# ---- Surfaces / ink / grid ----
SURFACE = {
    "light": {"bg": "#FFFFFF", "ink": "#11171C", "ink2": "#5F7281", "grid": "#E8ECF0"},
    "dark":  {"bg": "#11171C", "ink": "#E8ECF0", "ink2": "#BDCDD9", "grid": "#2A3A45"},
}

BRAND = "#2272B4"       # Du Bois primary / brand action
FONT = "DM Sans, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"


def categorical(mode: str = "dark"):
    return CATEGORICAL_DARK if mode == "dark" else CATEGORICAL_LIGHT


def sequential(mode: str = "dark"):
    return SEQUENTIAL_DARK if mode == "dark" else SEQUENTIAL_LIGHT


def dubois_config(mode: str = "dark") -> dict:
    """Vega-Lite `config` block applying Du Bois styling to any spec.

    Sets color ranges + recessive marks/grid; leaves text colors to the AI/BI
    theme so labels stay legible in the viewer's light/dark mode.
    """
    cat = categorical(mode)
    seq = sequential(mode)
    return {
        "background": None,                 # inherit the dashboard card surface
        "view": {"stroke": None},
        "font": FONT,
        "range": {
            "category": cat,
            "ordinal": seq,
            "heatmap": seq,
            "ramp": seq,
            "diverging": DIVERGING,
        },
        "arc": {"stroke": SURFACE[mode]["bg"], "strokeWidth": 1},
        "bar": {"cornerRadiusEnd": 3},
        "line": {"strokeWidth": 2},
        "area": {"opacity": 0.85, "line": True},
        "point": {"filled": True, "size": 64},
        "rect": {"stroke": None},
        "axis": {"grid": True, "gridColor": SURFACE[mode]["grid"], "gridOpacity": 0.6,
                 "domainColor": SURFACE[mode]["grid"], "tickColor": SURFACE[mode]["grid"],
                 "labelFont": FONT, "titleFont": FONT, "labelFontSize": 11, "titleFontSize": 12},
        "legend": {"labelFont": FONT, "titleFont": FONT, "labelFontSize": 11, "titleFontSize": 12},
        "title": {"font": FONT, "fontSize": 13, "fontWeight": 600, "anchor": "start"},
    }


def dubois_theme() -> dict:
    """The Du Bois palette as an AI/BI dashboard THEME (uiSettings.theme).

    Unlike dubois_config() — which themes the Vega-Lite custom-viz specs — this
    themes the whole dashboard so that NATIVE (out-of-the-box) widgets render in
    the Du Bois palette too. `visualizationColors` is the categorical series
    order; canvas/widget/font mirror the Du Bois dark+light surfaces.
    """
    return {
        "canvasBackgroundColor": {"light": SURFACE["light"]["bg"], "dark": "#1F272D"},
        "widgetBackgroundColor": {"light": "#FFFFFF", "dark": SURFACE["dark"]["bg"]},
        "fontColor": {"light": SURFACE["light"]["ink"], "dark": SURFACE["dark"]["ink"]},
        "selectionColor": {"light": BRAND, "dark": CATEGORICAL_DARK[0]},
        # categorical series order (dark tuned; two neutral overflow slots at 9-10)
        "visualizationColors": CATEGORICAL_DARK + ["#92A4B3", "#C6E4FB"],
        "widgetHeaderAlignment": "LEFT",
    }
