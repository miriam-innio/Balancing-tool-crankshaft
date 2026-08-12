import os
import tempfile
import pandas as pd


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

        table1 = pd.read_excel(tmp_path, sheet_name="Balancing", usecols="B:D", skiprows=3, nrows=4, header=None)
        table2 = pd.read_excel(tmp_path, sheet_name="Balancing", usecols="F:H", skiprows=3, nrows=7, header=None)
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
