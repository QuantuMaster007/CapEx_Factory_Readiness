

```markdown
# CapEx Factory Readiness Command Center — Reducing Tool Install Delays Through Predictive Readiness Tracking

[![capex-readiness-ci](https://github.com/QuantuMaster007/CapEx_Factory_Readiness/actions/workflows/capex_readiness_ci.yml/badge.svg?branch=main)](https://github.com/QuantuMaster007/CapEx_Factory_Readiness/actions/workflows/capex_readiness_ci.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-success)](https://quantumaster007.github.io/CapEx_Factory_Readiness/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-brightgreen?logo=streamlit&logoColor=white)](https://capexfactoryreadiness-3t3ngaxnz2fvjf8jqsxkvg.streamlit.app/)

> **Built from 7+ years managing $500M+ CapEx portfolios** — A command center approach to de-risk tool installations across NPI programs. Translates fragmented operational data into executive decision-making tools where **execution discipline + financial governance + cross-functional coordination** intersect.

> **All data is synthetic/anonymized**.

---

## 🎯 For Interviewers & Hiring Managers

| What to Review | Why It Matters | Link |
|:---|:---|:---|
| **Live Dashboard** | See how I visualize complex program data for leadership decision-making | [Streamlit App](https://capexfactoryreadiness-3t3ngaxnz2fvjf8jqsxkvg.streamlit.app/) |
| **CI/CD Pipeline** | Evidence of production-grade automation mindset | [GitHub Actions](.github/workflows/capex_readiness_ci.yml) |
| **Evidence Pack** | Sample executive-ready outputs I generate for leadership reviews | [`docs/evidence/`](docs/evidence/) |
| **Program Artifacts** | RAID logs, decision logs, exec updates — showing operational rigor | [`docs/templates/`](docs/templates/) |

---

## Dashboard Preview

<a href="docs/images/dashboard.pdf">
  <img src="docs/images/dashboard.png" alt="Dashboard preview" style="border:1px solid #d0d7de; border-radius:10px; padding:6px; background:white;" />
</a>

(High-res backup: [`docs/images/dashboard.pdf`](docs/images/dashboard.pdf))

---

## 💼 What This Demonstrates (Using Synthetic Data)

| Business Challenge | How I Solved It | Result |
|:---|:---|:---|
| **CapEx variance blind spots** | Automated variance tracking by program/category/month with root-cause tagging | **+$7.5M variance** surfaced early across $561.8M plan |
| **Readiness status ambiguity** | RAG-scored readiness gates with dependency-aware critical path | **57.5% → 87.0%** readiness clarity across 50 tools |
| **Expedite cost leakage** | Vendor-level burn analysis with driver categorization | **$7.6M expedite** tracked across 1,434 lines |
| **Leadership reporting overhead** | CI-generated evidence packs on every commit | **Zero-touch** exec-ready outputs |

> **Dataset scale:** 5 programs, 50 tools, 6 categories, 6 vendors, 24 months — all synthetic CSVs in `data/raw/`

---

## 🏗️ Architecture & Design Decisions

```
┌─────────────────────────────────────────────────────────────┐
│  Leadership Layer (GitHub Pages / Markdown Evidence Packs)  │
├─────────────────────────────────────────────────────────────┤
│  Analytics Engine (Pandas + Plotly + Custom Logic)          │
│  ├── Readiness scoring with dependency-aware critical path  │
│  ├── CapEx variance analysis with forecast drift detection  │
│  └── Expedite burn-down by vendor & root cause              │
├─────────────────────────────────────────────────────────────┤
│  Data Layer (Synthetic CSVs → Extensible to ERP/PLM APIs)   │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Choices:**
- **Synthetic data only:** Demonstrates capability without exposing proprietary information
- **Modular analytics:** Each module (`readiness.py`, `critical_path.py`, `expedite.py`) reusable across programs
- **CI-generated outputs:** Mirrors production automation of leadership reporting

---

## ✅ TPM/OPM Competencies Demonstrated

| Competency | Evidence in This Repo |
|:---|:---|
| **Cross-functional orchestration** | Integration of facilities, supply chain, and finance data models |
| **Executive communication** | Automated evidence packs + RAID/decision log templates |
| **Financial acumen** | CapEx variance analysis, forecast drift, expedite ROI tracking |
| **Risk management** | Critical path analysis, gate slip risk scoring, RAG statusing |
| **Process automation** | CI/CD pipeline for zero-touch reporting |
| **Data-driven decision making** | Plotly dashboards with drill-down capability |
| **NPI/Operational excellence** | Tool readiness gating, install → power-on → SAT tracking |

---

## What Questions the Dashboard Answers

- What's on the **critical path** right now (per program/tool)?
- What's **blocking** install → power-on → commissioning → SAT?
- Where are we burning **expedite**, and which vendors drive it?
- Which gates are most likely to **slip**, and why?
- Where is CapEx trending vs plan/forecast (what's driving variance)?

---

## What's Included

### 1) Streamlit Dashboard
- Entry point: `app.py`
- Reads from: `data/raw/` (synthetic CSVs)

### 2) Analytics Modules (Reusable Program Logic)
- `src/analytics/readiness.py` — readiness rollups + RAG
- `src/analytics/critical_path.py` — dependency-aware critical path per tool/program
- `src/analytics/expedite.py` — vendor burn summaries

### 3) Evidence Pack (Auto-Generated CI Artifact)
Generated by: `python -m src.tooling.generate_evidence`

Outputs to `docs/evidence/`:
- `readiness_score_output.md`
- `critical_path_output.md`
- `expedite_summary_output.md`
- `capex_variance_snapshot.md`
- `gate_slip_risk_output.md`

---

## How to Run Locally

**Prerequisites:** Python 3.11+

```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt

# Run dashboard
streamlit run app.py

# Generate evidence pack
python -m src.tooling.generate_evidence
```

---

## CI / Automation

**Workflow:** `.github/workflows/capex_readiness_ci.yml`

- Installs dependencies
- Runs `python -m src.tooling.generate_evidence`
- Uploads `docs/evidence/**` as CI artifact

---

## 🔒 Adapting to Production (Data Governance)

This repository uses **synthetic/anonymized data only**. In production environments, I implement:

- **Data classification:** CapEx data tagged by sensitivity level
- **Anonymization pipelines:** Automated PII/vendor identifier scrubbing
- **API integration:** Direct connections to ERP (SAP/Oracle) and PLM systems
- **Access controls:** Role-based permissions for program/finance/executive views

> **Never commit proprietary data.** This portfolio demonstrates the *logic* — the data layer is swappable.

---

## 🚀 Roadmap (Production Hardening)

| Priority | Enhancement | Business Value |
|:---|:---|:---|
| P0 | Scenario planning module (Forecast/Commit/Stretch) | Enable "what-if" analysis for CapEx reallocation |
| P1 | Automated gate go/no-go criteria | Reduce program review prep from days to hours |
| P2 | KPI suite (OTD, lead time P95, expedite rate) | Standardize vendor performance scorecards |
| P3 | Schema validation + data quality checks | Prevent garbage-in-garbage-out in automated pipelines |

---

## 🛠️ Tech Stack

**Data & Analytics:** Python · Pandas · NumPy · Plotly  
**App & Visualization:** Streamlit · HTML/CSS  
**Automation & DevOps:** GitHub Actions · Bash  
**Data Engineering:** SQL (PostgreSQL-compatible) · Docker-ready  

---

## Program Management Artifacts

### Templates
- `docs/templates/DECISION_LOG_TEMPLATE.md`
- `docs/templates/RAID_LOG_TEMPLATE.md`
- `docs/templates/WEEKLY_EXEC_UPDATE_TEMPLATE.md`

### Samples
- `docs/samples/DECISION_LOG_SAMPLE.md`
- `docs/samples/RAID_LOG_SAMPLE.md`
- `docs/samples/WEEKLY_EXEC_UPDATE_2026-01-02.md`

### System View
- `docs/diagrams/system_view.md`

---

## Repo Structure

```
data/
  raw/                       # synthetic/anonymized source data
  processed/                 # rollups used by charts 
docs/
  data_dictionary/           # column-level documentation
  diagrams/                  # system views
  evidence/                  # auto-generated outputs
  images/                    # screenshots / preview PDF
  samples/                   # program artifacts
  templates/                 # program templates
src/
  analytics/                 # readiness, critical path, expedite logic
  tooling/                   # evidence generation scripts
  utils/                     # IO helpers
app.py                       # Streamlit dashboard
.github/                     # CI workflow
```

---

## 🤝 Contributing

This is a demonstration project for portfolio purposes. To extend:

1. Fork the repository
2. Create a feature branch
3. Add enhancements (new models, visualizations, data sources)
4. Submit a pull request

---

## 📬 Connect

**Sourabh Tarodekar** | CapEx Program Management · NPI Operations · Portfolio Analytics

[LinkedIn](https://www.linkedin.com/in/sourabh232) · [Email](mailto:sourabh232@gmail.com) · [Full Portfolio](https://github.com/QuantuMaster007/sourabh232.git)

---

## 📄 License

MIT License — See LICENSE file for details
```
