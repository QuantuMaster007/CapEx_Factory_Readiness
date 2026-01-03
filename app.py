import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from src.utils.io import read_csv
from src.analytics.readiness import compute_readiness
from src.analytics.critical_path import compute_critical_path
from src.analytics.expedite import expedite_summary

# 1. Page Configuration & Theme
st.set_page_config(page_title="CapEx & Factory Readiness", layout="wide")

# Custom CSS for a professional "Enterprise" look
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    [data-testid="stMetricValue"] { font-size: 32px; font-weight: 700; color: #1E3A8A; }
    [data-testid="stMetricDelta"] { font-size: 16px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Header
st.title("🏗️ CapEx & Factory Readiness Command Center")
st.caption("Operational readiness and financial governance for global factory scaling.")
st.divider()

# 3. Data Loading
@st.cache_data
def load_all_data():
    capex = read_csv("data/raw/capex_plan_vs_actuals.csv")
    lead = read_csv("data/raw/lead_times_expedite.csv")
    tasks = read_csv("data/raw/facility_readiness_tasks.csv")
    return capex, lead, tasks

capex, lead, tasks = load_all_data()

# 4. Sidebar Filters
st.sidebar.header("Global Controls")
program = st.sidebar.selectbox("Program Focus", ["All"] + sorted(capex["program"].unique().tolist()))
site = st.sidebar.selectbox("Geographic Site", ["All"] + sorted(tasks["site"].unique().tolist()))
tool = st.sidebar.selectbox("Tool ID", ["All"] + sorted(tasks["tool_id"].unique().tolist()))
gate = st.sidebar.selectbox("Project Gate", ["All","Install","PowerOn","Comm","SAT"])

# Apply Filtering Logic
cap_f = capex.copy()
lead_f = lead.copy()
tasks_f = tasks.copy()

if program != "All":
    cap_f, lead_f, tasks_f = cap_f[cap_f["program"]==program], lead_f[lead_f["program"]==program], tasks_f[tasks_f["program"]==program]
if site != "All":
    tasks_f = tasks_f[tasks_f["site"]==site]
if tool != "All":
    cap_f, lead_f, tasks_f = cap_f[cap_f["tool_id"]==tool], lead_f[lead_f["tool_id"]==tool], tasks_f[tasks_f["tool_id"]==tool]
if gate != "All":
    tasks_f = tasks_f[tasks_f["gate"]==gate]

# 5. KPI Row
cap_f["variance_usd"] = cap_f["actual_spend_usd"] - cap_f["planned_spend_usd"]
plan, act, var = cap_f["planned_spend_usd"].sum(), cap_f["actual_spend_usd"].sum(), cap_f["variance_usd"].sum()
exp = lead_f["expedite_spend_usd"].sum()
open_tasks = int((tasks_f['status']!='Done').sum())

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Budgeted CapEx", f"${plan/1e6:.1f}M")
k2.metric("Actual Spend", f"${act/1e6:.1f}M", f"{var/1e3:.1f}k Var", delta_color="inverse")
k3.metric("Expedite Burn", f"${exp/1e3:.1f}k")
k4.metric("Open Tasks", open_tasks)
k5.metric("System Health", "Active" if var < plan*0.1 else "Review Required")

st.divider()

# 6. Tabbed Analytics
tab1, tab2, tab3, tab4 = st.tabs(["⚡ Critical Path", "🚩 Blockers & Risk", "✈️ Expedite Analysis", "📊 Financial Variance"])

with tab1:
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("Critical Path Dependencies")
        prog_cp = program if program != "All" else tasks["program"].iloc[0]
        tool_cp = tool if tool != "All" else tasks[tasks["program"]==prog_cp]["tool_id"].iloc[0]
        cp = compute_critical_path(tasks, program=prog_cp, tool_id=tool_cp)
        st.dataframe(cp, use_container_width=True, hide_index=True)

    with col_b:
        st.subheader("Readiness RAG")
        r = compute_readiness(tasks_f)
        def color_status(val):
            color = '#ef4444' if val == 'Red' else '#f59e0b' if val == 'Amber' else '#22c55e'
            return f'background-color: {color}; color: white; font-weight: bold'
        
        if 'readiness_score' in r.columns:
             st.dataframe(r.style.applymap(color_status, subset=['readiness_score']), use_container_width=True)
        else:
             st.dataframe(r, use_container_width=True)

with tab2:
    st.subheader("Immediate Execution Blockers")
    blockers = tasks_f[tasks_f["status"].isin(["Blocked","In Progress"])].copy()
    blockers["planned_finish"] = pd.to_datetime(blockers["planned_finish"])
    blockers = blockers.sort_values(["risk_level","planned_finish"], ascending=[False, True]).head(20)
    
    # Dynamic styling for risk levels
    st.dataframe(blockers[["program","site","tool_id","task_name","gate","owner","status","risk_level"]], use_container_width=True)

    # Gauge Chart for Risk
    total = len(tasks_f)
    blocked = len(tasks_f[tasks_f["status"]=="Blocked"])
    fig_risk = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = (blocked/total*100) if total > 0 else 0,
        title = {'text': "Critical Blockage %"},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#1E3A8A"}}
    ))
    fig_risk.update_layout(height=250)
    st.plotly_chart(fig_risk, use_container_width=True)

with tab3:
    st.subheader("Expedite Spending by Vendor")
    es = expedite_summary(lead_f)
    
    fig_exp = px.bar(es.head(10), x='vendor', y='expedite_spend_usd', 
                     title="Top 10 Expedite Costs", color_discrete_sequence=['#1E3A8A'])
    st.plotly_chart(fig_exp, use_container_width=True)
    
    with st.expander("View Full Expedite Data"):
        st.dataframe(es, use_container_width=True)

with tab4:
    st.subheader("CapEx Variance: Plan vs Actual")
    by_cat = cap_f.groupby("capex_category")[["planned_spend_usd", "actual_spend_usd"]].sum().reset_index()
    
    fig_var = go.Figure(data=[
        go.Bar(name='Planned', x=by_cat['capex_category'], y=by_cat['planned_spend_usd'], marker_color='#94A3B8'),
        go.Bar(name='Actual', x=by_cat['capex_category'], y=by_cat['actual_spend_usd'], marker_color='#1E3A8A')
    ])
    fig_var.update_layout(barmode='group', title="Financial Integrity by Category")
    st.plotly_chart(fig_var, use_container_width=True)
