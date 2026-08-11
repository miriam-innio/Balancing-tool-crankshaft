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

    html.A(
        "Open User Manual",
        href="assets/User Manual.pdf",
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
                "backgroundColor": "#24DB82", #INNIO grün!!! orange: EF773C
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
        html.Span("✓ Uploaded file: ", style={"color": "#24DB82", "fontWeight": "bold"}),
        html.Span(filename)
    ])

def make_table(dataframe):
    return dash_table.DataTable(
        data=dataframe.to_dict("records"),
        columns=[{"name": col, "id": col} for col in dataframe.columns],
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

tab_style = {
    "fontFamily": "'Segoe UI', Arial, sans-serif",
    "padding": "10px 16px",
    "backgroundColor": "#f9f9f9",
    "color": "#444444",
    "borderLeft": "1px solid #dddddd",
    "borderRight": "1px solid #dddddd",
    "borderBottom": "1px solid #dddddd",
    "borderTop": "3px solid transparent"
}

tab_selected_style = {
    "fontFamily": "'Segoe UI', Arial, sans-serif",
    "padding": "10px 16px",
    "backgroundColor": "white",
    "color": "#24DB82",
    "fontWeight": "600",
    "borderLeft": "1px solid #dddddd",
    "borderRight": "1px solid #dddddd",
    "borderBottom": "1px solid white",
    "borderTop": "3px solid #24DB82"
}


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
        df = result["results_df"] #alles in DataFrame
        overview_df = df[["Case number", "Balancing ratio", "F_r (N)", "M_r (Nmm)"]]
        low_order_df = df[["Case number", "F_o 1H (N)", "F_o 1V (N)", "M_o 1H (Nmm)", "M_o 1V (Nmm)"]]
        high_order_df = df[["Case number", "F_o 4H (N)", "F_o 4V (N)", "M_o 4H (Nmm)", "M_o 4V (Nmm)",
                             "F_o 6H (N)", "F_o 6V (N)", "M_o 6H (Nmm)", "M_o 6V (Nmm)", 
                             "F_o 8H (N)", "F_o 8V (N)", "M_o 8H (Nmm)", "M_o 8V (Nmm)"]]
        full_df = df 


        os.remove(tmp_path)
        
        tabs = dcc.Tabs([
    dcc.Tab(
        label="Overview",
        children=[
            html.Br(),
            make_table(overview_df)
        ],
        style=tab_style,
        selected_style=tab_selected_style
    ),
    dcc.Tab(
        label="Low Order Harmonics (1H / 2H)",
        children=[
            html.Br(),
            make_table(low_order_df)
        ],
        style=tab_style,
        selected_style=tab_selected_style
    ),
    dcc.Tab(
        label="High Order Harmonics (4H / 6H / 8H)",
        children=[
            html.Br(),
            make_table(high_order_df)
        ],
        style=tab_style,
        selected_style=tab_selected_style
    ),
    dcc.Tab(
        label="Full Results",
        children=[
            html.Br(),
            make_table(full_df)
        ],
        style=tab_style,
        selected_style=tab_selected_style
    )
])

        return f"Calculation successful: {filename}", tabs

    except Exception as e:
        return f"Error: {str(e)}", ""
    
#app nur starten, wenn das Skript direkt ausgeführt wird
if __name__ == "__main__": 
    app.run(debug=True)
