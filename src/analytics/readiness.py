from __future__ import annotations
import pandas as pd

STATUS_SCORE = {"Done": 1.0, "In Progress": 0.5, "Blocked": 0.0, "Not Started": 0.0}
RISK_WEIGHT = {"Low": 1.0, "Medium": 1.15, "High": 1.35}
GATE_WEIGHT = {"Install": 0.40, "PowerOn": 0.25, "Comm": 0.20, "SAT": 0.15}

def compute_readiness(tasks: pd.DataFrame) -> pd.DataFrame:
    df = tasks.copy()
    df["status_score"] = df["status"].map(STATUS_SCORE).fillna(0.0)
    df["risk_weight"] = df["risk_level"].map(RISK_WEIGHT).fillna(1.0)
    df["gate_weight"] = df["gate"].map(GATE_WEIGHT).fillna(0.2)
    df["weighted_score"] = df["status_score"] * df["gate_weight"] / df["risk_weight"]

    grp = df.groupby(["program","tool_id","site","area"], as_index=False).agg(
        readiness_score=("weighted_score","sum"),
        tasks_total=("task_id","count"),
        tasks_done=("status", lambda s: int((s=="Done").sum())),
        tasks_blocked=("status", lambda s: int((s=="Blocked").sum())),
        high_risk=("risk_level", lambda s: int((s=="High").sum())),
    )

    max_w = df.groupby(["program","tool_id","site","area"], as_index=False)["gate_weight"].sum().rename(columns={"gate_weight":"max_weight"})
    grp = grp.merge(max_w, on=["program","tool_id","site","area"], how="left")
    grp["readiness_pct"] = 100.0 * (grp["readiness_score"] / grp["max_weight"].clip(lower=1e-9))

    def rag(pct: float, blocked: int, high_risk: int) -> str:
        if blocked > 0 and pct < 88:
            return "R"
        if pct >= 88:
            return "G"
        if pct >= 75:
            return "A"
        return "R"

    grp["rag"] = grp.apply(lambda r: rag(float(r.readiness_pct), int(r.tasks_blocked), int(r.high_risk)), axis=1)
    return grp.sort_values(["rag","readiness_pct"], ascending=[True, False])
