import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Ensure directories exist
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

def rand_dates(start_base, n, min_days=0, max_days=90):
    return [(start_base + timedelta(days=int(x))).strftime('%Y-%m-%d') for x in np.random.randint(min_days, max_days, n)]

# --- Configuration for High Density Data ---
programs = ["Project Apollo", "Project Zeus", "Project Hera", "Project Artemis", "Project Hermes"]
sites = ["Arizona (PHX-1)", "Texas (AUS-2)", "Berlin (BER-1)", "Taiwan (TSM-3)", "Oregon (PDX-5)"]
gates = ["Install", "PowerOn", "Comm", "SAT", "Handover"]
areas = ["Cleanroom A", "Cleanroom B", "Subfab", "Loading Dock", "Support Gallery", "Chemical Yard"]
vendors = ["ASML", "AppliedMat", "LamResearch", "TokyoElectron", "KLA", "Screen"]
categories = ["Construction", "Tooling", "Facilities", "HVAC", "Electrical", "Gas Systems"]
statuses = ["Done", "In Progress", "Blocked", "At Risk", "Not Started"]
risks = ["Low", "Medium", "High", "Critical"]

# 1. GENERATE CAPEX DATA (100 Rows)
# Satisfies: forecast_spend_usd, capex_category
df_capex = pd.DataFrame({
    "program": np.random.choice(programs, 100),
    "tool_id": [f"TL-{i:04d}" for i in range(100)],
    "capex_category": np.random.choice(categories, 100),
    "planned_spend_usd": np.random.uniform(1000000, 5000000, 100).round(2),
})
df_capex["actual_spend_usd"] = (df_capex["planned_spend_usd"] * np.random.uniform(0.85, 1.4, 100)).round(2)
df_capex["forecast_spend_usd"] = (df_capex["actual_spend_usd"] * 1.08).round(2)
df_capex.to_csv("data/raw/capex_plan_vs_actuals.csv", index=False)

# 2. GENERATE FACILITY READINESS DATA (500 Rows)
# Satisfies: area, gate, risk_level, task_name, planned_start, planned_finish
start_base = datetime(2026, 1, 1)
df_tasks = pd.DataFrame({
    "program": np.random.choice(programs, 500),
    "site": np.random.choice(sites, 500),
    "area": np.random.choice(areas, 500),
    "tool_id": [f"TL-{np.random.randint(0, 100):04d}" for _ in range(500)],
    "task_id": [f"T-{i:04d}" for i in range(500)],
    "task_name": np.random.choice(["Foundation", "Power Hookup", "LSS Connection", "Gas Line", "SAT", "Safety Insp", "Seismic Bracing"], 500),
    "gate": np.random.choice(gates, 500),
    "status": np.random.choice(statuses, 500, p=[0.3, 0.3, 0.15, 0.15, 0.1]),
    "risk_level": np.random.choice(risks, 500),
    "planned_start": rand_dates(start_base, 500, 0, 60),
})
# Ensure finish is always after start
df_tasks["planned_finish"] = [ (datetime.strptime(sd, '%Y-%m-%d') + timedelta(days=np.random.randint(5, 30))).strftime('%Y-%m-%d') for sd in df_tasks["planned_start"]]
df_tasks.to_csv("data/raw/facility_readiness_tasks.csv", index=False)

# 3. GENERATE LEAD TIMES / EXPEDITE DATA (75 Rows)
df_lead = pd.DataFrame({
    "program": np.random.choice(programs, 75),
    "tool_id": [f"TL-{np.random.randint(0, 100):04d}" for _ in range(75)],
    "vendor": np.random.choice(vendors, 75),
    "expedite_spend_usd": np.random.uniform(20000, 250000, 75).round(2),
    "days_saved": np.random.randint(7, 45, 75)
})
df_lead.to_csv("data/raw/lead_times_expedite.csv", index=False)

print("💎 HIGH-DENSITY DATA GENERATED: 100 CapEx items, 500 Tasks, 75 Expedite records.")
