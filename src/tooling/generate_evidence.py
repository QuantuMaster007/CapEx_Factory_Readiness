from __future__ import annotations
import pandas as pd
from pathlib import Path

from src.utils.io import read_csv, write_md
from src.analytics.readiness import compute_readiness
from src.analytics.critical_path import compute_critical_path
from src.analytics.expedite import expedite_summary

def main() -> None:
    capex = read_csv("data/raw/capex_plan_vs_actuals.csv")
    lead = read_csv("data/raw/lead_times_expedite.csv")
    tasks = read_csv("data/raw/facility_readiness_tasks.csv")

    # Evidence 1: readiness (top 15 worst)
    readiness = compute_readiness(tasks)
    worst = readiness.sort_values(["rag","readiness_pct"], ascending=[True, True]).head(15)
    write_md(Path("docs/evidence/readiness_score_output.md"),
             "# Readiness Score Output (15 Most At-Risk)\n\n" + worst.to_markdown(index=False))

    # Evidence 2: critical path example (first program/tool)
    prog = tasks["program"].iloc[0]
    tool = tasks[tasks["program"]==prog]["tool_id"].iloc[0]
    cp = compute_critical_path(tasks, program=prog, tool_id=tool)
    write_md(Path("docs/evidence/critical_path_output.md"),
             f"# Critical Path Output\n\nProgram: **{prog}**\n\nTool: **{tool}**\n\n" + cp.to_markdown(index=False))

    # Evidence 3: expedite top drivers
    es = expedite_summary(lead).head(20)
    write_md(Path("docs/evidence/expedite_summary_output.md"),
             "# Expedite Summary Output (Top 20)\n\n" + es.to_markdown(index=False))

    # Evidence 4: CapEx variance top lines
    capex["variance_usd"] = capex["actual_spend_usd"] - capex["planned_spend_usd"]
    top = (capex.groupby(["program","capex_category"], as_index=False)
                .agg(planned=("planned_spend_usd","sum"),
                     actual=("actual_spend_usd","sum"),
                     variance=("variance_usd","sum"))
                .sort_values("variance", ascending=False)
                .head(25))
    write_md(Path("docs/evidence/capex_variance_snapshot.md"),
             "# CapEx Variance Snapshot (Top 25)\n\n" + top.to_markdown(index=False))

    # Evidence 5: gate slip risk
    t = tasks.copy()
    t["planned_finish"] = pd.to_datetime(t["planned_finish"])
    incom = t[t["status"] != "Done"]
    slip = (incom.groupby(["program","gate"], as_index=False)
                .agg(next_gate_date=("planned_finish","max"),
                     open_tasks=("task_id","count"),
                     blocked=("status", lambda s: int((s=="Blocked").sum())),
                     high_risk=("risk_level", lambda s: int((s=="High").sum()))))
    slip = slip.sort_values(["next_gate_date","blocked","high_risk"], ascending=[True, False, False]).head(25)
    write_md(Path("docs/evidence/gate_slip_risk_output.md"),
             "# Gate Slip Risk Output (Top 25)\n\n" + slip.to_markdown(index=False))

    print("Evidence generated in docs/evidence/")

if __name__ == "__main__":
    main()
