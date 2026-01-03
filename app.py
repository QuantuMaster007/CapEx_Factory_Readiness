import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Setup
st.set_page_config(page_title="Executive Readiness Dashboard", layout="wide")

# Professional Theme CSS
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    div[data-testid="stMetric"] { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    [data-testid="stMetricValue"] { color: #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("🏗️ Factory Readiness Command Center")
st.markdown("---")

# Data Loading (with error handling)
try:
    capex = pd.read_csv("data/raw/capex_plan_vs_actuals.csv")
    tasks = pd.read_csv("data/raw/facility_readiness_tasks.csv")
    lead = pd.read_csv("data/raw/lead_times_expedite.csv")
except:
    st.error("Data files missing! Run python generate_data.py first.")
    st.stop()

# KPIs
k1, k2, k3, k4 = st.columns(4)
total_plan = capex['planned_spend_usd'].sum()
total_act = capex['actual_spend_usd'].sum()
var = total_act - total_plan

k1.metric("Total Budgeted", f"${total_plan/1e6:.1f}M")
k2.metric("Actual Spend", f"${total_act/1e6:.1f}M", f"{var/1e6:+.1f}M", delta_color="inverse")
k3.metric("Blocked Tasks", len(tasks[tasks['status'] == 'Blocked']))
k4.metric("Avg Expedite", f"${lead['expedite_spend_usd'].mean()/1e3:.1f}k")

# Main Content
tab1, tab2 = st.tabs(["🎯 Program Readiness", "💰 Financial Governance"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Task Status by Site")
        # Visualizing status distribution
        fig_status = px.histogram(tasks, x="site", color="status", barmode="group",
                                 color_discrete_map={'Done': '#22c55e', 'Blocked': '#ef4444', 'In Progress': '#3b82f6', 'At Risk': '#f59e0b'})
        fig_status.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.subheader("Global Blockage %")
        blocked_pct = (len(tasks[tasks['status'] == 'Blocked']) / len(tasks)) * 100
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = blocked_pct,
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#ef4444"}, 
                     'steps': [{'range': [0, 20], 'color': "#1e293b"}, {'range': [20, 100], 'color': "#450a0a"}]},
            title = {'text': "Critical Path Blockers"}
        ))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

with tab2:
    st.subheader("CapEx Variance by Category")
    fig_var = px.bar(capex.groupby('capex_category').sum().reset_index(), 
                     x='capex_category', y=['planned_spend_usd', 'actual_spend_usd'],
                     barmode='group', title="Planned vs Actual per Category")
    fig_var.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_var, use_container_width=True)
    
    st.subheader("Detailed Vendor Expedite Costs")
    st.dataframe(lead.sort_values('expedite_spend_usd', ascending=False), use_container_width=True)
