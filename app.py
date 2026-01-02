import pandas as pd
import streamlit as st

from src.utils.io import read_csv
from src.analytics.readiness import compute_readiness
from src.analytics.critical_path import compute_critical_path
from src.analytics.expedite import expedite_summary

st.set_page_config(page_title="CapEx & Factory Readiness Dashboard", layout="wide")
st.title("CapEx / Factory Readiness Dashboard")
st.caption("Synthetic/anonymized demo data. Use filters to simulate a real factory readiness + CapEx governance view.")

capex = read_csv("data/raw/capex_plan_vs_actuals.csv")
lead = read_csv("data/raw/lead_times_expedite.csv")
tasks = read_csv("data/raw/facility_readiness_tasks.csv")

st.sidebar.header("Filters")
program = st.sidebar.selectbox("Program", ["All"] + sorted(capex["program"].unique().tolist()))
site = st.sidebar.selectbox("Site", ["All"] + sorted(tasks["site"].unique().tolist()))
tool = st.sidebar.selectbox("Tool", ["All"] + sorted(tasks["tool_id"].unique().tolist()))
gate = st.sidebar.selectbox("Gate", ["All","Install","PowerOn","Comm","SAT"])

cap_f = capex.copy()
lead_f = lead.copy()
tasks_f = tasks.copy()

if program != "All":
    cap_f = cap_f[cap_f["program"]==program]
    lead_f = lead_f[lead_f["program"]==program]
    tasks_f = tasks_f[tasks_f["program"]==program]
if site != "All":
    tasks_f = tasks_f[tasks_f["site"]==site]
if tool != "All":
    cap_f = cap_f[cap_f["tool_id"]==tool]
    lead_f = lead_f[lead_f["tool_id"]==tool]
    tasks_f = tasks_f[tasks_f["tool_id"]==tool]
if gate != "All":
    tasks_f = tasks_f[tasks_f["gate"]==gate]

# KPIs
cap_f["variance_usd"] = cap_f["actual_spend_usd"] - cap_f["planned_spend_usd"]
plan = cap_f["planned_spend_usd"].sum()
act = cap_f["actual_spend_usd"].sum()
fcst = cap_f["forecast_spend_usd"].sum()
var = cap_f["variance_usd"].sum()
exp = lead_f["expedite_spend_usd"].sum()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Planned ($)", f"{plan:,.0f}")
k2.metric("Actual ($)", f"{act:,.0f}", f"{var:,.0f}")
k3.metric("Forecast ($)", f"{fcst:,.0f}")
k4.metric("Expedite ($)", f"{exp:,.0f}")
k5.metric("Open tasks", f"{int((tasks_f['status']!='Done').sum()):,}")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Critical Path", "Blockers", "Expedite", "CapEx Variance"])

with tab1:
    st.subheader("What’s on the critical path?")
    if program == "All":
        program_cp = tasks["program"].iloc[0]
    else:
        program_cp = program
    if tool == "All":
        tool_cp = tasks[tasks["program"]==program_cp]["tool_id"].iloc[0]
    else:
        tool_cp = tool
    cp = compute_critical_path(tasks, program=program_cp, tool_id=tool_cp)
    st.caption(f"Longest planned dependency chain for **{program_cp}** / **{tool_cp}**.")
    st.dataframe(cp, use_container_width=True, hide_index=True)

    st.subheader("Readiness rollup (RAG)")
    r = compute_readiness(tasks if (program=="All" and site=="All" and tool=="All" and gate=="All") else tasks_f)
    st.dataframe(r, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("What’s blocking installation / power-on?")
    blockers = tasks_f[tasks_f["status"].isin(["Blocked","In Progress"])].copy()
    blockers["planned_finish"] = pd.to_datetime(blockers["planned_finish"])
    blockers = blockers.sort_values(["gate","status","risk_level","planned_finish"], ascending=[True, True, False, True]).head(50)
    st.dataframe(blockers[["program","site","area","tool_id","task_id","task_name","gate","owner","planned_finish","status","risk_level"]],
                 use_container_width=True, hide_index=True)

    st.subheader("Gate slip risk (why the gate slips)")
    incom = tasks_f[tasks_f["status"]!="Done"].copy()
    incom["planned_finish"] = pd.to_datetime(incom["planned_finish"])
    slip = (incom.groupby(["gate"], as_index=False)
                .agg(next_gate_date=("planned_finish","max"),
                     open_tasks=("task_id","count"),
                     blocked=("status", lambda s: int((s=="Blocked").sum())),
                     high_risk=("risk_level", lambda s: int((s=="High").sum()))))
    slip = slip.sort_values(["next_gate_date","blocked","high_risk"], ascending=[True, False, False])
    st.dataframe(slip, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Where are we burning expedite?")
    es = expedite_summary(lead_f)
    st.dataframe(es.head(30), use_container_width=True, hide_index=True)
    st.bar_chart(es.set_index(es.columns[0])["expedite_spend_usd"].head(12))

    st.subheader("Expedite trend (processed dataset)")
    proc = read_csv("data/processed/expedite_by_month_vendor.csv")
    if program != "All":
        proc = proc[proc["vendor"].isin(es["vendor"].unique().tolist())]  # keep relevant vendors
    st.dataframe(proc.tail(24), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("CapEx variance (Plan vs Actual) — by category")
    by_cat = (cap_f.groupby(["capex_category"], as_index=False)
                 .agg(planned=("planned_spend_usd","sum"),
                      actual=("actual_spend_usd","sum"),
                      variance=("variance_usd","sum"))
                 .sort_values("variance", ascending=False))
    st.dataframe(by_cat, use_container_width=True, hide_index=True)

    st.subheader("CapEx variance by month/category (processed dataset)")
    proc = read_csv("data/processed/capex_variance_by_month_category.csv")
    if program != "All":
        proc = proc[proc["program"]==program]
    st.dataframe(proc.tail(36), use_container_width=True, hide_index=True)
