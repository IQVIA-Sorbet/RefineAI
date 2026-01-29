import pandas as pd
import os
import json


def to_toon(data, indent=0):
    """
    Converts a Python object to a TOON-formatted string.
    """
    spaces = " " * indent
    output = []

    if isinstance(data, dict):
        for key, value in data.items():
            # Check if value is a list of dicts (Uniform Table)
            if isinstance(value, list) and value and isinstance(value[0], dict):
                keys = list(value[0].keys())
                # check if all items have the same keys
                if all(isinstance(x, dict) and list(x.keys()) == keys for x in value):
                    headers = ",".join(keys)
                    output.append(f"{spaces}{key}[{len(value)}]{{{headers}}}:")
                    for item in value:
                        row = []
                        for k in keys:
                            val = item.get(k)
                            if val is None:
                                row.append("null")
                            elif isinstance(val, (int, float, bool)):
                                row.append(str(val).lower())
                            else:
                                s_val = str(val)
                                # Quote if comma or special chars exist
                                if "," in s_val or "\n" in s_val or ":" in s_val:
                                    row.append(f'"{s_val}"')
                                else:
                                    row.append(s_val)
                        output.append(f"{spaces}  " + ",".join(row))
                    continue

            # Recursive handling for other types
            if isinstance(value, dict):
                output.append(f"{spaces}{key}:")
                output.append(to_toon(value, indent + 2))
            elif isinstance(value, list):
                # Simple lists or non-uniform lists
                if not value:
                    output.append(f"{spaces}{key}[0]:")
                elif isinstance(value[0], (int, float, bool, str)):
                    # Primitive list (inline)
                    formatted_list = ", ".join([str(x) for x in value])
                    output.append(f"{spaces}{key}[{len(value)}]: {formatted_list}")
                else:
                    # Complex list
                    output.append(f"{spaces}{key}[{len(value)}]:")
                    for item in value:
                        output.append(to_toon(item, indent + 2))
            else:
                # Primitives
                val_str = str(value)
                if isinstance(value, bool): val_str = val_str.lower()
                if value is None: val_str = "null"
                # Simple quoting check
                if any(c in val_str for c in [",", "\n", ":"]):
                    val_str = f'"{val_str}"'
                output.append(f"{spaces}{key}: {val_str}")

        return "\n".join(output)

    elif isinstance(data, list):
        # Fallback for top-level lists
        return "\n".join([to_toon(x, indent) for x in data])

    else:
        return str(data)


def read_excel(path, output_folder):
    if not os.path.exists(path):
        print(f"Error finding file: {path}")
        return
    try:
        all_sheets_data = pd.read_excel(path, sheet_name=None)
        print(f"Successfully read excel file: '{path}' which had {len(all_sheets_data)} sheets")
        convert_toon(all_sheets_data, path, output_folder)
    except Exception as e:
        print(f"An error occured while reading the file: {e}")


def save_toon(toon_output, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(toon_output)


def convert_toon(all_sheets_data, path, output_folder=None):
    if not all_sheets_data:
        print("Error in data")
        return

    file_name = os.path.basename(path)
    file_basename, extension = os.path.splitext(file_name)
    output_filename = file_basename + ".toon"

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        output_filepath = os.path.join(output_folder, output_filename)
    else:
        output_filepath = output_filename

    # Constructing the data structure
    data_wrapper = {file_name: {}}

    for sheet_name, df in all_sheets_data.items():
        # Converting to 'records' (list of dicts) matches TOON's tabular strength better
        # than 'list' (dict of lists), but TOON handles both.
        # If you prefer column-wise: keep 'list'. If you prefer table rows: use 'records'.
        # The implementation below handles 'list' format (dict of lists) as standard keys.
        sheet_data_dict = df.to_dict('list')
        data_wrapper[file_name][sheet_name] = sheet_data_dict

    # Convert to TOON string
    toon_string = to_toon(data_wrapper)
    save_toon(toon_string, output_filepath)
    print(f"Saved TOON file to: {output_filepath}")


file = ".\cleaning_note_sample.xlsx"
# Note: Ensure the file exists or comment this out to avoid runtime errors
if os.path.exists(file):
    read_excel(file, output_folder="rules")