import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# Helper for random dates
def rand_dates(start, n):
    return [(start + timedelta(days=x)).strftime('%Y-%m-%d') for x in np.random.randint(0, 100, n)]

# 1. CapEx Plan vs Actuals (Rich)
programs = ["Project Apollo", "Project Zeus", "Project Hera"]
categories = ["Construction", "Tooling", "Facilities", "HVAC", "Electrical"]
data_size = 50

capex = pd.DataFrame({
    "program": np.random.choice(programs, data_size),
    "tool_id": [f"TL-{i:03d}" for i in range(data_size)],
    "capex_category": np.random.choice(categories, data_size),
    "planned_spend_usd": np.random.uniform(500000, 2000000, data_size),
})
capex["actual_spend_usd"] = capex["planned_spend_usd"] * np.random.uniform(0.9, 1.3, data_size)
capex["forecast_spend_usd"] = capex["actual_spend_usd"] * 1.05
capex.to_csv("data/raw/capex_plan_vs_actuals.csv", index=False)

# 2. Facility Readiness Tasks
tasks = pd.DataFrame({
    "program": np.random.choice(programs, 100),
    "site": np.random.choice(["Arizona", "Texas", "Berlin", "Taiwan"], 100),
    "tool_id": [f"TL-{np.random.randint(0, 50):03d}" for _ in range(100)],
    "task_id": range(100),
    "task_name": np.random.choice(["Foundation", "Power Hookup", "LSS Connection", "Gas Line", "SAT"], 100),
    "gate": np.random.choice(["Install", "PowerOn", "Comm", "SAT"], 100),
    "owner": np.random.choice(["Sarah", "Mike", "Chen", "Raj"], 100),
    "planned_finish": rand_dates(datetime(2026, 1, 1), 100),
    "status": np.random.choice(["Done", "In Progress", "Blocked", "At Risk"], 100, p=[0.4, 0.3, 0.2, 0.1]),
    "risk_level": np.random.choice(["Low", "Medium", "High"], 100)
})
tasks.to_csv("data/raw/facility_readiness_tasks.csv", index=False)

# 3. Lead Times & Expedite
lead = pd.DataFrame({
    "program": np.random.choice(programs, 30),
    "tool_id": [f"TL-{i:03d}" for i in range(30)],
    "vendor": np.random.choice(["ASML", "AppliedMat", "LamResearch", "TokyoElectron"], 30),
    "expedite_spend_usd": np.random.uniform(10000, 150000, 30)
})
lead.to_csv("data/raw/lead_times_expedite.csv", index=False)

print("🚀 Rich Data Generated!")
