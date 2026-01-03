import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="Executive Readiness Dashboard", layout="wide")

# 2. Professional Theme CSS (Dark Mode Focus)
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    div[data-testid="stMetric"] { 
        background-color: #1e293b; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #334155; 
    }
    [data-testid="stMetricValue"] { color: #38bdf8; }
    [data-testid="stMetricLabel"] { color: #94a3b8; }
    /* Fix for dataframe visibility in dark mode */
    .stDataFrame { background-color: #1e293b; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header
st.title("🏗️ Factory Readiness Command Center")
st.caption("Real-time CapEx Governance & Operational Readiness Tracking")
st.markdown("---")

# 4. Data Loading with Error Handling
try:
    capex = pd.read_csv("data/raw/capex_plan_vs_actuals.csv")
    tasks = pd.read_csv("data/raw/facility_readiness_tasks.csv")
    lead = pd.read_csv("data/raw/lead_times_expedite.csv")
except Exception as e:
    st.error(f"⚠️ Data files missing or corrupted! Error: {e}")
    st.info("Run 'python generate_data.py' to generate the required CSV files.")
    st.stop()

# 5. Top-Level KPIs
k1, k2, k3, k4 = st.columns(4)
total_plan = capex['planned_spend_usd'].sum()
total_act = capex['actual_spend_usd'].sum()
var = total_act - total_plan
blocked_count = len(tasks[tasks['status'] == 'Blocked'])

k1.metric("Total Budgeted", f"${total_plan/1e6:.1f}M")
k2.metric("Actual Spend", f"${total_act/1e6:.1f}M", f"{var/1e6:+.1f}M Var", delta_color="inverse")
k3.metric("Blocked Tasks", blocked_count, delta="Critical Path" if blocked_count > 0 else "Clear")
k4.metric("Avg Expedite Cost", f"${lead['expedite_spend_usd'].mean()/1e3:.1f}k")

# 6. Tabbed Interface
tab1, tab2, tab3 = st.tabs(["🎯 Program Readiness", "💰 Financial Governance", "📑 Evidence Reports"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Task Status by Geographic Site")
        fig_status = px.histogram(
            tasks, x="site", color="status", barmode="group",
            color_discrete_map={
                'Done': '#22c55e', 
                'Blocked': '#ef4444', 
                'In Progress': '#3b82f6', 
                'At Risk': '#f59e0b'
            }
        )
        fig_status.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color="white",
            legend_title_text='Status'
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.subheader("Global Blockage %")
        total_tasks = len(tasks)
        blocked_pct = (blocked_count / total_tasks * 100) if total_tasks > 0 else 0
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = blocked_pct,
            number = {'suffix': "%", 'font': {'color': 'white'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickcolor': "white"},
                'bar': {'color': "#ef4444"}, 
                'steps': [
                    {'range': [0, 20], 'color': "#1e293b"}, 
                    {'range': [20, 100], 'color': "#450a0a"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': 15
                }
            },
            title = {'text': "Critical Path Health", 'font': {'color': 'white'}}
        ))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

with tab2:
    st.subheader("CapEx Variance by Category")
    # Grouping data for a cleaner bar chart
    fin_summary = capex.groupby('capex_category')[['planned_spend_usd', 'actual_spend_usd']].sum().reset_index()
    
    fig_var = px.bar(
        fin_summary, 
        x='capex_category', 
        y=['planned_spend_usd', 'actual_spend_usd'],
        barmode='group',
        labels={'value': 'USD ($)', 'variable': 'Budget Type'},
        color_discrete_sequence=['#94a3b8', '#38bdf8']
    )
    fig_var.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_var, use_container_width=True)
    
    st.subheader("Detailed Vendor Expedite Costs")
    st.dataframe(lead.sort_values('expedite_spend_usd', ascending=False), use_container_width=True)

with tab3:
    st.subheader("Detailed Evidence Logs & Audits")
    st.info("These reports are auto-generated from the latest project telemetry.")
    
    evidence_path = "docs/evidence"
    
    if os.path.exists(evidence_path):
        reports = [f for f in os.listdir(evidence_path) if f.endswith('.md')]
        
        if reports:
            selected_report = st.selectbox("Select Evidence File", sorted(reports))
            
            # Read and display the markdown content
            with open(os.path.join(evidence_path, selected_report), "r") as f:
                report_content = f.read()
                st.markdown("---")
                st.markdown(report_content)
        else:
            st.warning("No markdown reports found in `docs/evidence/`. Run your evidence generation script first.")
    else:
        st.error(f"Directory `{evidence_path}` not found. Ensure your backend scripts have run.")
