# facility_readiness_tasks.csv

**Row grain:** tool_id + task_id (task)

Key columns:
- `gate` — Install / PowerOn / Comm / SAT
- `depends_on` — comma-separated predecessor task_name values
- `status` — Done / In Progress / Blocked
- `risk_level` — Low / Medium / High
