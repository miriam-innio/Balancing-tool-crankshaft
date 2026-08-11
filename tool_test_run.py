from tool_service import run_balancing_from_excel
from tool_input_output import write_results_excel

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

input_file = "Balancing_HeatenV16.xlsm"
output_file = "Tool_Results.xlsx"

result = run_balancing_from_excel(input_file, sheet_name="Balancing")
write_results_excel(result["results_df"], output_file)

print("Done. Results written to", output_file)
