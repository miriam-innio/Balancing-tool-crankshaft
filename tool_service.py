import numpy as np
from tool_balancing_core import mass_forces
from tool_input_output import read_input_excel, build_results_dataframe


def run_balancing_from_excel(file_path, sheet_name="Balancing", phi=None):
    if phi is None:
        phi = np.arange(0, 360, 1)

    inputs = read_input_excel(file_path, sheet_name=sheet_name)

    ratio_r, fry, frz, mry, mrz, harm_ord, foy, foz, moy, moz = mass_forces(
        inputs["eng_conf"],
        inputs["crankshaft_geo"],
        inputs["masses"],
        inputs["throw_angles_mat"],
        phi,
    )

    results_df = build_results_dataframe(
        inputs["case_number"],
        ratio_r,
        fry,
        frz,
        mry,
        mrz,
        foy,
        foz,
        moy,
        moz,
    )

    return {
        "inputs": inputs,
        "phi": phi,
        "harm_ord": harm_ord,
        "raw_results": {
            "ratio_r": ratio_r,
            "fry": fry,
            "frz": frz,
            "mry": mry,
            "mrz": mrz,
            "foy": foy,
            "foz": foz,
            "moy": moy,
            "moz": moz,
        },
        "results_df": results_df,
    }
