def generate_code(llm, rule_toon, metadata_toon):
    prompt = f"""
Generate Python code to implement the following human-written rule.

RULE (verbatim):
{rule_toon}

DATASET METADATA:
{metadata_toon}

CRITICAL RULES:
- Do NOT use import statements.
- The pandas library is available as 'pd' and numpy is available as 'np'.
- You MUST define a function called apply_rule(df).
- The function must return the modified DataFrame and a list of issues, like `return df, issues`.
- **Keep the code simple and direct. Do not write complex or overly-clever code.**
- **Define all helper variables (like lists or dictionaries) at the top level, outside the apply_rule function.** This is mandatory for clarity.
- When parsing dates, use pd.to_datetime(column, format='mixed', errors='coerce'). Do NOT use 'infer_datetime_format'.
- Do NOT invent reference data or make assumptions beyond the rule.
- Do NOT return "no action required" or just print statements.
"""
    return llm.call(prompt)
