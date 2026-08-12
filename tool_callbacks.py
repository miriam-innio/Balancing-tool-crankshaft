import base64
import os
import tempfile

from dash import html, dcc, Input, Output, State

from tool_service import run_balancing_from_excel
from tool_components import make_upload_component, make_table, tab_style, tab_selected_style
from tool_validation import validate_uploaded_excel

#show_uploaded_filename, store_uploaded_file, remove_uploaded_file
#validate_uploaded_file, reset_upload_component, run_calculation

def register_callbacks(app):

    @app.callback(
        Output("uploaded-file-info", "children"),
        Input("upload-file", "filename")
    )
    def show_uploaded_filename(filename):
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

        tmp_path = None
        try:
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsm") as tmp:
                tmp_path = tmp.name

            with open(tmp_path, "wb") as f:
                f.write(decoded)

            result = run_balancing_from_excel(tmp_path, sheet_name="Balancing")
            df = result["results_df"]

            overview_df = df[["Case number", "Balancing ratio", "F_r (N)", "M_r (Nmm)"]]
            low_order_df = df[["Case number", "F_o 1H (N)", "F_o 1V (N)", "M_o 1H (Nmm)", "M_o 1V (Nmm)"]]
            high_order_df = df[[
                "Case number",
                "F_o 4H (N)", "F_o 4V (N)", "M_o 4H (Nmm)", "M_o 4V (Nmm)",
                "F_o 6H (N)", "F_o 6V (N)", "M_o 6H (Nmm)", "M_o 6V (Nmm)",
                "F_o 8H (N)", "F_o 8V (N)", "M_o 8H (Nmm)", "M_o 8V (Nmm)"
            ]]
            full_df = df

            tabs = dcc.Tabs([
                dcc.Tab(
                    label="Overview",
                    children=[html.Br(), make_table(overview_df)],
                    style=tab_style,
                    selected_style=tab_selected_style
                ),
                dcc.Tab(
                    label="Low Order Harmonics (1H / 2H)",
                    children=[html.Br(), make_table(low_order_df)],
                    style=tab_style,
                    selected_style=tab_selected_style
                ),
                dcc.Tab(
                    label="High Order Harmonics (4H / 6H / 8H)",
                    children=[html.Br(), make_table(high_order_df)],
                    style=tab_style,
                    selected_style=tab_selected_style
                ),
                dcc.Tab(
                    label="Full Results",
                    children=[html.Br(), make_table(full_df)],
                    style=tab_style,
                    selected_style=tab_selected_style
                )
            ])

            return f"Calculation successful: {filename}", tabs

        except Exception as e:
            return f"Error: {str(e)}", ""

        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except PermissionError:
                    pass
