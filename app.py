import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="Factory Readiness Command Center", layout="wide")

# 2. Advanced CSS for Custom Metric Cards
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricValue"] { color: #38bdf8; font-size: 1.8rem !important; }
    [data-testid="stMetricLabel"] { color: #94a3b8; font-size: 1rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Header
st.title("🏗️ CapEx / Factory Readiness Dashboard")
st.caption("Strategic Portfolio Governance & Operational Readiness Tracking")
st.markdown("---")

# 4. Data Loading
try:
    capex = pd.read_csv("data/raw/capex_plan_vs_actuals.csv")
    tasks = pd.read_csv("data/raw/facility_readiness_tasks.csv")
    lead = pd.read_csv("data/raw/lead_times_expedite.csv")
except:
    st.error("⚠️ Data missing. Please run your data generation scripts.")
    st.stop()

# 5. Strategic KPIs (Top Row)
m1, m2, m3, m4, m5 = st.columns(5)
total_plan = capex['planned_spend_usd'].sum()
total_act = capex['actual_spend_usd'].sum()
expedite = lead['expedite_spend_usd'].sum()
open_tasks = len(tasks[tasks['status'] != 'Done'])

m1.metric("Planned ($)", f"{total_plan:,.0f}")
m2.metric("Actual ($)", f"{total_act:,.0f}", f"{(total_act-total_plan):+,.0f}", delta_color="inverse")
m3.metric("Forecast ($)", f"{total_act * 1.02:,.0f}")
m4.metric("Expedite ($)", f"{expedite:,.0f}")
m5.metric("Open Tasks", open_tasks)

st.write("") # Spacing

# 6. Functional Tabs
tab1, tab2, tab3 = st.tabs(["📊 Readiness Analytics", "💰 Financial Variance", "📑 Evidence Reports"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Operational Readiness by Site")
        # Creating a more attractive bar chart than a table
        fig_site = px.histogram(
            tasks, x="site", color="status", barmode="group",
            color_discrete_map={'Done': '#22c55e', 'Blocked': '#ef4444', 'In Progress': '#3b82f6', 'At Risk': '#f59e0b'}
        )
        fig_site.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_site, use_container_width=True)

    with col2:
        st.subheader("Critical Path Risk")
        blocked_pct = (len(tasks[tasks['status'] == 'Blocked']) / len(tasks)) * 100
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = blocked_pct,
            number = {'suffix': "%", 'font': {'color': 'white'}},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#ef4444"},
                'steps': [{'range': [0, 15], 'color': "#1e293b"}, {'range': [15, 100], 'color': "#450a0a"}]
            }
        ))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=300, margin=dict(t=30, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.subheader("Detailed Critical Path Tasks")
    st.dataframe(tasks[tasks['status'] != 'Done'].head(10), use_container_width=True)

with tab2:
    st.subheader("Budget Variance by Category")
    fin_data = capex.groupby('capex_category')[['planned_spend_usd', 'actual_spend_usd']].sum().reset_index()
    fig_fin = px.bar(fin_data, x='capex_category', y=['planned_spend_usd', 'actual_spend_usd'], barmode='group')
    fig_fin.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_fin, use_container_width=True)

with tab3:
    st.subheader("Audit Logs & Generated Evidence")
    evidence_path = "docs/evidence"
    if os.path.exists(evidence_path):
        files = [f for f in os.listdir(evidence_path) if f.endswith('.md')]
        if files:
            selected = st.selectbox("Select Report", files)
            with open(os.path.join(evidence_path, selected), "r") as f:
                st.markdown(f.read())
