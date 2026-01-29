def verify_code(llm, code, rule_toon):
    prompt = f"""
RULE:
{rule_toon}

CODE:
{code}

TASK:
- Does the code actually implement the rule?
- If the rule requires checks or validation, does the code perform them?
- Is "no action required" an invalid response here?

Reply ONLY JSON:
{{"approved": true/false, "reason": "string"}}
"""
    return llm.ask_json(prompt)
