from dash import Dash, html, dcc

from tool_components import make_upload_component
from tool_callbacks import register_callbacks

#App erzeugen, Layout definieren, Komponenten importieren
#Callbacks registrieren, App starten

app = Dash(__name__)

app.layout = html.Div([
    html.H1(
        "Balancing Tool",
        style={
            "textAlign": "center",
            "fontFamily": "'Segoe UI', Arial, sans-serif",
            "marginBottom": "10px"
        }
    ),

    html.P(
        "Upload an Excel input file, run the balancing calculation, and review the results.",
        style={
            "textAlign": "center",
            "fontFamily": "'Segoe UI', Arial, sans-serif",
            "fontSize": "16px",
            "color": "#555555",
            "marginBottom": "10px"
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
            "marginBottom": "30px",
            "color": "#EF773C",
            "textDecoration": "none",
            "fontWeight": "bold"
        }
    ),

    dcc.Store(id="stored-file-data"),

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
    ),

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
    )
],
style={
    "fontFamily": "'Segoe UI', Arial, sans-serif",
    "padding": "30px"
})

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
