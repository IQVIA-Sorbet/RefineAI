from sandbox import execute
from diff_engine import compute_diff
from llms.generator import generate_code
from llms.verifier import verify_code
from llms.auditor import audit
from llms.interpreter import interpret_rule
from ast_guard import sanitize_code, validate_code
from csv_read_toon import generate_metadata_toon_from_df

import os
from datetime import datetime


def run_pipeline(state, rules, metadata_toon, llm):
    current_metadata_toon = metadata_toon

    while state.rule_index < len(rules):
        rule = rules[state.rule_index]

        intent = interpret_rule(llm, rule)

        if not intent["requires_execution"]:
            state.snapshot("Informational rule – skipped execution")
            state.rule_index += 1
            continue

        MAX_ATTEMPTS = 3
        last_error = None
        code_approved = False
        df_after, issues = (None, [])

        for attempt in range(MAX_ATTEMPTS):
            if not code_approved:
                raw_code = generate_code(
                    llm,
                    rule + (f"\n\nNOTE: Previous attempt failed due to: {last_error}" if last_error else ""),
                    current_metadata_toon
                )
                code = sanitize_code(raw_code)

            try:
                validate_code(code)
                print("INFO: Code syntax is valid.")

                if not code_approved:
                    verdict = verify_code(llm, code, rule)
                    if not verdict["approved"]:
                        raise ValueError(f"Code rejected by verifier: {verdict.get('reason')}")
                    code_approved = True
                    print("INFO: Code verification approved.")

                df_before = state.df.copy()
                df_after, issues = execute(code, df_before)

                print("INFO: Code executed successfully in validation.")
                break

            except (ValueError, NameError, TypeError, KeyError, AttributeError, SyntaxError) as e:
                print(f"WARNING: Validation failed on attempt {attempt + 1}: {e}")
                last_error = str(e)
                code_approved = False
                if attempt == MAX_ATTEMPTS - 1:
                    print("ERROR: Code failed validation after multiple attempts.")
                    raise

        summary = "Validation rule executed with no data changes."
        diff_result = None
        audit_feedback = None

        df_before_step = state.df
        diff = compute_diff(df_before_step, df_after)

        if diff["row_delta"] != 0 or diff.get("changed_cells", 0) != 0:
            print("INFO: Data changed, proceeding to audit.")
            diff_result = diff

            audit_feedback = audit(llm, diff, rule)

            summary = audit_feedback["summary"]
            verdict_text = "APPROVED" if audit_feedback.get("approve") else "REJECTED"
            print(f"INFO: Audit complete. Verdict: {verdict_text}")
        else:
            print("INFO: No data changed.")

        # Commit the changes to the main DataFrame
        state.df = df_after

        # Save CSV after each rule
        os.makedirs("step_csv", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = f"step_csv/output_after_rule_{state.rule_index+1}_{ts}.csv"
        state.df.to_csv(csv_path, index=False)

        # Snapshot (writes per-rule log)
        state.snapshot(note=summary, diff=diff_result, audit=audit_feedback)

        # Regenerate metadata for the next loop
        print("INFO: Regenerating metadata from the updated DataFrame.")
        current_metadata_toon = generate_metadata_toon_from_df(state.df)

        # Move to the next rule
        state.rule_index += 1

    # 🔹 FINAL LOG after all rules are completed
    state.snapshot(note="Pipeline completed. All rules processed.")