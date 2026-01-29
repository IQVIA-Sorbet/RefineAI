import pandas as pd
import os
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class PipelineState:
    df: pd.DataFrame
    rule_index: int = 0
    history: list = field(default_factory=list)

    def snapshot(self, note: str, diff: dict = None, audit: dict = None):
        entry = {
            "rule_index": self.rule_index,
            "rows": len(self.df),
            "note": note,
        }

        if diff:
            entry["diff"] = {
                "row_delta": diff.get("row_delta", 0),
                "changed_cells": diff.get("changed_cells", 0)
            }

        if audit:
            entry["audit"] = audit

        self.history.append(entry)

        #  NEW: Save this snapshot as a log file
        os.makedirs("logs", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = f"logs/rule_{self.rule_index+1}_{ts}.txt"

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Rule Index: {self.rule_index+1}\n")
            f.write(f"Rows: {len(self.df)}\n")
            f.write(f"Note: {note}\n\n")

            if diff:
                f.write("Diff:\n")
                for k, v in entry["diff"].items():
                    f.write(f"  {k}: {v}\n")

            if audit:
                f.write("\nAudit:\n")
                for k, v in audit.items():
                    f.write(f"  {k}: {v}\n")
