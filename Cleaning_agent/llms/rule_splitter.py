def split_rules(llm, rules_toon):
    prompt = f"""
You are given a TOON document containing multiple human-written
data cleaning and validation rules.

TASK:
Split the document into individual executable rule blocks.

Rules:
- Preserve original wording
- Do NOT rewrite or summarize
- Each block should represent ONE logical instruction
- Notes or comments that belong to a rule should stay with it

Output STRICT JSON:
{{ "rules": ["rule block 1", "rule block 2", "..."] }}

DOCUMENT:
{rules_toon}
"""
    return llm.ask_json(prompt)["rules"]
