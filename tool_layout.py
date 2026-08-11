import base64
import io
import tempfile #temporäre Dateien auf Rechner
import os #wieder löschen

from dash import Dash, html, dcc, dash_table, Input, Output, State
import pandas as pd

from tool_service import run_balancing_from_excel

#App erzeugen
app = Dash(__name__)

#Layout
app.layout = html.Div([
    html.H1( #titel (Überschrift)
        "Balancing Tool",
        style={
            "textAlign": "center",
            "fontFamily": "'Segoe UI', Arial, sans-serif",
            "marginBottom": "10px"
        }
    ), 

    html.P( #Description 
        "Upload an Excel input file, run the balancing calculation, and review the results.",
        style={
            "textAlign": "center",
            "fontFamily": "'Segoe UI', Arial, sans-serif",
            "fontSize": "16px",
            "color": "#555555",
            "marginBottom": "10px"
        }
    ),

    #html.A(
        #"Open User Manual",
        #href="/assets/User_Manual.pdf",
        #target="_blank",
        #style={
            #"display": "block",
            #"textAlign": "center",
            #"fontFamily": "'Segoe UI', Arial, sans-serif",
            #"marginBottom": "30px",
            #"color": "#1f77b4",
            #"textDecoration": "none",
            #"fontWeight": "bold"
        #}
    #),


    dcc.Upload(
        id="upload-file",
        #text der im Upload-Feld angezeigt wird
        children=html.Div([
            "Drag and Drop or ",
            html.A("Select an Excel File")
        ]),
        style={
            "width": "50%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "8px",
            "textAlign": "center",
            "fontFamily": "'Segoe UI', Arial, sans-serif",
            "color": "#444444",
            "margin": "20px auto"

        },
        multiple=False #nur 1 Datei
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
        html.Button(
            "Run Calculation",
            id="run-button",
            n_clicks=0,
            style={
                "fontSize": "18px",
                "padding": "12px 24px",
                "backgroundColor": "#2e8b57",
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
    #Platzhalter für Statusmeldung

    html.Div(
        id="status-message",
        style={
            "marginTop": "20px",
            "fontFamily": "'Segoe UI', Arial, sans-serif"
        }
    ),
#Platzhalter für Ergebnistabelle
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

#automatisch aufgerufen, wenn Button gedrückt wird
@app.callback(
    Output("uploaded-file-info", "children"),
    Input("upload-file", "filename")
)
def show_uploaded_filename(filename): #direkt zeigen file uploaded und welche Datei
    if filename is None:
        return "No file uploaded yet."
    
    return html.Div([
        html.Span("✓ Uploaded file: ", style={"color": "#2e8b57", "fontWeight": "bold"}),
        html.Span(filename)
    ])

@app.callback(
    Output("status-message", "children"),
    Output("results-table", "children"),
    Input("run-button", "n_clicks"),
    State("upload-file", "contents"),
    State("upload-file", "filename"),
    prevent_initial_call=True
)

def run_calculation(n_clicks, contents, filename):
    if contents is None:
        return "Please upload an Excel file first.", ""

    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        #temporäre Datei erzeugen, um die Excel-Datei zu speichern
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsm") as tmp:
            tmp.write(decoded)
            tmp_path = tmp.name

        result = run_balancing_from_excel(tmp_path, sheet_name="Balancing")
        df = result["results_df"]

        table = dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in df.columns],
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "center",
                "padding": "8px",
                "fontFamily": "'Segoe UI', Arial, sans-serif"
            },
            style_header={
                "fontWeight": "bold",
                "backgroundColor": "#f2f2f2"
            }
        )

        os.remove(tmp_path)

        return f"Calculation successful: {filename}", table

    except Exception as e:
        return f"Error: {str(e)}", ""
    
#app nur starten, wenn das Skript direkt ausgeführt wird
if __name__ == "__main__": 
    app.run(debug=True)
