import pandas as pd
import os
import numpy as np


# Reusing the same encoder function for consistency
def to_toon(data, indent=0):
    spaces = " " * indent
    output = []

    if isinstance(data, dict):
        for key, value in data.items():
            # 1. Check for Tabular Data (List of Uniform Dicts)
            if isinstance(value, list) and value and isinstance(value[0], dict):
                keys = list(value[0].keys())
                # Ensure uniformity
                if all(isinstance(x, dict) and list(x.keys()) == keys for x in value):
                    # Header: key[N]{col1,col2}:
                    headers = ",".join(str(k) for k in keys)
                    output.append(f"{spaces}{key}[{len(value)}]{{{headers}}}:")
                    # Rows
                    for item in value:
                        row = []
                        for k in keys:
                            val = item.get(k)
                            if val is None or (isinstance(val, float) and np.isnan(val)):
                                row.append("null")
                            elif isinstance(val, (int, float, bool)):
                                row.append(str(val).lower())
                            else:
                                s_val = str(val)
                                if any(c in s_val for c in [",", "\n", ":", "{", "}"]):
                                    row.append(f'"{s_val}"')
                                else:
                                    row.append(s_val)
                        output.append(f"{spaces}  " + ",".join(row))
                    continue

            # 2. Recursive Dict
            if isinstance(value, dict):
                output.append(f"{spaces}{key}:")
                output.append(to_toon(value, indent + 2))

            # 3. Lists (Non-tabular)
            elif isinstance(value, list):
                if not value:
                    output.append(f"{spaces}{key}[0]:")
                elif isinstance(value[0], (int, float, bool, str)):
                    # Inline primitive list
                    clean_vals = []
                    for x in value:
                        if isinstance(x, str) and "," in x:
                            clean_vals.append(f'"{x}"')
                        else:
                            clean_vals.append(str(x))
                    output.append(f"{spaces}{key}[{len(value)}]: {', '.join(clean_vals)}")
                else:
                    # Complex/Mixed list
                    output.append(f"{spaces}{key}[{len(value)}]:")
                    for item in value:
                        output.append(to_toon(item, indent + 2))

            # 4. Primitives
            else:
                val_str = str(value)
                if isinstance(value, bool): val_str = val_str.lower()
                if value is None: val_str = "null"
                if pd.isna(value): val_str = "null"  # Handle numpy NaN

                # Quote if necessary
                if any(c in val_str for c in [",", "\n", ":"]):
                    val_str = f'"{val_str}"'

                output.append(f"{spaces}{key}: {val_str}")

        return "\n".join(output)
    return str(data)

def generate_metadata_toon_from_df(df: pd.DataFrame, file_name: str = "dataframe") -> str:
    """
    Generates a TOON metadata string directly from an in-memory DataFrame.
    """
    sample_rows = df.head(3).replace({np.nan: None}).to_dict('records')

    metadata = {
        "File_Name": file_name,
        "Total_Rows": int(df.shape[0]),
        "Total_Columns": int(df.shape[1]),
        "Sample_Rows_Head_3": sample_rows,
        "Column_Details": {}
    }

    dtypes_series = df.dtypes
    nulls_series = df.isnull().sum()

    for col_name in df.columns:
        desc = df[col_name].describe().to_dict()
        for key, value in desc.items():
            if pd.api.types.is_number(value):
                desc[key] = float(value)

        unique_count = df[col_name].nunique()
        null_percentage = (nulls_series[col_name] / metadata["Total_Rows"]) * 100 if metadata["Total_Rows"] > 0 else 0

        metadata["Column_Details"][col_name] = {
            "Data_Type": str(dtypes_series[col_name]),
            "Non_Null_Count": int(metadata["Total_Rows"] - nulls_series[col_name]),
            "Null_Count": int(nulls_series[col_name]),
            "Null_Percentage": round(float(null_percentage), 2),
            "Unique_Values_Count": int(unique_count),
            "Descriptive_Stats": desc,
        }

    return to_toon(metadata)

def save_toon(toon_output, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(toon_output)
        print(f"\nSUCCESS: Metadata saved to {output_path}")
    except Exception as e:
        print(f"\nERROR saving TOON file: {e}")


def process_csv_metadata(csv_path, output_folder=None):
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at '{csv_path}'")
        return

    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except Exception as e:
        print(f"Error reading CSV file '{csv_path}': {e}")
        return

    file_name = os.path.basename(csv_path)
    file_basename, extension = os.path.splitext(file_name)

    # Replaced np.nan with None to ensure clean nulls in TOON
    sample_rows = df.head(3).replace({np.nan: None}).to_dict('records')

    metadata = {
        "File_Name": file_name,
        "Total_Rows": int(df.shape[0]),
        "Total_Columns": int(df.shape[1]),
        "Sample_Rows_Head_3": sample_rows,  # This will trigger tabular formatting
        "Column_Details": {}
    }

    dtypes_series = df.dtypes
    nulls_series = df.isnull().sum()

    for col_name in df.columns:
        desc = df[col_name].describe().to_dict()
        for key, value in desc.items():
            if pd.api.types.is_number(value):
                desc[key] = float(value)

        unique_count = df[col_name].nunique()
        null_percentage = (nulls_series[col_name] / metadata["Total_Rows"]) * 100

        metadata["Column_Details"][col_name] = {
            "Data_Type": str(dtypes_series[col_name]),
            "Non_Null_Count": int(metadata["Total_Rows"] - nulls_series[col_name]),
            "Null_Count": int(nulls_series[col_name]),
            "Null_Percentage": round(float(null_percentage), 2),
            "Unique_Values_Count": int(unique_count),
            "Descriptive_Stats": desc,
        }

    output_filename = file_basename + "_metadata.toon"

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, output_filename)
    else:
        output_path = output_filename

    # Convert the metadata dict to TOON string
    toon_output = to_toon(metadata)
    save_toon(toon_output, output_path)


CSV_FILE = 'input.csv'
OUTPUT_DIR = "csv_metadata_output"

# Note: Ensure the file exists or comment this out
if os.path.exists(CSV_FILE):
    process_csv_metadata(CSV_FILE, output_folder=OUTPUT_DIR)