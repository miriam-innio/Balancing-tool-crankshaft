from dash import Dash, html, dcc

from tool_components import make_upload_component
from tool_callbacks_upload import register_upload_callbacks
from tool_callbacks_results import register_results_callbacks

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1(
        "Balancing Tool",
        style={
            "textAlign": "center",
            "fontFamily": "'Segoe UI', Arial, sans-serif",
            "marginBottom": "10px"
        }
    ),

    html.Div([
        html.P(
            "Upload an Excel input file, run the balancing calculation, and review the results.",
            style={
                "textAlign": "center",
                "fontFamily": "'Segoe UI', Arial, sans-serif",
                "fontSize": "16px",
                "color": "#555555",
                "marginBottom": "10px",
                "marginTop": "0"
            }
        ),

        html.A(
            "Open User Manual",
            href="/assets/User Manual.pdf",
            target="_blank",
            style={
                "display": "block",
                "textAlign": "center",
                "fontFamily": "'Segoe UI', Arial, sans-serif",
                "color": "#EF773C",
                "textDecoration": "none",
                "fontWeight": "bold"
            }
        )
    ], style={
        "backgroundColor": "white",
        "border": "1px solid #e0e0e0",
        "borderRadius": "10px",
        "padding": "20px",
        "width": "60%",
        "margin": "0 auto 25px auto",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.08)"
    }),

    dcc.Store(id="stored-file-data"),
    dcc.Store(id="stored-results-data"),

    html.Div([
        html.Div(
            id="upload-container",
            children=make_upload_component()
        ),

        html.Div(
            id="uploaded-file-info",
            style={
                "textAlign": "center",
                "marginTop": "10px",
                "fontFamily": "'Segoe UI', Arial, sans-serif",
                "color": "#444444"
            }
        ),

        html.Div(
            id="uploaded-file-validation",
            style={
                "textAlign": "center",
                "marginTop": "6px",
                "fontFamily": "'Segoe UI', Arial, sans-serif",
                "color": "#444444"
            }
        ),

        html.Div(
            html.Button(
                "Remove File",
                id="remove-file-button",
                n_clicks=0,
                style={
                    "fontSize": "14px",
                    "padding": "8px 16px",
                    "backgroundColor": "transparent",
                    "color": "#EF773C",
                    "border": "none",
                    "cursor": "pointer",
                    "fontFamily": "'Segoe UI', Arial, sans-serif",
                    "fontWeight": "bold"
                }
            ),
            style={
                "textAlign": "center",
                "marginTop": "10px"
            }
        )
    ], style={
        "backgroundColor": "white",
        "border": "1px solid #e0e0e0",
        "borderRadius": "10px",
        "padding": "20px",
        "width": "60%",
        "margin": "0 auto 25px auto",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.08)"
    }),

    html.Div(
        html.Button(
            "Run Calculation",
            id="run-button",
            n_clicks=0,
            style={
                "fontSize": "18px",
                "padding": "12px 24px",
                "backgroundColor": "#24DB82",
                "color": "white",
                "border": "none",
                "borderRadius": "8px",
                "cursor": "pointer",
                "fontFamily": "'Segoe UI', Arial, sans-serif",
                "fontWeight": "bold"
            }
        ),
        style={
            "textAlign": "right",
            "marginTop": "30px",
            "marginRight": "10%"
        }
    ),

    html.Div(
        id="status-message",
        style={
            "marginTop": "20px",
            "fontFamily": "'Segoe UI', Arial, sans-serif"
        }
    ),

    html.Div(
        id="results-table",
        style={
            "marginTop": "20px",
            "fontFamily": "'Segoe UI', Arial, sans-serif"
        }
    ),

    html.Div(
        id="export-section",
        style={
            "marginTop": "25px"
        }
    ),

    html.Div(
        id="input-section",
        style={
            "marginTop": "25px"
        }
    ),
    html.Div(
        id="plot-section",
        style={
            "marginTop": "25px"
        }
    ),

    dcc.Download(id="download-results-excel")
], style={
    "fontFamily": "'Segoe UI', Arial, sans-serif",
    "padding": "30px"
})

register_upload_callbacks(app)
register_results_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
