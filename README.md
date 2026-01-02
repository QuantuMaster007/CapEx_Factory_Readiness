# CapEx / Factory Readiness

A **TPM/EPM-style portfolio repo** demonstrating decision-making using data across **CapEx + readiness + supply chain + facilities**.

## What questions this dashboard answers
- **What’s on the critical path?**
- **What’s blocking installation / power-on?**
- **Where are we burning expedite?**
- **What gate will slip and why?**

---

## What’s included (long sample data)
This repo ships with **synthetic/anonymized** datasets sized to feel realistic:

- `data/raw/capex_plan_vs_actuals.csv` — **3,600 rows** (24 months × tools × categories)
- `data/raw/lead_times_expedite.csv` — **4,200 rows** (line-level material + expedite drivers)
- `data/raw/facility_readiness_tasks.csv` — **900 rows** (multi-tool readiness tasks with dependencies)
- plus processed rollups in `data/processed/`

---

## Quick start (local)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Generates recruiter-proof outputs in docs/evidence/
python -m src.tooling.generate_evidence

# Dashboard
streamlit run app.py
```

## Key portfolio artifacts
- **Weekly exec update (template):** `docs/templates/WEEKLY_EXEC_UPDATE_TEMPLATE.md`
- **Weekly exec update (filled example):** `docs/samples/WEEKLY_EXEC_UPDATE_2026-01-02.md`
- **RAID log:** `docs/templates/RAID_LOG_TEMPLATE.md` (+ `docs/samples/RAID_LOG_SAMPLE.md`)
- **Decision log:** `docs/templates/DECISION_LOG_TEMPLATE.md` (+ `docs/samples/DECISION_LOG_SAMPLE.md`)
- **Metrics definitions:** `docs/metrics_definitions.md`
- **Data dictionary:** `docs/data_dictionary/`
- **System diagram:** `docs/diagrams/system_view.md`
- **Evidence outputs:** `docs/evidence/` (generated + CI artifact)

## Evidence outputs (proof this repo runs)
Generate evidence:
```bash
python -m src.tooling.generate_evidence
```

Outputs:
- `docs/evidence/readiness_score_output.md`
- `docs/evidence/critical_path_output.md`
- `docs/evidence/expedite_summary_output.md`
- `docs/evidence/capex_variance_snapshot.md`
- `docs/evidence/gate_slip_risk_output.md`

## Repo map
```text
data/
  raw/                      # long synthetic/anonymized datasets
  processed/                # derived rollups for trends
docs/
  templates/                # exec updates, RAID, decision logs
  samples/                  # filled examples (what recruiters love)
  evidence/                 # generated outputs for proof
  diagrams/                 # simple system diagram
  data_dictionary/          # column-level documentation
src/
  analytics/                # readiness, critical path, expedite summaries
  tooling/                  # scripts to generate evidence
  utils/                    # IO helpers
app.py                      # Streamlit dashboard
.github/                    # CI + issue templates
```

---

## Notes
- Data is **synthetic/anonymized** for portfolio use.
- Replace datasets with sanitized exports if needed.
