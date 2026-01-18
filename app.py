import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="Executive Command Center | Advanced Factory Readiness",
    page_icon="🏗️",
    layout="wide"
)

# 2. Advanced CSS (Glassmorphism + Neon accents)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; }
    section[data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.8); border-right: 1px solid #334155; }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px; border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
    }
    .metric-label { color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
    .metric-value { color: #00f2ff; font-size: 1.8rem; font-weight: 700; }
    .metric-delta { font-size: 0.8rem; margin-top: 4px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading
@st.cache_data
def load_data():
    try:
        capex = pd.read_csv("data/raw/capex_plan_vs_actuals.csv")
        tasks = pd.read_csv("data/raw/facility_readiness_tasks.csv")
        lead = pd.read_csv("data/raw/lead_times_expedite.csv")
        return capex, tasks, lead
    except:
        return None, None, None

capex, tasks, lead = load_data()

if capex is None:
    st.error("⚠️ Data missing. Please ensure your CSV files are in the 'data/raw/' directory.")
    st.stop()

# 4. Sidebar: Navigation + WHAT-IF PARAMETERS
with st.sidebar:
    st.title("⚙️ Controls")
    page = st.radio("Navigation", ["Executive Overview", "Financial Intelligence", "Operational Risk"])
    
    st.markdown("---")
    st.subheader("🔮 What-If Analysis")
    st.caption("Simulate impact on remaining budget")
    # Simulation Parameters
    cost_multiplier = st.slider("Forecasted Inflation (%)", 0, 20, 5) / 100
    expedite_risk = st.select_slider("Supply Chain Delay Risk", options=["Low", "Medium", "High", "Critical"])
    
    risk_factor = {"Low": 1.0, "Medium": 1.15, "High": 1.4, "Critical": 2.0}[expedite_risk]
    
    st.markdown("---")
    st.info(f"**Last Refresh:** {datetime.now().strftime('%H:%M:%S')}")

# 5. Helper Function for Cards
def custom_metric(label, value, delta=None, delta_color="normal"):
    delta_html = ""
    if delta:
        color = "#10b981" if delta_color == "normal" else "#ef4444"
        delta_html = f'<div class="metric-delta" style="color: {color}">{delta}</div>'
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div>{delta_html}</div>', unsafe_allow_html=True)

# 6. Page Routing
if page == "Executive Overview":
    st.header("🚀 Strategic Portfolio Governance")
    
    # CALCULATE PREDICTIVE METRICS
    actual_total = capex['actual_spend_usd'].sum()
    planned_total = capex['planned_spend_usd'].sum()
    remaining_planned = max(0, planned_total - actual_total)
    # Applying What-If Logic
    projected_final = actual_total + (remaining_planned * (1 + cost_multiplier) * risk_factor)
    budget_variance_proj = projected_final - planned_total

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        custom_metric("Baseline Budget", f"${planned_total:,.0f}")
    with m2:
        custom_metric("Current Actuals", f"${actual_total:,.0f}")
    with m3:
        color = "inverse" if budget_variance_proj > 0 else "normal"
        custom_metric("Projected Final Spend", f"${projected_final:,.0f}", f"${budget_variance_proj:+,.0f} vs Plan", color)
    with m4:
        blocked_pct = (len(tasks[tasks['status'] == 'Blocked']) / len(tasks)) * 100
        custom_metric("Risk Index", f"{blocked_pct:.1f}%", "Blocked Tasks", "inverse")

    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Site Readiness Tracker")
        fig_site = px.bar(tasks, x="site", color="status", barmode="stack", 
                         color_discrete_map={'Done': '#22c55e', 'Blocked': '#ef4444', 'In Progress': '#3b82f6', 'At Risk': '#f59e0b'},
                         template="plotly_dark")
        fig_site.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_site, use_container_width=True)
    
    with col2:
        st.subheader("Simulation Insight")
        st.write(f"Based on a **{cost_multiplier*100:.0f}%** inflation forecast and **{expedite_risk}** supply chain risk:")
        if budget_variance_proj > 0:
            st.warning(f"⚠️ Your project is at risk of exceeding budget by **${budget_variance_proj:,.0f}**.")
        else:
            st.success("✅ Projected spend remains within baseline boundaries.")

elif page == "Financial Intelligence":
    st.header("💰 Budget Variance & Financial Storytelling")
    
    # WATERFALL CHART LOGIC
    # Showing how we got from Planned to Actual
    fin_summary = capex.groupby('capex_category')[['planned_spend_usd', 'actual_spend_usd']].sum()
    fin_summary['variance'] = fin_summary['actual_spend_usd'] - fin_summary['planned_spend_usd']
    
    categories = fin_summary.index.tolist()
    variances = fin_summary['variance'].tolist()
    
    fig_waterfall = go.Figure(go.Waterfall(
        name = "Budget Leakage", orientation = "v",
        measure = ["absolute"] + (["relative"] * len(categories)) + ["total"],
        x = ["Planned"] + categories + ["Current Actual"],
        textposition = "outside",
        text = [f"${planned_total:,.0f}"] + [f"{v:+,.0f}" for v in variances] + [f"${actual_total:,.0f}"],
        y = [planned_total] + variances + [0], # Plotly handles the 'total' measure automatically
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        increasing = {"marker":{"color":"#ef4444"}}, # Cost increase is red
        decreasing = {"marker":{"color":"#22c55e"}}, # Cost decrease is green
        totals = {"marker":{"color":"#38bdf8"}}
    ))
    
    fig_waterfall.update_layout(title = "Budget Variance Waterfall (Planned to Actual)", 
                               template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_waterfall, use_container_width=True)

    st.markdown("---")
    st.subheader("Category Breakdown")
    st.dataframe(fin_summary.style.format("${:,.0f}").background_gradient(subset=['variance'], cmap='RdYlGn_r'), use_container_width=True)

elif page == "Operational Risk":
    st.header("⚠️ Logistics & Critical Path")
    # Sunburst Chart for deep dive into site/status
    fig_sun = px.sunburst(tasks, path=['site', 'status'], values=None,
                         color='status', color_discrete_map={'Done': '#22c55e', 'Blocked': '#ef4444', 'In Progress': '#3b82f6', 'At Risk': '#f59e0b'},
                         template="plotly_dark")
    st.plotly_chart(fig_sun, use_container_width=True)
