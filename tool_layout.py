import base64
from email.mime import message
import io
import tempfile #temporäre Dateien auf Rechner
import os #wieder löschen

from dash import Dash, html, dcc, dash_table, Input, Output, State
import pandas as pd

from tool_service import run_balancing_from_excel

#App erzeugen
app = Dash(__name__)

def make_upload_component():
    return dcc.Upload(
        id="upload-file",
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
        multiple=False
    )
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

    html.A( #user manual
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
    dcc.Store(id="stored-file-data"), #damit Datai gelöscht werden kann, Datai gespeichert


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
                "backgroundColor": "#EF773C",
                "color": "white",
                "border": "none",
                "borderRadius": "6px",
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
@app.callback(
    Output("stored-file-data", "data"),
    Input("upload-file", "contents"),
    State("upload-file", "filename"),
    prevent_initial_call=True
)
def store_uploaded_file(contents, filename):
    if contents is None:
        return None
    return {
        "contents": contents,
        "filename": filename
    }
@app.callback(
    Output("stored-file-data", "clear_data"),
    Output("uploaded-file-info", "children", allow_duplicate=True),
    Output("uploaded-file-validation", "children", allow_duplicate=True),
    Output("status-message", "children", allow_duplicate=True),
    Output("results-table", "children", allow_duplicate=True),
    Input("remove-file-button", "n_clicks"),
    prevent_initial_call=True
)
def remove_uploaded_file(n_clicks):
    return True, "No file uploaded yet.", "", "", ""


def validate_uploaded_excel(decoded_bytes):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsm") as tmp:
            tmp_path = tmp.name

        with open(tmp_path, "wb") as f:
            f.write(decoded_bytes)

        xls = pd.ExcelFile(tmp_path)

        if "Balancing" not in xls.sheet_names:
            return False, "Missing required sheet: 'Balancing'"

        # Table 1
        table1 = pd.read_excel(tmp_path, sheet_name="Balancing", usecols="B:D", skiprows=3, nrows=4, header=None)
        # Table 2
        table2 = pd.read_excel(tmp_path, sheet_name="Balancing", usecols="F:H", skiprows=3, nrows=7, header=None)
        # Table 3
        table3 = pd.read_excel(tmp_path, sheet_name="Balancing", usecols="J:L", skiprows=3, nrows=6, header=None)

        if table1.dropna(how="all").shape[0] < 4:
            return False, "Table 1 in sheet 'Balancing' is incomplete."

        if table2.dropna(how="all").shape[0] < 7:
            return False, "Table 2 in sheet 'Balancing' is incomplete."

        if table3.dropna(how="all").shape[0] < 6:
            return False, "Table 3 in sheet 'Balancing' is incomplete."

        return True, "File structure looks valid."

    except Exception as e:
        return False, f"Validation failed: {str(e)}"

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except PermissionError:
                pass

@app.callback(
    Output("uploaded-file-validation", "children"),
    Input("upload-file", "contents"),
    prevent_initial_call=True
)
def validate_uploaded_file(contents):
    if contents is None:
        return ""

    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        is_valid, message = validate_uploaded_excel(decoded)

        if is_valid:
            return html.Div([
                html.Span("✓ ", style={"color": "#24DB82", "fontWeight": "bold"}),
                html.Span(message, style={"color": "#24DB82", "fontWeight": "bold"})
            ])
        else:
            return html.Div([
                html.Span("✗ ", style={"color": "red", "fontWeight": "bold"}),
                html.Span(message, style={"color": "red", "fontWeight": "bold"})
            ])

    except Exception as e:
        return html.Span(f"Validation failed: {str(e)}", style={"color": "red", "fontWeight": "bold"})



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
    Output("upload-container", "children"),
    Input("remove-file-button", "n_clicks"),
    prevent_initial_call=True
)
def reset_upload_component(n_clicks):
    return make_upload_component()



@app.callback(
    Output("status-message", "children"),
    Output("results-table", "children"),
    Input("run-button", "n_clicks"),
    State("stored-file-data", "data"),
    prevent_initial_call=True
)


def run_calculation(n_clicks, stored_file_data):
    if stored_file_data is None:
        return "Please upload an Excel file first.", ""

    contents = stored_file_data["contents"]
    filename = stored_file_data["filename"]

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
