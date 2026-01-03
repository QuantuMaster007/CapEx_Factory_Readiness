import pandas as pd
import os

# Create folders if they don't exist
os.makedirs("data/raw", exist_ok=True)

# 1. Create CapEx Data
capex_data = {
    "program": ["Alpha", "Alpha", "Beta"],
    "tool_id": ["T01", "T02", "T03"],
    "capex_category": ["Construction", "Tooling", "Facilities"],
    "planned_spend_usd": [1000000, 500000, 750000],
    "actual_spend_usd": [1100000, 450000, 800000],
    "forecast_spend_usd": [1100000, 480000, 820000]
}
pd.DataFrame(capex_data).to_csv("data/raw/capex_plan_vs_actuals.csv", index=False)

# 2. Create Readiness Data
tasks_data = {
    "program": ["Alpha", "Alpha", "Beta"],
    "site": ["USA", "USA", "Germany"],
    "tool_id": ["T01", "T01", "T03"],
    "task_id": [1, 2, 3],
    "task_name": ["Foundation", "Power Hookup", "Safety Check"],
    "gate": ["Install", "PowerOn", "SAT"],
    "owner": ["Alice", "Bob", "Charlie"],
    "planned_finish": ["2026-01-01", "2026-02-01", "2026-03-01"],
    "status": ["Done", "Blocked", "In Progress"],
    "risk_level": ["Low", "High", "Medium"]
}
pd.DataFrame(tasks_data).to_csv("data/raw/facility_readiness_tasks.csv", index=False)

# 3. Create Lead Time Data
lead_data = {
    "program": ["Alpha", "Beta"],
    "tool_id": ["T01", "T03"],
    "vendor": ["VendorA", "VendorB"],
    "expedite_spend_usd": [5000, 12000]
}
pd.DataFrame(lead_data).to_csv("data/raw/lead_times_expedite.csv", index=False)

print("✅ Synthetic data created in data/raw/")
