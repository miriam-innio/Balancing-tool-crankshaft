import os
import tempfile
import pandas as pd


def check_required_columns(table, table_name, expected_rows):
    for i in range(expected_rows):
        description = table.iloc[i, 0]
        unit = table.iloc[i, 1]
        value = table.iloc[i, 2]

        field_name = description if pd.notna(description) and str(description).strip() != "" else f"row {i + 1}"

        if pd.isna(unit) or str(unit).strip() == "":
            return False, f"{table_name}: missing unit for '{field_name}'."

        if pd.isna(value) or str(value).strip() == "":
            return False, f"{table_name}: missing value for '{field_name}'."

    return True, None


def check_throw_table(throw_info, n_throw):
    if throw_info.dropna(how="all").shape[0] == 0:
        return False, "Table 4: no throw angle cases found."

    for row_idx in range(len(throw_info)):
        case_number = throw_info.iloc[row_idx, 0]

        if pd.isna(case_number) or str(case_number).strip() == "":
            return False, f"Table 4: missing case number in row {row_idx + 1}."

        for throw_idx in range(1, n_throw + 1):
            value = throw_info.iloc[row_idx, throw_idx] if throw_idx < throw_info.shape[1] else None

            if pd.isna(value) or str(value).strip() == "":
                return False, f"Table 4: missing throw angle for case '{case_number}' in Throw {throw_idx}."

    return True, None


def validate_uploaded_excel(decoded_bytes):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsm") as tmp:
            tmp_path = tmp.name

        with open(tmp_path, "wb") as f:
            f.write(decoded_bytes)

        xls = pd.ExcelFile(tmp_path)

        if "Balancing" not in xls.sheet_names:
            return False, "Missing required sheet: 'Balancing'."

        table1 = pd.read_excel(
            tmp_path,
            sheet_name="Balancing",
            usecols="B:D",
            skiprows=3,
            nrows=4,
            header=None
        )

        table2 = pd.read_excel(
            tmp_path,
            sheet_name="Balancing",
            usecols="F:H",
            skiprows=3,
            nrows=7,
            header=None
        )

        table3 = pd.read_excel(
            tmp_path,
            sheet_name="Balancing",
            usecols="J:L",
            skiprows=3,
            nrows=6,
            header=None
        )

        if table1.dropna(how="all").shape[0] < 4:
            return False, "Table 1 in sheet 'Balancing' is incomplete."

        if table2.dropna(how="all").shape[0] < 7:
            return False, "Table 2 in sheet 'Balancing' is incomplete."

        if table3.dropna(how="all").shape[0] < 6:
            return False, "Table 3 in sheet 'Balancing' is incomplete."

        ok, message = check_required_columns(table1, "Table 1", 4)
        if not ok:
            return False, message

        ok, message = check_required_columns(table2, "Table 2", 7)
        if not ok:
            return False, message

        ok, message = check_required_columns(table3, "Table 3", 6)
        if not ok:
            return False, message

        # Table 4 prüfen
        n_cyl = int(table1.iloc[1, 2])
        cyl_arr = str(table1.iloc[2, 2]).strip()
        n_throw = n_cyl // 2 if cyl_arr == "Vee" else n_cyl

        throw_info = pd.read_excel(
            tmp_path,
            sheet_name="Balancing",
            usecols=range(13, 13 + n_throw + 1),
            skiprows=3,
            header=None
        ).dropna(how="all")

        ok, message = check_throw_table(throw_info, n_throw)
        if not ok:
            return False, message

        return True, "File structure looks valid."

    except Exception as e:
        return False, f"Validation failed: {str(e)}"

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except PermissionError:
                pass
