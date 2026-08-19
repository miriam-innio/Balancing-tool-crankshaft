import base64
import os
import tempfile

import pandas as pd
from dash import html, dcc, Input, Output, State

from tool_service import run_balancing_from_excel
from tool_input_output import read_input_tables
from tool_components import (
    clean_display_dataframe,
    make_table,
    tab_style,
    tab_selected_style,
)


def build_export_box():
    return html.Div([
        html.Details([
            html.Summary(
                "Export Results",
                style={
                    "cursor": "pointer",
                    "fontWeight": "bold",
                    "fontFamily": "'Segoe UI', Arial, sans-serif",
                    "color": "#444444"
                }
            ),
            html.Div([
                html.P(
                    "Download the full results table as an Excel file.",
                    style={
                        "fontFamily": "'Segoe UI', Arial, sans-serif",
                        "color": "#555555",
                        "marginTop": "10px"
                    }
                ),
                html.Button(
                    "Download Full Results",
                    id="download-results-button",
                    n_clicks=0,
                    style={
                        "fontSize": "14px",
                        "padding": "10px 18px",
                        "backgroundColor": "#24DB82",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "6px",
                        "cursor": "pointer",
                        "fontFamily": "'Segoe UI', Arial, sans-serif",
                        "fontWeight": "bold",
                        "marginTop": "10px"
                    }
                )
            ])
        ])
    ], style={
        "backgroundColor": "white",
        "border": "1px solid #e0e0e0",
        "borderRadius": "10px",
        "padding": "20px",
        "width": "60%",
        "margin": "25px auto 25px auto",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.08)"
    })


def build_input_box(table1, table2, table3, table4):
    return html.Div([
        html.Details([
            html.Summary(
                "See Input Data",
                style={
                    "cursor": "pointer",
                    "fontWeight": "bold",
                    "fontFamily": "'Segoe UI', Arial, sans-serif",
                    "color": "#444444"
                }
            ),
            html.Div([
                dcc.Tabs([
                    dcc.Tab(
                        label="Table 1",
                        children=[html.Br(), make_table(table1)],
                        style=tab_style,
                        selected_style=tab_selected_style
                    ),
                    dcc.Tab(
                        label="Table 2",
                        children=[html.Br(), make_table(table2)],
                        style=tab_style,
                        selected_style=tab_selected_style
                    ),
                    dcc.Tab(
                        label="Table 3",
                        children=[html.Br(), make_table(table3)],
                        style=tab_style,
                        selected_style=tab_selected_style
                    ),
                    dcc.Tab(
                        label="Table 4",
                        children=[html.Br(), make_table(table4)],
                        style=tab_style,
                        selected_style=tab_selected_style
                    ),
                ])
            ])
        ])
    ], style={
        "backgroundColor": "white",
        "border": "1px solid #e0e0e0",
        "borderRadius": "10px",
        "padding": "20px",
        "width": "60%",
        "margin": "25px auto 25px auto",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.08)"
    })


def register_results_callbacks(app):

    @app.callback(
        Output("status-message", "children"),
        Output("results-table", "children"),
        Output("export-section", "children"),
        Output("input-section", "children"),
        Output("stored-results-data", "data"),
        Input("run-button", "n_clicks"),
        State("stored-file-data", "data"),
        prevent_initial_call=True
    )
    def run_calculation(n_clicks, stored_file_data):
        if stored_file_data is None:
            return "Please upload an Excel file first.", "", "", "", None

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

            overview_df = df[[
                "Case number", "Balancing ratio", "F_r (N)", "M_r (Nmm)",
                "F_o 1H (N)", "F_o 1V (N)", "M_o 1H (Nmm)", "M_o 1V (Nmm)"
            ]]

            rotating_df = df[
                ["Case number", "Balancing ratio", "F_r (N)", "M_r (Nmm)"]
            ]

            low_order_df = df[[
                "Case number",
                "F_o 1H (N)", "F_o 1V (N)", "M_o 1H (Nmm)", "M_o 1V (Nmm)"
            ]]

            high_order_df = df[[
                "Case number",
                "F_o 4H (N)", "F_o 4V (N)", "M_o 4H (Nmm)", "M_o 4V (Nmm)",
                "F_o 6H (N)", "F_o 6V (N)", "M_o 6H (Nmm)", "M_o 6V (Nmm)",
                "F_o 8H (N)", "F_o 8V (N)", "M_o 8H (Nmm)", "M_o 8V (Nmm)"
            ]]

            full_df = df.copy()

            overview_df = clean_display_dataframe(overview_df, threshold=1e-2, decimals=2)
            rotating_df = clean_display_dataframe(rotating_df, threshold=1e-2, decimals=2)
            low_order_df = clean_display_dataframe(low_order_df, threshold=1e-2, decimals=2)
            high_order_df = clean_display_dataframe(high_order_df, threshold=1e-2, decimals=2)
            full_df_display = clean_display_dataframe(full_df, threshold=1e-2, decimals=2)

            table1, table2, table3, table4 = read_input_tables(tmp_path, sheet_name="Balancing")

            tabs = dcc.Tabs([
                dcc.Tab(
                    label="Overview",
                    children=[html.Br(), make_table(overview_df)],
                    style=tab_style,
                    selected_style=tab_selected_style
                ),
                dcc.Tab(
                    label="Rotating",
                    children=[html.Br(), make_table(rotating_df)],
                    style=tab_style,
                    selected_style=tab_selected_style
                ),
                dcc.Tab(
                    label="Oscillating Low Order Harmonics",
                    children=[html.Br(), make_table(low_order_df)],
                    style=tab_style,
                    selected_style=tab_selected_style
                ),
                dcc.Tab(
                    label="Oscillating High Order Harmonics",
                    children=[html.Br(), make_table(high_order_df)],
                    style=tab_style,
                    selected_style=tab_selected_style
                ),
                dcc.Tab(
                    label="Full Results",
                    children=[html.Br(), make_table(full_df_display)],
                    style=tab_style,
                    selected_style=tab_selected_style
                )
            ])

            export_box = build_export_box()
            input_box = build_input_box(table1, table2, table3, table4)

            stored_results = {
                "data": full_df.to_dict("records"),
                "columns": list(full_df.columns)
            }

            return (
                f"Calculation successful: {filename}",
                tabs,
                export_box,
                input_box,
                stored_results
            )

        except Exception as e:
            return f"Error: {str(e)}", "", "", "", None

        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except PermissionError:
                    pass

    @app.callback(
        Output("download-results-excel", "data"),
        Input("download-results-button", "n_clicks"),
        State("stored-results-data", "data"),
        prevent_initial_call=True
    )
    def download_results_excel(n_clicks, stored_results):
        if not stored_results or n_clicks is None or n_clicks == 0:
            return None

        df = pd.DataFrame(
            stored_results["data"],
            columns=stored_results["columns"]
        )

        return dcc.send_data_frame(
            df.to_excel,
            "full_results.xlsx",
            index=False
        )
