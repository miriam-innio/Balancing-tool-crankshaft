import base64

from dash import html, Input, Output, State

from tool_components import make_upload_component
from tool_validation import validate_uploaded_excel


def register_upload_callbacks(app):

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
        Output("status-message", "children", allow_duplicate=True),
        Output("results-table", "children", allow_duplicate=True),
        Output("export-section", "children", allow_duplicate=True),
        Output("input-section", "children", allow_duplicate=True),
        Output("stored-results-data", "clear_data", allow_duplicate=True),
        Input("upload-file", "contents"),
        prevent_initial_call=True
    )
    def clear_old_results_on_new_upload(contents):
        return "", "", "", "", True


    @app.callback(
        Output("stored-file-data", "clear_data"),
        Output("uploaded-file-info", "children", allow_duplicate=True),
        Output("uploaded-file-validation", "children", allow_duplicate=True),
        Output("status-message", "children", allow_duplicate=True),
        Output("results-table", "children", allow_duplicate=True),
        Output("export-section", "children", allow_duplicate=True),
        Output("input-section", "children", allow_duplicate=True),
        Output("stored-results-data", "clear_data"),
        Output("plot-section", "children", allow_duplicate=True),
        Input("remove-file-button", "n_clicks"),
        prevent_initial_call=True
    )
    def remove_uploaded_file(n_clicks):
        return True, "No file uploaded yet.", "", "", "", "", "", "", True

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
            return html.Span(
                f"Validation failed: {str(e)}",
                style={"color": "red", "fontWeight": "bold"}
            )

    @app.callback(
        Output("upload-container", "children"),
        Input("remove-file-button", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_upload_component(n_clicks):
        return make_upload_component()
