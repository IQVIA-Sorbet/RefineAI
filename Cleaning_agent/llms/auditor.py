def audit(llm, diff, rule_toon):
    prompt = f"""
RULE:
{rule_toon}

DIFF:
{diff}

Reply ONLY JSON:
{{"approve": true/false, "summary": "string"}}
"""
    return llm.ask_json(prompt)
