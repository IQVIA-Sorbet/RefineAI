import json
import pandas as pd
from state import PipelineState
from orchestrator import run_pipeline
from llms.base import LLMClient
from llms.gemini_client import gemini_call
from llms.rule_splitter import split_rules
from csv_read_toon import generate_metadata_toon_from_df


def load_rules(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # SUPER IMPORTANT:
    # Split rules at top-level markers (adjust if needed)
    rules = [r.strip() for r in content.split("\n\n") if r.strip()]
    return rules


def print_audit_summary(history: list, rules: list):
    """
    Prints a human-readable report of the entire pipeline run,
    highlighting the auditor's feedback for each step.
    """
    print("\n\n" + "=" * 80)
    print("--- PIPELINE AUDIT SUMMARY REPORT ---")
    print("=" * 80)

    for entry in history:
        # Check if this is a rule entry or a final summary
        if "rule_index" not in entry:
            continue
            
        rule_index = entry["rule_index"]
        rule_text = rules[rule_index] if rule_index < len(rules) else "N/A"

        print(f"\n## Rule #{rule_index + 1}: {rule_text[:100]}...")
        print(f"   - Note: {entry['note']}")

        if "audit" in entry and entry["audit"] is not None:
            audit = entry["audit"]
            diff = entry.get("diff", {})

            verdict = "APPROVED" if audit.get("approve", False) else "REJECTED"

            # Use a clear visual indicator for the verdict
            verdict_marker = f"[{verdict}]" if verdict == "APPROVED" else f"[!!! {verdict} !!!]"

            print(f"   - Changes: {diff.get('row_delta', 0)} rows, {diff.get('changed_cells', 0)} cells")
            print(f"   - Auditor Verdict: {verdict_marker}")
        else:
            print("   - No data changes were made in this step.")

    print("\n" + "=" * 80)
    print("Review the report above to decide if the final output is acceptable.")
    print("=" * 80)


def save_results_json(history: list, rules: list, output_path: str):
    """
    Saves the pipeline history and rules to a JSON file for the web UI.
    """
    results = {
        "rules": rules,
        "history": history,
        "summary": {
            "total_rules": len(rules),
            "processed_at": pd.Timestamp.now().isoformat()
        }
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)


def main():
    df = pd.read_csv("data/input.csv")

    # Generate metadata directly from the dataframe
    metadata = generate_metadata_toon_from_df(df)

    with open("data/rules.toon", "r", encoding="utf-8") as f:
        rules_toon = f.read()

    llm = LLMClient(gemini_call)

    rules = split_rules(llm, rules_toon)

    state = PipelineState(df=df)

    run_pipeline(
        state=state,
        rules=rules,
        metadata_toon=metadata,
        llm=llm
    )

    print_audit_summary(state.history, rules)

    state.df.to_csv("data/cleaned_output.csv", index=False)
    
    # Save results to JSON for the specific integration with the web app
    save_results_json(state.history, rules, "data/results.json")
    
    print("Pipeline complete. Output saved.")


if __name__ == "__main__":
    main()
