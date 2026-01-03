import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from src.utils.io import read_csv
from src.analytics.readiness import compute_readiness
from src.analytics.critical_path import compute_critical_path
from src.analytics.expedite import expedite_summary

st.set_page_config(page_title="CapEx & Factory Readiness", layout="wide")

# Modern UI Styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stMetricValue"] { font-size: 32px; color: #1e293b; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 6px;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0f172a !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Factory Readiness Command Center")
st.caption(f"Running on Python {pd.sys.version.split()[0]} | Integrated CapEx & Readiness View")

# Data Loading
@st.cache_data
def load_data():
    return read_csv("data/raw/capex_plan_vs_actuals.csv"), \
           read_csv("data/raw/lead_times_expedite.csv"), \
           read_csv("data/raw/facility_readiness_tasks.csv")

capex, lead, tasks = load_data()

# Filters
st.sidebar.header("Global Filters")
program = st.sidebar.selectbox("Program", ["All"] + sorted(capex["program"].unique().tolist()))
site = st.sidebar.selectbox("Site", ["All"] + sorted(tasks["site"].unique().tolist()))

# Filtering logic (Simplified)
tasks_f = tasks.copy()
if program != "All":
    tasks_f = tasks_f[tasks_f["program"]==program]
if site != "All":
    tasks_f = tasks_f[tasks_f["site"]==site]

# KPI Row
k1, k2, k3, k4 = st.columns(4)
k1.metric("Planned CapEx", f"${capex['planned_spend_usd'].sum()/1e6:.1f}M")
k2.metric("Actual Spend", f"${capex['actual_spend_usd'].sum()/1e6:.1f}M")
k3.metric("Expedite Costs", f"${lead['expedite_spend_usd'].sum()/1e3:.1f}k")
k4.metric("Open Tasks", len(tasks_f[tasks_f['status'] != 'Done']))

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(["⚡ Readiness", "🚩 Risk & Blockers", "📊 Financials"])

with tab1:
    st.subheader("Critical Path & RAG Status")
    col1, col2 = st.columns([2,1])
    with col1:
        # Placeholder for your specific critical path logic
        st.write("Critical Path Analysis")
        st.dataframe(tasks_f.head(10), use_container_width=True)
    with col2:
        r = compute_readiness(tasks_f)
        if 'readiness_score' in r.columns:
            # Using .map for Python 3.12 / Pandas 2.2+ compatibility
            st.dataframe(r.style.map(lambda x: 'background-color: #ef4444; color: white' if x == 'Red' else '', subset=['readiness_score']))

with tab2:
    # Gauge Chart
    total = len(tasks_f)
    blocked = len(tasks_f[tasks_f['status'] == 'Blocked'])
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = (blocked/total*100) if total > 0 else 0,
        title = {'text': "% Tasks Blocked"},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#ef4444"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("CapEx Variance")
    fig_var = px.bar(capex, x="capex_category", y=["planned_spend_usd", "actual_spend_usd"], barmode="group")
    st.plotly_chart(fig_var, use_container_width=True)
