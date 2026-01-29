def interpret_rule(llm, rule_toon):
    prompt = f"""
You are analyzing a human-written data rule.

RULE (verbatim):
{rule_toon}

Question:
Does this rule require executable logic
to inspect, validate, log, or transform data?

IMPORTANT:
- Even if no data is modified, checking conditions counts as execution
- Logging or flagging issues counts as execution
- Reply false ONLY if the rule is purely informational

Reply STRICT JSON:
{{ "requires_execution": true/false, "reason": "short explanation" }}
"""
    result = llm.ask_json(prompt)

    if "requires_execution" not in result:
        raise ValueError("Interpreter did not return requires_execution")

    return result

