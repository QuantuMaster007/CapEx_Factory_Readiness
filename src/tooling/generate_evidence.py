from __future__ import annotations
import pandas as pd
from pathlib import Path
import sys

from src.utils.io import read_csv, write_md
from src.analytics.readiness import compute_readiness
from src.analytics.critical_path import compute_critical_path
from src.analytics.expedite import expedite_summary

def safe_to_markdown(df: pd.DataFrame) -> str:
    """Helper to prevent crashes if tabulate is missing."""
    try:
        return df.to_markdown(index=False)
    except ImportError:
        # Fallback to a plain text representation if 'tabulate' isn't installed
        return "```\n" + df.to_string(index=False) + "\n```"

def main() -> None:
    # Ensure the output directory exists
    output_dir = Path("docs/evidence")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load Data
    capex = read_csv("data/raw/capex_plan_vs_actuals.csv")
    lead = read_csv("data/raw/lead_times_expedite.csv")
    tasks = read_csv("data/raw/facility_readiness_tasks.csv")

    # 1. Readiness Score Output (Top 15 Most At-Risk)
    readiness = compute_readiness(tasks)
    # Sort by RAG (Red first) then by lowest percentage
    worst = readiness.sort_values(["rag", "readiness_pct"], ascending=[True, True]).head(15)
    write_md(output_dir / "readiness_score_output.md",
             "# Readiness Score Output (15 Most At-Risk)\n\n" + safe_to_markdown(worst))

    # 2. Critical Path Example (First program/tool)
    prog = tasks["program"].iloc[0]
    tool = tasks[tasks["program"] == prog]["tool_id"].iloc[0]
    cp = compute_critical_path(tasks, program=prog, tool_id=tool)
    write_md(output_dir / "critical_path_output.md",
             f"# Critical Path Output\n\nProgram: **{prog}**\n\nTool: **{tool}**\n\n" + safe_to_markdown(cp))

    # 3. Expedite Top Drivers
    es = expedite_summary(lead).head(20)
    write_md(output_dir / "expedite_summary_output.md",
             "# Expedite Summary Output (Top 20)\n\n" + safe_to_markdown(es))

    # 4. CapEx Variance Top Lines
    capex["variance_usd"] = capex["actual_spend_usd"] - capex["planned_spend_usd"]
    top = (capex.groupby(["program", "capex_category"], as_index=False)
                .agg(planned=("planned_spend_usd", "sum"),
                     actual=("actual_spend_usd", "sum"),
                     variance=("variance_usd", "sum"))
                .sort_values("variance", ascending=False)
                .head(25))
    write_md(output_dir / "capex_variance_snapshot.md",
             "# CapEx Variance Snapshot (Top 25)\n\n" + safe_to_markdown(top))

    # 5. Gate Slip Risk
    t = tasks.copy()
    t["planned_finish"] = pd.to_datetime(t["planned_finish"])
    incom = t[t["status"] != "Done"]
    slip = (incom.groupby(["program", "gate"], as_index=False)
                .agg(next_gate_date=("planned_finish", "max"),
                     open_tasks=("task_id", "count"),
                     blocked=("status", lambda s: int((s == "Blocked").sum())),
                     high_risk=("risk_level", lambda s: int((s == "High").sum()))))
    
    slip = slip.sort_values(["next_gate_date", "blocked", "high_risk"], ascending=[True, False, False]).head(25)
    write_md(output_dir / "gate_slip_risk_output.md",
             "# Gate Slip Risk Output (Top 25)\n\n" + safe_to_markdown(slip))

    print(f"✅ Success: Evidence generated in {output_dir}/")

if __name__ == "__main__":
    main()
