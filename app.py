import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
import hashlib

# ==================== CONFIGURATION MANAGEMENT ====================
CONFIG = {
    "paths": {
        "capex": "data/raw/capex_plan_vs_actuals.csv",
        "tasks": "data/raw/facility_readiness_tasks.csv",
        "lead": "data/raw/lead_times_expedite.csv",
        "evidence": "docs/evidence",
        "logo": "assets/company_logo.png"  # Local fallback option
    },
    "colors": {
        "primary": "#00f2ff",
        "secondary": "#38bdf8",
        "accent": "#fbbf24",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "background": "#0f172a",
        "card_bg": "rgba(30, 41, 59, 0.7)",
        "text": "#f8fafc",
        "text_secondary": "#94a3b8"
    },
    "thresholds": {
        "blocked_alert": 10.0,  # Percentage
        "variance_tolerance": 5.0  # Percentage
    },
    "auth": {
        "enabled": False,  # Set True to enable basic auth
        "users": {"admin": "sha256_hash_of_password"}  # Use hashed passwords
    }
}

# ==================== AUTHENTICATION ====================
def check_password():
    """Returns `True` if the user has the correct password."""
    if not CONFIG["auth"]["enabled"]:
        return True
    
    def password_entered():
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() in CONFIG["auth"]["users"].values():
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# ==================== DATA VALIDATION ====================
def validate_dataframe(df: pd.DataFrame, required_cols: list, name: str) -> pd.DataFrame:
    """Validate dataframe schema and provide helpful errors."""
    missing = set(required_cols) - set(df.columns)
    if missing:
        st.error(f"❌ **{name}** missing columns: {', '.join(missing)}")
        st.stop()
    return df

# ==================== DATA LOADING ====================
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def load_data() -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Load and validate all datasets with error handling."""
    try:
        # Define expected schemas
        schemas = {
            "capex": ["planned_spend_usd", "actual_spend_usd", "capex_category", "date"],
            "tasks": ["status", "site", "task_name", "priority", "due_date"],
            "lead": ["supplier", "category", "lead_time_days", "expedite_spend_usd"]
        }
        
        data = {}
        for key, path in CONFIG["paths"].items():
            if key in schemas:  # Only load CSVs, not directories
                if not os.path.exists(path):
                    st.warning(f"⚠️ File not found: {path}")
                    data[key] = pd.DataFrame()
                else:
                    df = pd.read_csv(path)
                    df = validate_dataframe(df, schemas[key], f"{key}.csv")
                    # Parse dates where applicable
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    if 'due_date' in df.columns:
                        df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
                    data[key] = df
        
        return data.get("capex"), data.get("tasks"), data.get("lead")
    except Exception as e:
        st.error(f"Critical data loading error: {str(e)}")
        return None, None, None

# ==================== THEMING ENGINE ====================
def apply_theme():
    """Centralized theme application with CSS variables."""
    colors = CONFIG["colors"]
    st.set_page_config(
        page_title="Executive Command Center | Factory Readiness",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown(f"""
        <style>
        /* CSS Variables for Consistency */
        :root {{
            --primary-color: {colors['primary']};
            --card-bg: {colors['card_bg']};
            --text-color: {colors['text']};
            --text-secondary: {colors['text_secondary']};
        }}
        
        .stApp {{
            background: linear-gradient(135deg, {colors['background']} 0%, #1e293b 100%);
            color: var(--text-color);
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: rgba(15, 23, 42, 0.8);
            border-right: 1px solid #334155;
        }}
        
        .metric-card {{
            background: var(--card-bg);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            margin-bottom: 10px;
            transition: transform 0.2s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
        }}
        
        .metric-label {{ color: var(--text-secondary); font-size: 0.9rem; font-weight: 600; }}
        .metric-value {{ color: var(--primary-color); font-size: 2rem; font-weight: 700; }}
        
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: {colors['background']}; }}
        ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 10px; }}
        
        /* Hide Streamlit branding */
        footer {{ visibility: hidden; }}
        </style>
    """, unsafe_allow_html=True)

# ==================== METRIC COMPONENTS ====================
def custom_metric(label: str, value: Any, delta: Optional[str] = None, 
                  delta_color: str = "normal", help_text: Optional[str] = None):
    """Enhanced metric card with help tooltips and delta logic."""
    colors = CONFIG["colors"]
    delta_html = ""
    if delta is not None:
        is_positive = not str(delta).startswith('-')
        color = colors["success"] if (delta_color == "normal" and is_positive) or (delta_color == "inverse" and not is_positive) else colors["danger"]
        prefix = "+" if is_positive else ""
        delta_html = f'<div class="metric-delta" style="color: {color}">{prefix}{delta}</div>'
    
    help_attr = f' title="{help_text}"' if help_text else ""
    st.markdown(f"""
        <div class="metric-card"{help_attr}>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

# ==================== DATA PROCESSING ====================
def calculate_kpis(capex: pd.DataFrame, tasks: pd.DataFrame, lead: pd.DataFrame) -> Dict:
    """Calculate all KPIs in one place for consistency."""
    try:
        total_planned = capex['planned_spend_usd'].sum() if not capex.empty else 0
        total_actual = capex['actual_spend_usd'].sum() if not capex.empty else 0
        variance = total_actual - total_planned
        
        blocked_count = len(tasks[tasks['status'] == 'Blocked']) if not tasks.empty else 0
        total_tasks = len(tasks) if not tasks.empty else 1
        blocked_pct = (blocked_count / total_tasks) * 100
        
        expedite_cost = lead['expedite_spend_usd'].sum() if not lead.empty else 0
        
        return {
            "total_planned": total_planned,
            "total_actual": total_actual,
            "variance": variance,
            "blocked_pct": blocked_pct,
            "expedite_cost": expedite_cost,
            "variance_pct": (variance / total_planned * 100) if total_planned > 0 else 0
        }
    except Exception as e:
        st.error(f"KPI calculation error: {e}")
        return {}

def prepare_time_series(capex: pd.DataFrame) -> pd.DataFrame:
    """Properly aggregate CapEx data by date."""
    if capex.empty or 'date' not in capex.columns:
        return pd.DataFrame()
    
    # Group by actual date periods
    monthly = capex.groupby([pd.Grouper(key='date', freq='M'), 'capex_category']).agg({
        'planned_spend_usd': 'sum',
        'actual_spend_usd': 'sum'
    }).reset_index()
    
    return monthly

# ==================== VISUALIZATION FACTORY ====================
def create_plotly_figure(chart_type: str, data: pd.DataFrame, **kwargs) -> go.Figure:
    """Centralized Plotly figure creation with theme."""
    colors = CONFIG["colors"]
    template = "plotly_dark"
    
    fig = None
    try:
        if chart_type == "area":
            fig = px.area(data, **kwargs, color_discrete_sequence=[colors['secondary'], colors['accent']], template=template)
        elif chart_type == "bar":
            fig = px.bar(data, **kwargs, color_discrete_sequence=[colors['text_secondary'], colors['primary']], template=template)
        elif chart_type == "pie":
            fig = px.pie(data, **kwargs, template=template)
        elif chart_type == "heatmap":
            fig = px.density_heatmap(data, **kwargs, color_continuous_scale="Viridis", template=template)
        elif chart_type == "radar":
            fig = px.line_polar(data, **kwargs, line_close=True, color_discrete_sequence=[colors['primary']], template=template)
            fig.update_traces(fill='toself')
        
        if fig:
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=colors['text'])
            )
        return fig
    except Exception as e:
        st.error(f"Chart creation error: {e}")
        return go.Figure()

# ==================== MAIN APPLICATION ====================
def main():
    if not check_password():
        return
    
    apply_theme()
    
    # Load data with spinner
    with st.spinner("Loading executive intelligence..."):
        capex, tasks, lead = load_data()
    
    # Graceful degradation for missing data
    if capex is None or (capex.empty and tasks.empty and lead.empty):
        st.error("⚠️ No data available. Please check configuration and file paths.")
        st.json(CONFIG["paths"])  # Show expected paths for debugging
        if st.button("Retry"):
            st.cache_data.clear()
            st.rerun()
        return
    
    # Sidebar
    with st.sidebar:
        # Logo with fallback
        try:
            if os.path.exists(CONFIG["paths"]["logo"]):
                st.image(CONFIG["paths"]["logo"], width=80)
            else:
                st.image("https://cdn-icons-png.flaticon.com/512/2855/2855160.png", width=80)
        except:
            st.title("🏗️")
        
        st.title("Command Center")
        st.markdown("---")
        
        # Filter options (new feature)
        if not tasks.empty:
            sites = ["All"] + list(tasks['site'].unique())
            selected_site = st.selectbox("Filter by Site", sites)
        
        page = st.radio("Navigation", [
            "Executive Overview", 
            "Financial Intelligence", 
            "Operational Risk", 
            "Audit Evidence"
        ])
        
        st.markdown("---")
        st.info(f"**Status:** Operational\n\n**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Data refresh button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Calculate KPIs once
    kpis = calculate_kpis(capex, tasks, lead)
    
    # Page routing
    if page == "Executive Overview":
        render_executive_page(kpis, capex, tasks, lead)
    elif page == "Financial Intelligence":
        render_financial_page(capex)
    elif page == "Operational Risk":
        render_risk_page(tasks, lead)
    elif page == "Audit Evidence":
        render_audit_page()

def render_executive_page(kpis: Dict, capex: pd.DataFrame, tasks: pd.DataFrame, lead: pd.DataFrame):
    """Render Executive Overview with real-time KPIs."""
    st.header("🚀 Strategic Portfolio Governance")
    
    # KPI Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        custom_metric("Total Planned Spend", f"${kpis.get('total_planned', 0):,.0f}", 
                     help_text="Baseline budget across all CapEx categories")
    with m2:
        variance_status = "inverse" if kpis.get('variance', 0) > 0 else "normal"
        custom_metric("Actual Spend", f"${kpis.get('total_actual', 0):,.0f}", 
                     f"${kpis.get('variance', 0):,.0f} ({kpis.get('variance_pct', 0):.1f}%)",
                     delta_color=variance_status,
                     help_text="Current spend vs. plan")
    with m3:
        risk_level = "High Alert" if kpis.get('blocked_pct', 0) > CONFIG["thresholds"]["blocked_alert"] else "Stable"
        custom_metric("Critical Path Risk", f"{kpis.get('blocked_pct', 0):.1f}%", 
                     risk_level,
                     delta_color="inverse" if kpis.get('blocked_pct', 0) > CONFIG["thresholds"]["blocked_alert"] else "normal",
                     help_text="Percentage of blocked tasks")
    with m4:
        custom_metric("Expedite Costs", f"${kpis.get('expedite_cost', 0):,.0f}", 
                     "Supply Chain Leakage", delta_color="inverse",
                     help_text="Unplanned expedite spend")
    
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("Monthly Spend Projection vs. Actuals")
        if not capex.empty and 'date' in capex.columns:
            monthly_data = prepare_time_series(capex)
            if not monthly_data.empty:
                fig_trend = create_plotly_figure("area", monthly_data, 
                    x='date', y=['planned_spend_usd', 'actual_spend_usd'],
                    title=""
                )
                st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No date-based data available for trending")
    
    with col_right:
        st.subheader("Site Readiness Score")
        if not tasks.empty:
            site_readiness = tasks.groupby('site')['status'].apply(
                lambda x: (x == 'Done').sum() / len(x) * 100 if len(x) > 0 else 0
            ).reset_index(name='completion_rate')
            
            if not site_readiness.empty:
                fig_radar = create_plotly_figure("radar", site_readiness,
                    r='completion_rate', theta='site'
                )
                st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("No task data available")

def render_financial_page(capex: pd.DataFrame):
    """Render Financial Intelligence page."""
    st.header("💰 Budget Variance & Analytics")
    
    if not capex.empty:
        cat_data = capex.groupby('capex_category')[['planned_spend_usd', 'actual_spend_usd']].sum().reset_index()
        cat_data['Variance %'] = ((cat_data['actual_spend_usd'] - cat_data['planned_spend_usd']) / cat_data['planned_spend_usd'] * 100).round(2)
        
        fig_cat = create_plotly_figure("bar", cat_data,
            x='capex_category', y=['planned_spend_usd', 'actual_spend_usd'],
            barmode='group', title="Spend by Category"
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        
        st.subheader("Variance Details")
        st.dataframe(
            cat_data.style.background_gradient(subset=['Variance %'], cmap='RdYlGn_r', vmin=-20, vmax=20),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No CapEx data available")

def render_risk_page(tasks: pd.DataFrame, lead: pd.DataFrame):
    """Render Operational Risk page."""
    st.header("⚠️ Readiness & Bottlenecks")
    
    if tasks.empty and lead.empty:
        st.warning("No operational data available")
        return
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        if not tasks.empty:
            st.subheader("Status Distribution")
            status_counts = tasks['status'].value_counts()
            fig_pie = create_plotly_figure("pie", status_counts.reset_index(),
                names='status', values='count',
                color='status',
                color_discrete_map={
                    'Done': CONFIG["colors"]["success"],
                    'Blocked': CONFIG["colors"]["danger"],
                    'In Progress': CONFIG["colors"]["primary"],
                    'At Risk': CONFIG["colors"]["warning"]
                },
                hole=0.6
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with c2:
        if not lead.empty:
            st.subheader("Lead Time Heatmap")
            fig_heat = create_plotly_figure("heatmap", lead,
                x="supplier", y="category", z="lead_time_days",
                title=""
            )
            st.plotly_chart(fig_heat, use_container_width=True)
    
    if not tasks.empty:
        st.subheader("Critical Tasks (Action Required)")
        critical_tasks = tasks[tasks['status'].isin(['Blocked', 'At Risk'])].copy()
        if not critical_tasks.empty:
            # Add priority scoring
            critical_tasks['priority_score'] = critical_tasks['priority'].map({
                'Critical': 3, 'High': 2, 'Medium': 1, 'Low': 0
            }).fillna(0)
            
            st.dataframe(
                critical_tasks.sort_values(['priority_score', 'due_date'], ascending=[False, True])
                .drop('priority_score', axis=1)
                .head(10),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No critical tasks requiring immediate action")

def render_audit_page():
    """Render Audit Evidence page."""
    st.header("📑 Documented Evidence")
    
    evidence_path = CONFIG["paths"]["evidence"]
    if os.path.exists(evidence_path):
        files = [f for f in os.listdir(evidence_path) if f.endswith('.md')]
        if files:
            selected = st.selectbox("Select Report to Review", sorted(files))
            try:
                with open(os.path.join(evidence_path, selected), "r") as f:
                    content = f.read()
                    st.markdown(content)
                    # Add download button
                    st.download_button(
                        label="Download Report",
                        data=content,
                        file_name=selected,
                        mime="text/markdown"
                    )
            except Exception as e:
                st.error(f"Error reading file: {e}")
        else:
            st.info("No markdown reports found. Add files to `docs/evidence/`")
    else:
        st.warning(f"Evidence directory not found at `{evidence_path}`")
        if st.button("Create Directory"):
            os.makedirs(evidence_path, exist_ok=True)
            st.rerun()

# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    main()
