import datetime
import pandas as pd
import numpy as np


def execute(code, df):
    env = {
        'pd': pd,
        'np': np,
        'datetime': datetime
    }
    exec(code, env)

    fn = env.get("apply_rule")
    if not callable(fn):
        raise ValueError("apply_rule not defined")

    result = fn(df)

    if isinstance(result, tuple):
        df_out, issues = result
        if issues is None:
            issues = []
        return df_out, issues

    return result, []
