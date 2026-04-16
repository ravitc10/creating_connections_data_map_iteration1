import json
from pathlib import Path
import os

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html


# ----------------------------
# Files
# ----------------------------
JSON_FILE = Path("DEL_test1_tsne.json")
CSV_FILE = Path("DEL_test1.csv")

if not JSON_FILE.exists():
    raise FileNotFoundError(f"Missing {JSON_FILE.resolve()}")

if not CSV_FILE.exists():
    raise FileNotFoundError(f"Missing {CSV_FILE.resolve()}")


# ----------------------------
# Load data
# ----------------------------
coords = json.loads(JSON_FILE.read_text(encoding="utf-8"))
coords_df = pd.DataFrame(coords)

csv_df = pd.read_csv(CSV_FILE)

# Combine JSON + CSV
df = pd.concat([coords_df, csv_df], axis=1)


# ----------------------------
# 🔥 BULLETPROOF COLUMN FIX
# ----------------------------

# Clean column names (remove spaces, force string)
df.columns = df.columns.map(str).str.strip()

# Remove duplicate columns safely
df = df.loc[:, ~df.columns.duplicated()].copy()

# Helper to safely extract a single column (avoids DataFrame issue)
def get_column(df, col_name):
    cols = [c for c in df.columns if c == col_name]
    if len(cols) == 0:
        raise ValueError(f"Column '{col_name}' not found. Available: {list(df.columns)}")
    return df[cols[0]]  # guarantees Series

# Extract correctly
Code_col = get_column(df, "Code")
Data_col = get_column(df, "Data")

# Clean values
df["Code"] = Code_col.fillna("").astype(str).str.strip()
df["Data"] = Data_col.fillna("").astype(str).str.strip()

# Coordinates
df["x"] = df["x"].astype(float)
df["y"] = df["y"].astype(float)


# ----------------------------
# Wrap text for hover
# ----------------------------
def wrap_text(text, width=60):
    words = text.split()
    lines, current = [], []

    for w in words:
        if sum(len(x) for x in current) + len(current) + len(w) > width:
            lines.append(" ".join(current))
            current = [w]
        else:
            current.append(w)

    if current:
        lines.append(" ".join(current))

    return "<br>".join(lines)


df["wrapped_data"] = df["Data"].apply(lambda x: wrap_text(x, 60))


# ----------------------------
# Color mapping
# ----------------------------
pastel_colors = [
    "#AEC6CF", "#FFB7B2", "#B5EAD7", "#FFDAC1",
    "#C7CEEA", "#E2F0CB", "#FF9AA2", "#D5AAFF"
]

unique_codes = sorted(df["Code"].unique())

color_map = {
    code: pastel_colors[i % len(pastel_colors)]
    for i, code in enumerate(unique_codes)
}


# ----------------------------
# Build figure
# ----------------------------
fig = go.Figure()

for code in unique_codes:
    subset = df[df["Code"] == code]

    fig.add_trace(
        go.Scatter(
            x=subset["x"],
            y=subset["y"],
            mode="markers",
            marker=dict(size=12, color=color_map[code]),
            customdata=subset[["Code", "wrapped_data"]].values,
            hovertemplate="<b>%{customdata[0]}</b><br><br>%{customdata[1]}<extra></extra>",
            showlegend=False,
        )
    )

fig.update_layout(
    title="DEL Creating Connections Data Visualization",
    showlegend=False,
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(l=10, r=10, t=50, b=10),
    plot_bgcolor="#f9fafb",
    paper_bgcolor="#f9fafb",
    hoverlabel=dict(bgcolor="white", font_size=13, align="left"),
)


# ----------------------------
# Custom key
# ----------------------------
legend_items = []
for code in unique_codes:
    legend_items.append(
        html.Div(
            style={"display": "flex", "alignItems": "center", "marginBottom": "6px"},
            children=[
                html.Div(
                    style={
                        "width": "12px",
                        "height": "12px",
                        "backgroundColor": color_map[code],
                        "marginRight": "8px",
                        "borderRadius": "50%",
                    }
                ),
                html.Span(code),
            ],
        )
    )


# ----------------------------
# Dash app
# ----------------------------
app = Dash(__name__)

app.layout = html.Div(
    style={
        "display": "flex",
        "flexDirection": "column",
        "height": "100vh",
        "padding": "10px",
        "fontFamily": "system-ui",
        "backgroundColor": "#eef2f7",
    },
    children=[

        html.Div(
            style={"textAlign": "center", "marginBottom": "10px"},
            children=[
                html.H2("DEL Teacher Residency 2026"),
                html.P("Hover over a point to read the data point."),
            ],
        ),

        html.Div(
            style={"display": "flex", "height": "92vh"},
            children=[

                html.Div(
                    style={"width": "200px", "padding": "10px"},
                    children=[html.H4("Key"), *legend_items],
                ),

                html.Div(
                    style={
                        "flex": "1",
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                    },
                    children=[
                        html.Div(
                            style={
                                "width": "95%",
                                "height": "95%",
                                "backgroundColor": "white",
                                "borderRadius": "16px",
                                "boxShadow": "0px 10px 30px rgba(0,0,0,0.15)",
                                "padding": "10px",
                            },
                            children=[
                                dcc.Graph(
                                    figure=fig,
                                    style={"height": "100%", "width": "100%"},
                                )
                            ],
                        )
                    ],
                ),
            ],
        ),
    ],
)


# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8050"))
    app.run(host="0.0.0.0", port=port, debug=False)