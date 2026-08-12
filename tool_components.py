from dash import html, dcc, dash_table
#make_upload_component(), make_table(), tab_style, tab_selected_style

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
