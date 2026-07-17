"""Extreme & Experimental custom visualizations. Specs are Vega-Lite
WITHOUT config/data/width/height (the build script injects Du Bois config +
databricks_query binding + container sizing)."""

CATEGORY = "Extreme & Experimental"

CHARTS = [
    {
        "id": "ext_internet_spiral",
        "title": "Spiral — Global Internet Users (1995–2025)",
        "sql": "\n            SELECT * FROM VALUES\n              (1995,  1, 16,      0.0,   0.3),\n              (1998,  2, 147,     0.3,   2.9),\n              (2000,  3, 413,     2.9,  10.2),\n              (2003,  4, 778,    10.2,  24.0),\n              (2005,  5, 1030,   24.0,  42.2),\n              (2008,  6, 1574,   42.2,  70.1),\n              (2010,  7, 2023,   70.1, 105.9),\n              (2013,  8, 2802,  105.9, 155.5),\n              (2015,  9, 3366,  155.5, 215.0),\n              (2018, 10, 4208,  215.0, 289.4),\n              (2020, 11, 4833,  289.4, 374.9),\n              (2023, 12, 5450,  374.9, 471.3),\n              (2025, 13, 5800,  471.3, 573.9)\n            AS t(year, seq, users_m, start_angle, end_angle)\n        ",
        "fields": [
            "year",
            "seq",
            "users_m",
            "start_angle",
            "end_angle"
        ],
        "w": 6,
        "spec": {
            "transform": [
                {
                    "calculate": "datum.start_angle * PI / 180",
                    "as": "theta1"
                },
                {
                    "calculate": "datum.end_angle * PI / 180",
                    "as": "theta2"
                },
                {
                    "calculate": "15 + datum.seq * 11",
                    "as": "inner_r"
                },
                {
                    "calculate": "15 + datum.seq * 11 + 9",
                    "as": "outer_r"
                },
                {
                    "calculate": "datum.end_angle * PI / 180",
                    "as": "end_theta"
                },
                {
                    "calculate": "(datum.outer_r + 8) * cos(datum.end_theta)",
                    "as": "year_x"
                },
                {
                    "calculate": "(datum.outer_r + 8) * sin(datum.end_theta)",
                    "as": "year_y"
                },
                {
                    "calculate": "datum.inner_r * cos(datum.theta1)",
                    "as": "ix1"
                },
                {
                    "calculate": "datum.inner_r * sin(datum.theta1)",
                    "as": "iy1"
                },
                {
                    "calculate": "datum.outer_r * cos(datum.theta1)",
                    "as": "ox1"
                },
                {
                    "calculate": "datum.outer_r * sin(datum.theta1)",
                    "as": "oy1"
                },
                {
                    "calculate": "datum.outer_r * cos(datum.theta2)",
                    "as": "ox2"
                },
                {
                    "calculate": "datum.outer_r * sin(datum.theta2)",
                    "as": "oy2"
                },
                {
                    "calculate": "datum.inner_r * cos(datum.theta2)",
                    "as": "ix2"
                },
                {
                    "calculate": "datum.inner_r * sin(datum.theta2)",
                    "as": "iy2"
                },
                {
                    "calculate": "(datum.end_angle - datum.start_angle) > 180 ? 1 : 0",
                    "as": "large_arc"
                },
                {
                    "calculate": "'M' + datum.ox1 + ',' + datum.oy1 + ' A' + datum.outer_r + ',' + datum.outer_r + ' 0 ' + datum.large_arc + ' 1 ' + datum.ox2 + ',' + datum.oy2 + ' L' + datum.ix2 + ',' + datum.iy2 + ' A' + datum.inner_r + ',' + datum.inner_r + ' 0 ' + datum.large_arc + ' 0 ' + datum.ix1 + ',' + datum.iy1 + ' Z'",
                    "as": "arc_path"
                },
                {
                    "calculate": "format(datum.users_m, ',') + 'M'",
                    "as": "users_label"
                }
            ],
            "layer": [
                {
                    "mark": {
                        "type": "point",
                        "shape": {
                            "expr": "datum.arc_path"
                        },
                        "opacity": 1,
                        "stroke": "#999",
                        "strokeWidth": 0.5
                    },
                    "encoding": {
                        "x": {
                            "datum": 0,
                            "type": "quantitative",
                            "scale": {
                                "domain": [
                                    -200,
                                    200
                                ]
                            },
                            "axis": None
                        },
                        "y": {
                            "datum": 0,
                            "type": "quantitative",
                            "scale": {
                                "domain": [
                                    -200,
                                    200
                                ]
                            },
                            "axis": None
                        },
                        "fill": {
                            "field": "seq",
                            "type": "quantitative",
                            "scale": {
                                "domain": [
                                    1,
                                    13
                                ],
                                "range": [
                                    "#5B9BD5",
                                    "#3E7D53",
                                    "#D4A017",
                                    "#DC4B34",
                                    "#8A7B5C",
                                    "#5B9BD5",
                                    "#3E7D53",
                                    "#D4A017",
                                    "#DC4B34",
                                    "#8A7B5C",
                                    "#5B9BD5",
                                    "#3E7D53",
                                    "#DC4B34"
                                ]
                            },
                            "legend": None
                        },
                        "size": {
                            "value": 1
                        },
                        "tooltip": [
                            {
                                "field": "year",
                                "title": "Year"
                            },
                            {
                                "field": "users_label",
                                "title": "Internet Users"
                            }
                        ]
                    }
                },
                {
                    "mark": {
                        "type": "text",
                        "fontSize": 8,
                        "fontWeight": "bold",
                        "color": "#888"
                    },
                    "encoding": {
                        "x": {
                            "field": "year_x",
                            "type": "quantitative"
                        },
                        "y": {
                            "field": "year_y",
                            "type": "quantitative"
                        },
                        "text": {
                            "field": "year",
                            "type": "nominal"
                        }
                    }
                },
                {
                    "data": {
                        "values": [
                            {
                                "x": 0,
                                "y": -5,
                                "t": "GLOBAL INTERNET"
                            },
                            {
                                "x": 0,
                                "y": 5,
                                "t": "USERS (MILLIONS)"
                            }
                        ]
                    },
                    "mark": {
                        "type": "text",
                        "fontSize": 7,
                        "fontWeight": "bold",
                        "color": "#888"
                    },
                    "encoding": {
                        "x": {
                            "field": "x",
                            "type": "quantitative"
                        },
                        "y": {
                            "field": "y",
                            "type": "quantitative"
                        },
                        "text": {
                            "field": "t",
                            "type": "nominal"
                        }
                    }
                }
            ]
        }
    }
,
    {
        "id": "adv_dubois_fan",
        "title": "Du Bois Fan Chart — Land Ownership Proportions by Decade",
        "sql": "\n            SELECT * FROM VALUES\n              ('1874', 1, 'Owned',     4,   0.0,   14.4),\n              ('1874', 1, 'Rented',   92,  14.4,  345.6),\n              ('1874', 1, 'Other',     4,  345.6, 360.0),\n              ('1880', 2, 'Owned',     8,   0.0,   28.8),\n              ('1880', 2, 'Rented',   85,  28.8,  334.8),\n              ('1880', 2, 'Other',     7,  334.8, 360.0),\n              ('1886', 3, 'Owned',    14,   0.0,   50.4),\n              ('1886', 3, 'Rented',   76,  50.4,  324.0),\n              ('1886', 3, 'Other',    10,  324.0, 360.0),\n              ('1890', 4, 'Owned',    19,   0.0,   68.4),\n              ('1890', 4, 'Rented',   69,  68.4,  316.8),\n              ('1890', 4, 'Other',    12,  316.8, 360.0),\n              ('1895', 5, 'Owned',    24,   0.0,   86.4),\n              ('1895', 5, 'Rented',   62,  86.4,  309.6),\n              ('1895', 5, 'Other',    14,  309.6, 360.0),\n              ('1899', 6, 'Owned',    31,   0.0,  111.6),\n              ('1899', 6, 'Rented',   53, 111.6,  302.4),\n              ('1899', 6, 'Other',    16,  302.4, 360.0)\n            AS t(decade, ring, category, pct, start_deg, end_deg)\n        ",
        "fields": [
            "decade",
            "ring",
            "category",
            "pct",
            "start_deg",
            "end_deg"
        ],
        "w": 6,
        "spec": {
            "transform": [
                {
                    "calculate": "datum.start_deg * PI / 180",
                    "as": "theta1"
                },
                {
                    "calculate": "datum.end_deg * PI / 180",
                    "as": "theta2"
                },
                {
                    "calculate": "15 + (datum.ring - 1) * 25",
                    "as": "inner_r"
                },
                {
                    "calculate": "15 + (datum.ring - 1) * 25 + 22",
                    "as": "outer_r"
                },
                {
                    "calculate": "(datum.end_deg - datum.start_deg) > 180 ? 1 : 0",
                    "as": "lg"
                },
                {
                    "calculate": "datum.inner_r * cos(datum.theta1)",
                    "as": "ix1"
                },
                {
                    "calculate": "datum.inner_r * sin(datum.theta1)",
                    "as": "iy1"
                },
                {
                    "calculate": "datum.outer_r * cos(datum.theta1)",
                    "as": "ox1"
                },
                {
                    "calculate": "datum.outer_r * sin(datum.theta1)",
                    "as": "oy1"
                },
                {
                    "calculate": "datum.outer_r * cos(datum.theta2)",
                    "as": "ox2"
                },
                {
                    "calculate": "datum.outer_r * sin(datum.theta2)",
                    "as": "oy2"
                },
                {
                    "calculate": "datum.inner_r * cos(datum.theta2)",
                    "as": "ix2"
                },
                {
                    "calculate": "datum.inner_r * sin(datum.theta2)",
                    "as": "iy2"
                },
                {
                    "calculate": "'M' + datum.ox1 + ',' + datum.oy1 + ' A' + datum.outer_r + ',' + datum.outer_r + ' 0 ' + datum.lg + ' 1 ' + datum.ox2 + ',' + datum.oy2 + ' L' + datum.ix2 + ',' + datum.iy2 + ' A' + datum.inner_r + ',' + datum.inner_r + ' 0 ' + datum.lg + ' 0 ' + datum.ix1 + ',' + datum.iy1 + ' Z'",
                    "as": "arc_path"
                },
                {
                    "calculate": "datum.category === 'Owned' ? '#DC4B34' : datum.category === 'Rented' ? '#3E7D53' : '#D4A017'",
                    "as": "clr"
                },
                {
                    "calculate": "(datum.outer_r + 8) * cos(datum.theta2)",
                    "as": "lbl_x"
                },
                {
                    "calculate": "(datum.outer_r + 8) * sin(datum.theta2)",
                    "as": "lbl_y"
                }
            ],
            "layer": [
                {
                    "mark": {
                        "type": "point",
                        "shape": {
                            "expr": "datum.arc_path"
                        },
                        "opacity": 1,
                        "stroke": "#F4E3C9",
                        "strokeWidth": 0.5
                    },
                    "encoding": {
                        "x": {
                            "datum": 0,
                            "type": "quantitative",
                            "scale": {
                                "domain": [
                                    -200,
                                    200
                                ]
                            },
                            "axis": None
                        },
                        "y": {
                            "datum": 0,
                            "type": "quantitative",
                            "scale": {
                                "domain": [
                                    -200,
                                    200
                                ]
                            },
                            "axis": None
                        },
                        "fill": {
                            "field": "clr",
                            "type": "nominal",
                            "scale": None,
                            "legend": None
                        },
                        "size": {
                            "value": 1
                        },
                        "tooltip": [
                            {
                                "field": "decade",
                                "title": "Decade"
                            },
                            {
                                "field": "category",
                                "title": "Type"
                            },
                            {
                                "field": "pct",
                                "title": "Percent"
                            }
                        ]
                    }
                },
                {
                    "transform": [
                        {
                            "filter": "datum.category === 'Owned'"
                        }
                    ],
                    "mark": {
                        "type": "text",
                        "fontSize": 9,
                        "fontWeight": "bold",
                        "color": "#888"
                    },
                    "encoding": {
                        "x": {
                            "field": "lbl_x",
                            "type": "quantitative"
                        },
                        "y": {
                            "field": "lbl_y",
                            "type": "quantitative"
                        },
                        "text": {
                            "field": "decade",
                            "type": "nominal"
                        }
                    }
                },
                {
                    "data": {
                        "values": [
                            {
                                "x": -160,
                                "y": -140,
                                "label": "■ Owned",
                                "c": "#DC4B34"
                            },
                            {
                                "x": -160,
                                "y": -155,
                                "label": "■ Rented",
                                "c": "#3E7D53"
                            },
                            {
                                "x": -160,
                                "y": -170,
                                "label": "■ Other",
                                "c": "#D4A017"
                            }
                        ]
                    },
                    "mark": {
                        "type": "text",
                        "fontSize": 11,
                        "align": "left",
                        "fontWeight": "bold",
                        "color": "#888"
                    },
                    "encoding": {
                        "x": {
                            "field": "x",
                            "type": "quantitative"
                        },
                        "y": {
                            "field": "y",
                            "type": "quantitative"
                        },
                        "text": {
                            "field": "label",
                            "type": "nominal"
                        },
                        "color": {
                            "field": "c",
                            "type": "nominal",
                            "scale": None
                        }
                    }
                }
            ]
        }
    }
,
    {
        "id": "adv_wordcloud",
        "title": "Word Cloud — Technology Buzzwords by Frequency",
        "sql": "\n            SELECT * FROM VALUES\n              ('AI',           95, 'Core',      0.12, 0.45),\n              ('ML',           88, 'Core',     -0.30, 0.20),\n              ('LLM',          92, 'Core',      0.35,-0.15),\n              ('GPT',          85, 'Core',     -0.15,-0.35),\n              ('Cloud',        78, 'Infra',     0.55, 0.10),\n              ('Kubernetes',   72, 'Infra',    -0.50,-0.10),\n              ('Docker',       65, 'Infra',     0.10,-0.55),\n              ('Serverless',   58, 'Infra',    -0.40, 0.50),\n              ('Blockchain',   45, 'Web3',      0.65,-0.40),\n              ('NFT',          30, 'Web3',     -0.60, 0.35),\n              ('Web3',         35, 'Web3',      0.45, 0.60),\n              ('DeFi',         28, 'Web3',     -0.25, 0.65),\n              ('Python',       90, 'Lang',      0.20,-0.25),\n              ('Rust',         70, 'Lang',     -0.55,-0.45),\n              ('TypeScript',   75, 'Lang',      0.50, 0.35),\n              ('Go',           60, 'Lang',     -0.10, 0.10),\n              ('DevOps',       68, 'Practice',  0.30, 0.25),\n              ('MLOps',        62, 'Practice', -0.35,-0.55),\n              ('DataOps',      50, 'Practice',  0.60, 0.55),\n              ('GitOps',       42, 'Practice', -0.65, 0.15),\n              ('RAG',          82, 'AI',       -0.20,-0.10),\n              ('Embeddings',   55, 'AI',        0.40,-0.50),\n              ('Transformers', 80, 'AI',       -0.45, 0.40),\n              ('Fine-tuning',  73, 'AI',        0.15, 0.55),\n              ('Edge AI',      48, 'AI',       -0.55, 0.60)\n            AS t(word, freq, category, x_pos, y_pos)\n        ",
        "fields": [
            "word",
            "freq",
            "category",
            "x_pos",
            "y_pos"
        ],
        "w": 6,
        "spec": {
            "transform": [
                {
                    "calculate": "datum.freq / 10",
                    "as": "font_size"
                }
            ],
            "mark": {
                "type": "text",
                "fontWeight": "bold",
                "baseline": "middle",
                "align": "center"
            },
            "encoding": {
                "x": {
                    "field": "x_pos",
                    "type": "quantitative",
                    "scale": {
                        "domain": [
                            -0.8,
                            0.8
                        ]
                    },
                    "axis": None
                },
                "y": {
                    "field": "y_pos",
                    "type": "quantitative",
                    "scale": {
                        "domain": [
                            -0.8,
                            0.8
                        ]
                    },
                    "axis": None
                },
                "text": {
                    "field": "word",
                    "type": "nominal"
                },
                "size": {
                    "field": "freq",
                    "type": "quantitative",
                    "scale": {
                        "range": [
                            10,
                            40
                        ]
                    },
                    "legend": None
                },
                "color": {
                    "field": "category",
                    "type": "nominal",
                    "scale": {
                        "domain": [
                            "Core",
                            "Infra",
                            "Web3",
                            "Lang",
                            "Practice",
                            "AI"
                        ],
                        "range": [
                            "#DC4B34",
                            "#3E7D53",
                            "#D4A017",
                            "#5B9BD5",
                            "#8A7B5C",
                            "#241E1E"
                        ]
                    },
                    "title": "Category"
                },
                "tooltip": [
                    {
                        "field": "word",
                        "title": "Term"
                    },
                    {
                        "field": "freq",
                        "title": "Score"
                    },
                    {
                        "field": "category",
                        "title": "Category"
                    }
                ]
            }
        }
    }
,
    {
        "id": "adv_qr_visual",
        "title": "QR Code Style — Monthly P&L Binary Grid",
        "sql": "\n            WITH months AS (\n              SELECT * FROM VALUES\n                (0,0,1,'Jan-22','Profit'),(1,0,1,'Feb-22','Profit'),(2,0,0,'Mar-22','Loss'),\n                (3,0,1,'Apr-22','Profit'),(4,0,0,'May-22','Loss'),(5,0,1,'Jun-22','Profit'),\n                (6,0,1,'Jul-22','Profit'),(0,1,0,'Aug-22','Loss'),(1,1,1,'Sep-22','Profit'),\n                (2,1,1,'Oct-22','Profit'),(3,1,0,'Nov-22','Loss'),(4,1,1,'Dec-22','Profit'),\n                (5,1,1,'Jan-23','Profit'),(6,1,0,'Feb-23','Loss'),(0,2,1,'Mar-23','Profit'),\n                (1,2,1,'Apr-23','Profit'),(2,2,1,'May-23','Profit'),(3,2,0,'Jun-23','Loss'),\n                (4,2,1,'Jul-23','Profit'),(5,2,0,'Aug-23','Loss'),(6,2,1,'Sep-23','Profit'),\n                (0,3,1,'Oct-23','Profit'),(1,3,0,'Nov-23','Loss'),(2,3,1,'Dec-23','Profit'),\n                (3,3,1,'Jan-24','Profit'),(4,3,1,'Feb-24','Profit'),(5,3,0,'Mar-24','Loss'),\n                (6,3,1,'Apr-24','Profit'),(0,4,0,'May-24','Loss'),(1,4,1,'Jun-24','Profit'),\n                (2,4,1,'Jul-24','Profit'),(3,4,1,'Aug-24','Profit'),(4,4,0,'Sep-24','Loss'),\n                (5,4,1,'Oct-24','Profit'),(6,4,1,'Nov-24','Profit'),\n                (0,5,1,'Dec-24','Profit'),(1,5,0,'Jan-25','Loss'),(2,5,1,'Feb-25','Profit'),\n                (3,5,1,'Mar-25','Profit'),(4,5,1,'Apr-25','Profit'),(5,5,0,'May-25','Loss'),\n                (6,5,1,'Jun-25','Profit'),\n                (0,6,1,'Jul-25','Profit'),(1,6,1,'Aug-25','Profit'),(2,6,0,'Sep-25','Loss'),\n                (3,6,1,'Oct-25','Profit'),(4,6,1,'Nov-25','Profit'),(5,6,1,'Dec-25','Profit'),\n                (6,6,0,'Jan-26','Loss')\n              AS t(col, row, filled, month_label, status)\n            ),\n            -- QR finder pattern: top-left corner (7x7 with 5x5 inner, 3x3 core)\n            corners AS (\n              SELECT * FROM VALUES\n                -- Top-left finder: border ring\n                (-4,8,1,'TL','Finder'),(-3,8,1,'TL','Finder'),(-2,8,1,'TL','Finder'),(-1,8,1,'TL','Finder'),(0,8,1,'TL','Finder'),\n                (-4,9,1,'TL','Finder'),(0,9,1,'TL','Finder'),\n                (-4,10,1,'TL','Finder'),(-2,10,1,'TL','Finder'),(0,10,1,'TL','Finder'),\n                (-4,11,1,'TL','Finder'),(0,11,1,'TL','Finder'),\n                (-4,12,1,'TL','Finder'),(-3,12,1,'TL','Finder'),(-2,12,1,'TL','Finder'),(-1,12,1,'TL','Finder'),(0,12,1,'TL','Finder'),\n                -- Top-right finder\n                (7,8,1,'TR','Finder'),(8,8,1,'TR','Finder'),(9,8,1,'TR','Finder'),(10,8,1,'TR','Finder'),(11,8,1,'TR','Finder'),\n                (7,9,1,'TR','Finder'),(11,9,1,'TR','Finder'),\n                (7,10,1,'TR','Finder'),(9,10,1,'TR','Finder'),(11,10,1,'TR','Finder'),\n                (7,11,1,'TR','Finder'),(11,11,1,'TR','Finder'),\n                (7,12,1,'TR','Finder'),(8,12,1,'TR','Finder'),(9,12,1,'TR','Finder'),(10,12,1,'TR','Finder'),(11,12,1,'TR','Finder'),\n                -- Bottom-left finder\n                (-4,-1,1,'BL','Finder'),(-3,-1,1,'BL','Finder'),(-2,-1,1,'BL','Finder'),(-1,-1,1,'BL','Finder'),(0,-1,1,'BL','Finder'),\n                (-4,0,1,'BL','Finder'),(0,0,1,'BL','Finder'),\n                (-4,1,1,'BL','Finder'),(-2,1,1,'BL','Finder'),(0,1,1,'BL','Finder'),\n                (-4,2,1,'BL','Finder'),(0,2,1,'BL','Finder'),\n                (-4,3,1,'BL','Finder'),(-3,3,1,'BL','Finder'),(-2,3,1,'BL','Finder'),(-1,3,1,'BL','Finder'),(0,3,1,'BL','Finder')\n              AS t(col, row, filled, month_label, status)\n            )\n            SELECT col, row, filled, month_label, status FROM months\n            UNION ALL\n            SELECT col, row, filled, month_label, status FROM corners\n        ",
        "fields": [
            "col",
            "row",
            "filled",
            "month_label",
            "status"
        ],
        "w": 3,
        "spec": {
            "mark": {
                "type": "rect",
                "stroke": "#F4E3C9",
                "strokeWidth": 0.5,
                "cornerRadius": 1
            },
            "encoding": {
                "x": {
                    "field": "col",
                    "type": "ordinal",
                    "axis": None
                },
                "y": {
                    "field": "row",
                    "type": "ordinal",
                    "axis": None,
                    "sort": "descending"
                },
                "fill": {
                    "condition": {
                        "test": "datum.filled === 1",
                        "value": "#241E1E"
                    },
                    "value": "#F4E3C9"
                },
                "tooltip": [
                    {
                        "field": "month_label",
                        "title": "Period"
                    },
                    {
                        "field": "status",
                        "title": "Status"
                    }
                ]
            }
        }
    }
,
    {
        "id": "adv_particle_trail",
        "title": "Particle Trails — Flowing Data Streams",
        "sql": "\n            WITH RECURSIVE seq AS (\n              SELECT 0 AS i UNION ALL SELECT i + 1 FROM seq WHERE i < 59\n            ),\n            particles AS (\n              SELECT\n                i,\n                p.particle,\n                p.phase,\n                p.amplitude,\n                -- x advances linearly\n                ROUND(i * 0.1, 2) AS t_val,\n                ROUND(i * 0.1 + p.phase, 2) AS x_pos,\n                -- y follows a sine wave offset by particle phase\n                ROUND(p.amplitude * SIN((i * 0.1 + p.phase) * 2.0), 4) AS y_pos,\n                -- Size varies sinusoidally for thickness pulsation\n                ROUND(ABS(SIN((i * 0.15 + p.phase) * 1.5)) * 8 + 2, 2) AS thickness,\n                p.group_name\n              FROM seq\n              CROSS JOIN (\n                SELECT * FROM VALUES\n                  (1, 0.0,  1.2, 'Alpha'),\n                  (2, 1.05, 0.9, 'Beta'),\n                  (3, 2.09, 1.5, 'Gamma'),\n                  (4, 3.14, 1.0, 'Delta'),\n                  (5, 4.19, 1.3, 'Epsilon'),\n                  (6, 5.24, 0.7, 'Zeta')\n                AS t(particle, phase, amplitude, group_name)\n              ) p\n            )\n            SELECT particle, t_val, x_pos, y_pos, thickness, group_name\n            FROM particles\n            ORDER BY particle, t_val\n        ",
        "fields": [
            "particle",
            "t_val",
            "x_pos",
            "y_pos",
            "thickness",
            "group_name"
        ],
        "w": 6,
        "spec": {
            "mark": {
                "type": "trail",
                "opacity": 0.75
            },
            "encoding": {
                "x": {
                    "field": "x_pos",
                    "type": "quantitative",
                    "title": "Flow Position",
                    "axis": {
                        "grid": False
                    }
                },
                "y": {
                    "field": "y_pos",
                    "type": "quantitative",
                    "title": "Amplitude",
                    "scale": {
                        "domain": [
                            -2,
                            2
                        ]
                    }
                },
                "size": {
                    "field": "thickness",
                    "type": "quantitative",
                    "scale": {
                        "range": [
                            1,
                            12
                        ]
                    },
                    "legend": None
                },
                "color": {
                    "field": "group_name",
                    "type": "nominal",
                    "scale": {
                        "domain": [
                            "Alpha",
                            "Beta",
                            "Gamma",
                            "Delta",
                            "Epsilon",
                            "Zeta"
                        ],
                        "range": [
                            "#DC4B34",
                            "#3E7D53",
                            "#5B9BD5",
                            "#D4A017",
                            "#8A7B5C",
                            "#241E1E"
                        ]
                    },
                    "title": "Stream"
                },
                "detail": {
                    "field": "particle",
                    "type": "nominal"
                },
                "order": {
                    "field": "t_val",
                    "type": "quantitative"
                },
                "tooltip": [
                    {
                        "field": "group_name",
                        "title": "Stream"
                    },
                    {
                        "field": "x_pos",
                        "title": "Position"
                    },
                    {
                        "field": "y_pos",
                        "title": "Amplitude"
                    },
                    {
                        "field": "thickness",
                        "title": "Width"
                    }
                ]
            }
        }
    }
,
    {
        "id": "ext_marimekko",
        "title": "Marimekko Chart — Market Share by Segment & Product",
        "sql": "\n            SELECT * FROM VALUES\n              ('Enterprise', 'Platform',   40, 0.0,  0.40, 0.0,  0.55),\n              ('Enterprise', 'Analytics',  40, 0.0,  0.40, 0.55, 0.85),\n              ('Enterprise', 'Services',   40, 0.0,  0.40, 0.85, 1.0),\n              ('Mid-Market', 'Platform',   25, 0.40, 0.65, 0.0,  0.40),\n              ('Mid-Market', 'Analytics',  25, 0.40, 0.65, 0.40, 0.72),\n              ('Mid-Market', 'Services',   25, 0.40, 0.65, 0.72, 1.0),\n              ('SMB',        'Platform',   20, 0.65, 0.85, 0.0,  0.30),\n              ('SMB',        'Analytics',  20, 0.65, 0.85, 0.30, 0.75),\n              ('SMB',        'Services',   20, 0.65, 0.85, 0.75, 1.0),\n              ('Startup',    'Platform',   15, 0.85, 1.00, 0.0,  0.60),\n              ('Startup',    'Analytics',  15, 0.85, 1.00, 0.60, 0.80),\n              ('Startup',    'Services',   15, 0.85, 1.00, 0.80, 1.0)\n            AS t(segment, product, seg_pct, x1, x2, y1, y2)\n        ",
        "fields": [
            "segment",
            "product",
            "seg_pct",
            "x1",
            "x2",
            "y1",
            "y2"
        ],
        "w": 6,
        "spec": {
            "transform": [
                {
                    "calculate": "format(round((datum.y2 - datum.y1) * 100), 'd') + '%'",
                    "as": "share_label"
                },
                {
                    "calculate": "(datum.x1 + datum.x2) / 2",
                    "as": "mid_x"
                },
                {
                    "calculate": "(datum.y1 + datum.y2) / 2",
                    "as": "mid_y"
                }
            ],
            "layer": [
                {
                    "mark": {
                        "type": "rect",
                        "stroke": "#555555",
                        "strokeWidth": 2,
                        "cornerRadius": 2
                    },
                    "encoding": {
                        "x": {
                            "field": "x1",
                            "type": "quantitative",
                            "scale": {
                                "domain": [
                                    0,
                                    1
                                ]
                            },
                            "axis": None
                        },
                        "x2": {
                            "field": "x2"
                        },
                        "y": {
                            "field": "y1",
                            "type": "quantitative",
                            "scale": {
                                "domain": [
                                    0,
                                    1
                                ]
                            },
                            "axis": None
                        },
                        "y2": {
                            "field": "y2"
                        },
                        "fill": {
                            "field": "product",
                            "type": "nominal",
                            "scale": {
                                "domain": [
                                    "Platform",
                                    "Analytics",
                                    "Services"
                                ],
                                "range": [
                                    "#DC4B34",
                                    "#3E7D53",
                                    "#D4A017"
                                ]
                            },
                            "title": "Product"
                        },
                        "tooltip": [
                            {
                                "field": "segment",
                                "title": "Segment"
                            },
                            {
                                "field": "product",
                                "title": "Product"
                            },
                            {
                                "field": "share_label",
                                "title": "Share"
                            }
                        ]
                    }
                },
                {
                    "mark": {
                        "type": "text",
                        "fontSize": 11,
                        "fontWeight": "bold",
                        "color": "#F4E3C9"
                    },
                    "encoding": {
                        "x": {
                            "field": "mid_x",
                            "type": "quantitative"
                        },
                        "y": {
                            "field": "mid_y",
                            "type": "quantitative"
                        },
                        "text": {
                            "field": "share_label",
                            "type": "nominal"
                        }
                    }
                },
                {
                    "transform": [
                        {
                            "filter": "datum.product === 'Services'"
                        }
                    ],
                    "mark": {
                        "type": "text",
                        "fontSize": 10,
                        "fontWeight": "bold",
                        "color": "#F4E3C9",
                        "baseline": "top",
                        "dy": 8
                    },
                    "encoding": {
                        "x": {
                            "field": "mid_x",
                            "type": "quantitative"
                        },
                        "y": {
                            "datum": 1,
                            "type": "quantitative"
                        },
                        "text": {
                            "field": "segment",
                            "type": "nominal"
                        }
                    }
                }
            ]
        }
    }
,
    {
        "id": "ext_bump_chart",
        "title": "Bump Chart — City Innovation Rankings Over Time",
        "sql": "\n            SELECT * FROM VALUES\n              ('San Francisco', 2019, 1), ('San Francisco', 2020, 1), ('San Francisco', 2021, 2), ('San Francisco', 2022, 2), ('San Francisco', 2023, 3),\n              ('Austin',        2019, 4), ('Austin',        2020, 3), ('Austin',        2021, 2), ('Austin',        2022, 1), ('Austin',        2023, 1),\n              ('New York',      2019, 2), ('New York',      2020, 2), ('New York',      2021, 3), ('New York',      2022, 4), ('New York',      2023, 4),\n              ('Seattle',       2019, 3), ('Seattle',       2020, 4), ('Seattle',       2021, 1), ('Seattle',       2022, 3), ('Seattle',       2023, 2),\n              ('Miami',         2019, 5), ('Miami',         2020, 5), ('Miami',         2021, 4), ('Miami',         2022, 5), ('Miami',         2023, 5),\n              ('Denver',        2019, 6), ('Denver',        2020, 6), ('Denver',        2021, 5), ('Denver',        2022, 6), ('Denver',        2023, 6)\n            AS t(city, year, rank)\n        ",
        "fields": [
            "city",
            "year",
            "rank"
        ],
        "w": 6,
        "spec": {
            "transform": [
                {
                    "calculate": "'#' + datum.rank",
                    "as": "rank_label"
                }
            ],
            "layer": [
                {
                    "mark": {
                        "type": "line",
                        "strokeWidth": 3,
                        "opacity": 0.85,
                        "interpolate": "monotone"
                    },
                    "encoding": {
                        "x": {
                            "field": "year",
                            "type": "ordinal",
                            "title": "Year",
                            "axis": {
                                "labelColor": "#F4E3C9",
                                "titleColor": "#F4E3C9",
                                "labelFontSize": 12
                            }
                        },
                        "y": {
                            "field": "rank",
                            "type": "quantitative",
                            "title": "Rank",
                            "sort": "descending",
                            "scale": {
                                "domain": [
                                    1,
                                    6
                                ]
                            },
                            "axis": {
                                "labelColor": "#F4E3C9",
                                "titleColor": "#F4E3C9",
                                "labelFontSize": 12
                            }
                        },
                        "color": {
                            "field": "city",
                            "type": "nominal",
                            "scale": {
                                "domain": [
                                    "San Francisco",
                                    "Austin",
                                    "New York",
                                    "Seattle",
                                    "Miami",
                                    "Denver"
                                ],
                                "range": [
                                    "#DC4B34",
                                    "#3E7D53",
                                    "#5B9BD5",
                                    "#D4A017",
                                    "#8A7B5C",
                                    "#B7A98F"
                                ]
                            },
                            "title": "City"
                        },
                        "detail": {
                            "field": "city",
                            "type": "nominal"
                        }
                    }
                },
                {
                    "mark": {
                        "type": "circle",
                        "size": 120,
                        "opacity": 1,
                        "stroke": "#555555",
                        "strokeWidth": 2
                    },
                    "encoding": {
                        "x": {
                            "field": "year",
                            "type": "ordinal"
                        },
                        "y": {
                            "field": "rank",
                            "type": "quantitative"
                        },
                        "fill": {
                            "field": "city",
                            "type": "nominal",
                            "scale": {
                                "domain": [
                                    "San Francisco",
                                    "Austin",
                                    "New York",
                                    "Seattle",
                                    "Miami",
                                    "Denver"
                                ],
                                "range": [
                                    "#DC4B34",
                                    "#3E7D53",
                                    "#5B9BD5",
                                    "#D4A017",
                                    "#8A7B5C",
                                    "#B7A98F"
                                ]
                            },
                            "legend": None
                        },
                        "tooltip": [
                            {
                                "field": "city",
                                "title": "City"
                            },
                            {
                                "field": "year",
                                "title": "Year"
                            },
                            {
                                "field": "rank_label",
                                "title": "Rank"
                            }
                        ]
                    }
                },
                {
                    "transform": [
                        {
                            "filter": "datum.year === 2023"
                        }
                    ],
                    "mark": {
                        "type": "text",
                        "align": "left",
                        "dx": 12,
                        "fontSize": 11,
                        "fontWeight": "bold",
                        "color": "#F4E3C9"
                    },
                    "encoding": {
                        "x": {
                            "field": "year",
                            "type": "ordinal"
                        },
                        "y": {
                            "field": "rank",
                            "type": "quantitative"
                        },
                        "text": {
                            "field": "city",
                            "type": "nominal"
                        }
                    }
                }
            ]
        }
    }
,
    {
        "id": "ext_waffle_chart",
        "title": "Waffle Chart — Energy Source Mix (Each Square = 1%)",
        "sql": "\n            WITH grid AS (\n              SELECT\n                s.i AS idx,\n                MOD(s.i, 10) AS col,\n                FLOOR(s.i / 10) AS row\n              FROM (\n                SELECT explode(sequence(0, 99)) AS i\n              ) s\n            )\n            SELECT\n              col, row, idx,\n              CASE\n                WHEN idx < 38 THEN 'Fossil Fuels'\n                WHEN idx < 60 THEN 'Natural Gas'\n                WHEN idx < 78 THEN 'Nuclear'\n                WHEN idx < 90 THEN 'Wind'\n                WHEN idx < 96 THEN 'Solar'\n                ELSE 'Hydro'\n              END AS source,\n              CASE\n                WHEN idx < 38 THEN '38%'\n                WHEN idx < 60 THEN '22%'\n                WHEN idx < 78 THEN '18%'\n                WHEN idx < 90 THEN '12%'\n                WHEN idx < 96 THEN '6%'\n                ELSE '4%'\n              END AS pct_label\n            FROM grid\n            ORDER BY idx\n        ",
        "fields": [
            "col",
            "row",
            "idx",
            "source",
            "pct_label"
        ],
        "w": 3,
        "spec": {
            "layer": [
                {
                    "mark": {
                        "type": "rect",
                        "stroke": "#555555",
                        "strokeWidth": 1.5,
                        "cornerRadius": 2
                    },
                    "encoding": {
                        "x": {
                            "field": "col",
                            "type": "ordinal",
                            "axis": None
                        },
                        "y": {
                            "field": "row",
                            "type": "ordinal",
                            "axis": None,
                            "sort": "descending"
                        },
                        "fill": {
                            "field": "source",
                            "type": "nominal",
                            "scale": {
                                "domain": [
                                    "Fossil Fuels",
                                    "Natural Gas",
                                    "Nuclear",
                                    "Wind",
                                    "Solar",
                                    "Hydro"
                                ],
                                "range": [
                                    "#DC4B34",
                                    "#D4A017",
                                    "#8A7B5C",
                                    "#3E7D53",
                                    "#5B9BD5",
                                    "#B7A98F"
                                ]
                            },
                            "title": "Source"
                        },
                        "tooltip": [
                            {
                                "field": "source",
                                "title": "Source"
                            },
                            {
                                "field": "pct_label",
                                "title": "Share"
                            }
                        ]
                    }
                },
                {
                    "data": {
                        "values": [
                            {
                                "x": 0,
                                "y": 0,
                                "label": "■ Fossil 38%",
                                "c": "#DC4B34"
                            },
                            {
                                "x": 0,
                                "y": 1,
                                "label": "■ Gas 22%",
                                "c": "#D4A017"
                            },
                            {
                                "x": 0,
                                "y": 2,
                                "label": "■ Nuclear 18%",
                                "c": "#8A7B5C"
                            },
                            {
                                "x": 3,
                                "y": 0,
                                "label": "■ Wind 12%",
                                "c": "#3E7D53"
                            },
                            {
                                "x": 3,
                                "y": 1,
                                "label": "■ Solar 6%",
                                "c": "#5B9BD5"
                            },
                            {
                                "x": 3,
                                "y": 2,
                                "label": "■ Hydro 4%",
                                "c": "#B7A98F"
                            }
                        ]
                    },
                    "mark": {
                        "type": "text",
                        "fontSize": 9,
                        "fontWeight": "bold",
                        "align": "left",
                        "dy": -8
                    },
                    "encoding": {
                        "x": {
                            "field": "x",
                            "type": "quantitative",
                            "scale": {
                                "domain": [
                                    0,
                                    9
                                ]
                            }
                        },
                        "y": {
                            "field": "y",
                            "type": "quantitative",
                            "scale": {
                                "domain": [
                                    -1,
                                    11
                                ]
                            }
                        },
                        "text": {
                            "field": "label",
                            "type": "nominal"
                        },
                        "color": {
                            "field": "c",
                            "type": "nominal",
                            "scale": None
                        }
                    }
                }
            ]
        }
    }
,
    {
        "id": "ext_connected_scatter",
        "title": "Connected Scatterplot — Revenue vs. Headcount Trajectory (2015–2024)",
        "sql": "\n            SELECT * FROM VALUES\n              (2015, 12.5,  120, 'Phase 1'),\n              (2016, 18.2,  145, 'Phase 1'),\n              (2017, 22.0,  200, 'Phase 1'),\n              (2018, 28.5,  310, 'Phase 2'),\n              (2019, 35.0,  380, 'Phase 2'),\n              (2020, 30.2,  350, 'Phase 2'),\n              (2021, 48.0,  520, 'Phase 3'),\n              (2022, 62.5,  680, 'Phase 3'),\n              (2023, 55.0,  600, 'Phase 3'),\n              (2024, 78.0,  850, 'Phase 3')\n            AS t(yr, revenue_m, headcount, phase)\n        ",
        "fields": [
            "yr",
            "revenue_m",
            "headcount",
            "phase"
        ],
        "w": 6,
        "spec": {
            "layer": [
                {
                    "mark": {
                        "type": "line",
                        "strokeWidth": 2,
                        "opacity": 0.6,
                        "color": "#B7A98F",
                        "interpolate": "monotone"
                    },
                    "encoding": {
                        "x": {
                            "field": "revenue_m",
                            "type": "quantitative",
                            "title": "Revenue ($M)",
                            "axis": {
                                "labelColor": "#F4E3C9",
                                "titleColor": "#F4E3C9",
                                "gridColor": "#3a3530"
                            }
                        },
                        "y": {
                            "field": "headcount",
                            "type": "quantitative",
                            "title": "Headcount",
                            "axis": {
                                "labelColor": "#F4E3C9",
                                "titleColor": "#F4E3C9",
                                "gridColor": "#3a3530"
                            }
                        },
                        "order": {
                            "field": "yr",
                            "type": "quantitative"
                        }
                    }
                },
                {
                    "mark": {
                        "type": "circle",
                        "size": 150,
                        "opacity": 1,
                        "stroke": "#F4E3C9",
                        "strokeWidth": 1.5
                    },
                    "encoding": {
                        "x": {
                            "field": "revenue_m",
                            "type": "quantitative"
                        },
                        "y": {
                            "field": "headcount",
                            "type": "quantitative"
                        },
                        "fill": {
                            "field": "phase",
                            "type": "nominal",
                            "scale": {
                                "domain": [
                                    "Phase 1",
                                    "Phase 2",
                                    "Phase 3"
                                ],
                                "range": [
                                    "#3E7D53",
                                    "#D4A017",
                                    "#DC4B34"
                                ]
                            },
                            "title": "Growth Phase"
                        },
                        "tooltip": [
                            {
                                "field": "yr",
                                "title": "Year"
                            },
                            {
                                "field": "revenue_m",
                                "title": "Revenue ($M)"
                            },
                            {
                                "field": "headcount",
                                "title": "Headcount"
                            },
                            {
                                "field": "phase",
                                "title": "Phase"
                            }
                        ]
                    }
                },
                {
                    "mark": {
                        "type": "text",
                        "fontSize": 10,
                        "fontWeight": "bold",
                        "color": "#F4E3C9",
                        "dx": 10,
                        "dy": -10
                    },
                    "encoding": {
                        "x": {
                            "field": "revenue_m",
                            "type": "quantitative"
                        },
                        "y": {
                            "field": "headcount",
                            "type": "quantitative"
                        },
                        "text": {
                            "field": "yr",
                            "type": "nominal"
                        }
                    }
                }
            ]
        }
    }
,
    {
        "id": "ext_isotype_pictogram",
        "title": "Isotype Pictogram — Global Population by Region (1 Figure = 50M People)",
        "sql": "\n            WITH regions AS (\n              SELECT * FROM VALUES\n                ('Asia',          4700, 0, '#DC4B34'),\n                ('Africa',        1400, 1, '#3E7D53'),\n                ('Europe',         750, 2, '#5B9BD5'),\n                ('Latin America',  650, 3, '#D4A017'),\n                ('North America',  370, 4, '#8A7B5C'),\n                ('Oceania',         50, 5, '#B7A98F')\n              AS t(region, pop_m, row_idx, clr)\n            ),\n            icons AS (\n              SELECT\n                r.region, r.row_idx, r.clr,\n                s.i AS col_idx,\n                r.pop_m,\n                CONCAT(CAST(ROUND(r.pop_m / 1000.0, 1) AS STRING), 'B') AS pop_label\n              FROM regions r\n              CROSS JOIN (SELECT explode(sequence(0, 99)) AS i) s\n              WHERE s.i < ROUND(r.pop_m / 50.0, 0)\n            )\n            SELECT region, row_idx, col_idx, clr, pop_m, pop_label FROM icons\n            ORDER BY row_idx, col_idx\n        ",
        "fields": [
            "region",
            "row_idx",
            "col_idx",
            "clr",
            "pop_m",
            "pop_label"
        ],
        "w": 6,
        "spec": {
            "layer": [
                {
                    "mark": {
                        "type": "text",
                        "fontSize": 12,
                        "baseline": "middle",
                        "align": "center"
                    },
                    "encoding": {
                        "x": {
                            "field": "col_idx",
                            "type": "ordinal",
                            "axis": None
                        },
                        "y": {
                            "field": "region",
                            "type": "nominal",
                            "sort": {
                                "field": "row_idx",
                                "order": "ascending"
                            },
                            "axis": {
                                "labelColor": "#F4E3C9",
                                "titleColor": "#F4E3C9",
                                "labelFontSize": 11,
                                "labelFontWeight": "bold",
                                "title": None
                            }
                        },
                        "text": {
                            "value": "▮"
                        },
                        "color": {
                            "field": "clr",
                            "type": "nominal",
                            "scale": None,
                            "legend": None
                        },
                        "tooltip": [
                            {
                                "field": "region",
                                "title": "Region"
                            },
                            {
                                "field": "pop_label",
                                "title": "Population"
                            }
                        ]
                    }
                },
                {
                    "transform": [
                        {
                            "aggregate": [
                                {
                                    "op": "max",
                                    "field": "col_idx",
                                    "as": "max_col"
                                },
                                {
                                    "op": "max",
                                    "field": "pop_label",
                                    "as": "pop_label"
                                },
                                {
                                    "op": "max",
                                    "field": "row_idx",
                                    "as": "row_idx"
                                },
                                {
                                    "op": "max",
                                    "field": "clr",
                                    "as": "clr"
                                }
                            ],
                            "groupby": [
                                "region"
                            ]
                        }
                    ],
                    "mark": {
                        "type": "text",
                        "fontSize": 11,
                        "fontWeight": "bold",
                        "color": "#F4E3C9",
                        "align": "left",
                        "dx": 6
                    },
                    "encoding": {
                        "x": {
                            "field": "max_col",
                            "type": "ordinal"
                        },
                        "y": {
                            "field": "region",
                            "type": "nominal",
                            "sort": {
                                "field": "row_idx",
                                "order": "ascending"
                            }
                        },
                        "text": {
                            "field": "pop_label",
                            "type": "nominal"
                        }
                    }
                }
            ]
        }
    }
,
]
