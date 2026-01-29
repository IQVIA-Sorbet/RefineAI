def compute_diff(df_before, df_after):
    # Row / column deltas
    rows_before = len(df_before)
    rows_after = len(df_after)

    cols_before = set(df_before.columns)
    cols_after = set(df_after.columns)
    common_cols = sorted(cols_before & cols_after)

    # Align on index intersection
    common_index = df_before.index.intersection(df_after.index)

    if common_cols and not common_index.empty:
        before_aligned = df_before.loc[common_index, common_cols]
        after_aligned = df_after.loc[common_index, common_cols]

        changed_cells = (before_aligned != after_aligned).sum().sum()
    else:
        changed_cells = 0

    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "row_delta": rows_after - rows_before,
        "columns_before": len(cols_before),
        "columns_after": len(cols_after),
        "changed_cells": int(changed_cells),
        "nulls_before": df_before.isnull().sum().to_dict(),
        "nulls_after": df_after.isnull().sum().to_dict()
    }
