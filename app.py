"""
HireFlow AI - Intelligent Recruitment & Employee Onboarding System
Academic Subject: AI Agents & Autonomous Business Operations
Tech Stack: Streamlit, Python, SQLite, Plotly, Pandas, PDFPlumber/PyPDF2, Gemini API
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

# Import backend modules
import database as db
from ai_agent import HireFlowAgent
import resume_parser

# --- Page Configuration ---
st.set_page_config(
    page_title="HireFlow AI | Autonomous HR Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first load
db.init_db()
db.seed_sample_data()

# --- Custom Styling (SaaS Modern Dark Executive Theme) ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: #0B0F19 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #F8FAFC;
    }
    
    /* Headers & Typography - Ultra High Contrast */
    h1 {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em;
        margin-bottom: 8px !important;
    }
    h2 {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #F1F5F9 !important;
        letter-spacing: -0.01em;
    }
    h3 {
        font-size: 17px !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        margin-top: 12px !important;
        margin-bottom: 8px !important;
    }
    h4, h5, h6 {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }
    p, span, div, label, li {
        color: #CBD5E1;
    }
    
    /* =========================================================================
       SIDEBAR STYLING - High Contrast Executive Dark Navy
       ========================================================================= */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #CBD5E1 !important;
    }
    
    /* Brand Card */
    .sidebar-brand-card {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 14px;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 12px;
        margin-bottom: 12px;
    }
    
    .brand-icon-box {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #2563EB 0%, #0284C7 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        flex-shrink: 0;
    }
    
    .brand-title {
        margin: 0 !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em;
        line-height: 1.15 !important;
    }
    
    .brand-accent {
        color: #38BDF8 !important;
    }
    
    .brand-subtitle {
        margin: 2px 0 0 0 !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        color: #94A3B8 !important;
        letter-spacing: 0.02em;
    }
    
    /* Course Project Card */
    .sidebar-course-card {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-left: 4px solid #38BDF8;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 12px;
    }
    
    .course-tag {
        font-size: 10px;
        font-weight: 700;
        color: #38BDF8 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    
    .course-name {
        font-size: 12px;
        font-weight: 600;
        color: #F8FAFC !important;
        line-height: 1.35;
    }
    
    /* Mode Indicator Card */
    .sidebar-mode-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px 12px;
        border-radius: 10px;
        margin-bottom: 12px;
        text-align: center;
        box-sizing: border-box;
        width: 100%;
    }
    
    .mode-demo {
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.35);
    }
    
    .mode-live {
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.35);
    }
    
    .mode-badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 700;
        color: #38BDF8 !important;
        margin-bottom: 3px;
        white-space: nowrap;
    }
    
    .mode-live .mode-badge-pill {
        color: #4ADE80 !important;
    }
    
    .mode-subtext {
        font-size: 10.5px;
        color: #94A3B8 !important;
        line-height: 1.25;
    }
    
    /* Radio Navigation Item Enhancements */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 6px 10px !important;
        border-radius: 8px !important;
        transition: all 0.15s ease-in-out !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        color: #E2E8F0 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
    }
    
    /* Live Stats Grid in Sidebar */
    .sidebar-stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 8px;
    }
    
    .sidebar-stat-box {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 8px;
        padding: 8px 10px;
        text-align: center;
    }
    
    .sidebar-stat-val {
        display: block;
        font-size: 18px;
        font-weight: 800;
        color: #38BDF8 !important;
        line-height: 1.2;
    }
    
    .sidebar-stat-lbl {
        display: block;
        font-size: 10px;
        font-weight: 600;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 2px;
    }

    /* =========================================================================
       MAIN CONTENT COMPONENTS - Dark Executive SaaS Theme
       ========================================================================= */
    /* Metric Cards */
    .metric-card {
        background: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px -2px rgba(0, 0, 0, 0.4);
        border-color: #475569 !important;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #38BDF8 !important;
        margin-top: 4px;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #94A3B8 !important;
    }
    
    /* Badges - Strictly Single-Pill Flex Layout with Dark Backgrounds */
    .badge-strong {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        background-color: rgba(34, 197, 94, 0.18) !important;
        color: #4ADE80 !important;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        border: 1px solid rgba(34, 197, 94, 0.4) !important;
    }
    .badge-potential {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        background-color: rgba(245, 158, 11, 0.18) !important;
        color: #FBBF24 !important;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        border: 1px solid rgba(245, 158, 11, 0.4) !important;
    }
    .badge-low {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        background-color: rgba(239, 68, 68, 0.18) !important;
        color: #F87171 !important;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
    }
    .badge-info {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        background-color: rgba(56, 189, 248, 0.18) !important;
        color: #38BDF8 !important;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
    }
    
    /* Academic Disclaimer Banner */
    .human-loop-banner {
        background: rgba(30, 58, 138, 0.3) !important;
        border-left: 4px solid #38BDF8 !important;
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left-width: 4px;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 13.5px;
        color: #E0F2FE !important;
        line-height: 1.5;
    }
    .human-loop-banner strong {
        color: #38BDF8 !important;
    }
    
    /* Tag Pills */
    .skill-pill-match {
        display: inline-flex;
        align-items: center;
        white-space: nowrap;
        background-color: rgba(56, 189, 248, 0.18) !important;
        color: #38BDF8 !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 6px;
        padding: 3px 9px;
        margin: 3px 5px 3px 0;
        font-size: 12px;
        font-weight: 600;
    }
    .skill-pill-miss {
        display: inline-flex;
        align-items: center;
        white-space: nowrap;
        background-color: rgba(244, 63, 94, 0.18) !important;
        color: #FB7185 !important;
        border: 1px solid rgba(244, 63, 94, 0.4) !important;
        border-radius: 6px;
        padding: 3px 9px;
        margin: 3px 5px 3px 0;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Buttons & Form Elements */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.45) !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button:not([kind="primary"]) {
        background: #1E293B !important;
        color: #E2E8F0 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        border: 1px solid #334155 !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: #64748B !important;
        background: #334155 !important;
        color: #FFFFFF !important;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #334155 !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px !important;
        border-radius: 8px 8px 0 0 !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        color: #94A3B8 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #38BDF8 !important;
        border-bottom: 2px solid #38BDF8 !important;
    }
</style>
""", unsafe_allow_html=True)


# --- Session State Management ---
if "api_key" not in st.session_state:
    st.session_state["api_key"] = os.environ.get("GEMINI_API_KEY", "")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "👋 Hello! I am **HireFlow AI**, your autonomous HR and recruitment intelligence agent. How can I help you streamline talent acquisition or employee onboarding today?"}
    ]

# Instantiate Agent
agent = HireFlowAgent(api_key=st.session_state["api_key"])


# --- Sidebar Navigation & System Meta ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-card">
        <div class="brand-icon-box">💼</div>
        <div class="brand-text-box">
            <h2 class="brand-title">HireFlow <span class="brand-accent">AI</span></h2>
            <p class="brand-subtitle">Recruitment & Onboarding Agent</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Academic Subject Badge
    st.markdown("""
    <div class="sidebar-course-card">
        <div class="course-tag">ACADEMIC COURSE PROJECT</div>
        <div class="course-name">AI Agents & Autonomous Business Operations</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Engine Mode Indicator
    if agent.is_api_active():
        st.markdown("""
        <div class="sidebar-mode-card mode-live">
            <div class="mode-badge-pill">
                <span>🤖</span>
                <span>Gemini Live API Active</span>
            </div>
            <div class="mode-subtext">Connected to Google Gemini Models</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sidebar-mode-card mode-demo">
            <div class="mode-badge-pill">
                <span>✨</span>
                <span>HireFlow Demo Engine</span>
            </div>
            <div class="mode-subtext">Zero-Setup Mode • Ready for Evaluation</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid rgba(148, 163, 184, 0.2); margin: 12px 0;'>", unsafe_allow_html=True)

    menu_options = [
        "📊 Dashboard Overview",
        "📋 Recruitment Management",
        "📄 Resume Screening",
        "🎯 Interview Assistant",
        "✉️ Communications Hub",
        "👥 Employee Management",
        "🚀 Onboarding Management",
        "🤖 AI HR Assistant (Chatbot)",
        "⚙️ Settings & System Controls"
    ]
    
    selected_page = st.radio("Navigation Menu", menu_options, index=0)

    st.markdown("<hr style='border: none; border-top: 1px solid rgba(148, 163, 184, 0.2); margin: 12px 0;'>", unsafe_allow_html=True)
    
    # Live Quick Stats in Sidebar
    metrics = db.get_dashboard_metrics()
    st.markdown("<div style='font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;'>📌 Live Pipeline Glance</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="sidebar-stats-grid">
        <div class="sidebar-stat-box">
            <span class="sidebar-stat-val">{metrics['open_jobs']}</span>
            <span class="sidebar-stat-lbl">Open Jobs</span>
        </div>
        <div class="sidebar-stat-box">
            <span class="sidebar-stat-val">{metrics['total_candidates']}</span>
            <span class="sidebar-stat-lbl">Candidates</span>
        </div>
        <div class="sidebar-stat-box">
            <span class="sidebar-stat-val">{metrics['total_employees']}</span>
            <span class="sidebar-stat-lbl">Employees</span>
        </div>
        <div class="sidebar-stat-box">
            <span class="sidebar-stat-val">{metrics['pending_tasks']}</span>
            <span class="sidebar-stat-lbl">Tasks</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid rgba(148, 163, 184, 0.2); margin: 12px 0 6px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 10.5px; color: #64748B; text-align: center;'>HireFlow AI v1.0 • Academic Build</div>", unsafe_allow_html=True)


# ==============================================================================
# PAGE 1: 📊 DASHBOARD OVERVIEW
# ==============================================================================
if selected_page == "📊 Dashboard Overview":
    st.title("📊 HR Executive Operations Dashboard")
    st.markdown("Real-time operational view of recruitment pipelines, candidate evaluations, and employee onboarding lifecycles.")

    metrics = db.get_dashboard_metrics()

    # Metric Cards Row
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Candidates</div>
            <div class="metric-value" style="color: #38BDF8;">{metrics['total_candidates']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Shortlisted</div>
            <div class="metric-value" style="color: #34D399;">{metrics['shortlisted_candidates']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Interviews</div>
            <div class="metric-value" style="color: #A78BFA;">{metrics['interviews_scheduled']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Selected</div>
            <div class="metric-value" style="color: #60A5FA;">{metrics['selected_candidates']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Employees</div>
            <div class="metric-value" style="color: #2DD4BF;">{metrics['total_employees']}</div>
        </div>
        """, unsafe_allow_html=True)
    with m6:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Pending Tasks</div>
            <div class="metric-value" style="color: #FBBF24;">{metrics['pending_tasks']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    chart_col1, chart_col2 = st.columns([1.2, 1])

    with chart_col1:
        st.markdown("### 📈 Recruitment Pipeline Funnel")
        funnel_data = pd.DataFrame([
            {"Stage": "1. Applied", "Count": metrics['total_candidates']},
            {"Stage": "2. Shortlisted", "Count": metrics['shortlisted_candidates']},
            {"Stage": "3. Interview Scheduled", "Count": metrics['interviews_scheduled']},
            {"Stage": "4. Selected", "Count": metrics['selected_candidates']},
            {"Stage": "5. Onboarded as Employee", "Count": metrics['total_employees']}
        ])
        fig_funnel = px.bar(
            funnel_data,
            x="Count",
            y="Stage",
            orientation="h",
            text="Count",
            color="Stage",
            color_discrete_sequence=["#38BDF8", "#34D399", "#A78BFA", "#60A5FA", "#FBBF24"]
        )
        fig_funnel.update_layout(
            showlegend=False,
            margin=dict(l=20, r=20, t=10, b=20),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F1F5F9", size=12),
            xaxis=dict(gridcolor="#1E293B", tickfont=dict(color="#CBD5E1")),
            yaxis=dict(tickfont=dict(color="#F1F5F9", size=12))
        )
        st.plotly_chart(fig_funnel, use_container_state=True, use_container_width=True)

    with chart_col2:
        st.markdown("### 🍩 Candidate Status Distribution")
        dist = metrics["status_distribution"]
        if dist:
            dist_df = pd.DataFrame(list(dist.items()), columns=["Status", "Count"])
            fig_pie = px.pie(
                dist_df,
                values="Count",
                names="Status",
                hole=0.45,
                color_discrete_sequence=["#38BDF8", "#34D399", "#A78BFA", "#60A5FA", "#F87171", "#FBBF24"]
            )
            fig_pie.update_layout(
                margin=dict(l=20, r=20, t=10, b=20),
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F1F5F9", size=12)
            )
            st.plotly_chart(fig_pie, use_container_state=True, use_container_width=True)
        else:
            st.info("No candidates recorded yet.")

    st.markdown("---")

    # Bottom Row: Activities & Onboarding Health
    bot_col1, bot_col2 = st.columns([1.2, 1])

    with bot_col1:
        st.markdown("### 🕒 Recent Operational Activities & Audit Log")
        activities = db.get_activities(limit=8)
        if activities:
            for act in activities:
                badge_color = "#38BDF8" if act['actor'] == "HireFlow AI Agent" else "#34D399"
                st.markdown(f"""
                <div style="background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: 600; font-size: 13.5px; color: #F1F5F9;">{act['description']}</span>
                        <div style="font-size: 11.5px; color: #94A3B8;">Timestamp: {act['timestamp']}</div>
                    </div>
                    <span style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}55; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px;">
                        {act['actor']}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No activity logs recorded.")

    with bot_col2:
        st.markdown("### 🚀 Employee Onboarding Health")
        employees = db.get_all_employees()
        if employees:
            for emp in employees:
                tasks = db.get_onboarding_tasks(emp['employee_id'])
                total_t = max(len(tasks), 1)
                completed_t = sum(1 for t in tasks if t['status'] == 'Completed')
                progress_pct = int((completed_t / total_t) * 100)

                st.markdown(f"""
                <div style="background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 14px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div>
                            <strong style="color: #F8FAFC; font-size: 14px;">{emp['name']}</strong> <span style="color: #94A3B8; font-size: 12px;">({emp['employee_id']})</span><br>
                            <span style="font-size: 12px; color: #CBD5E1;">{emp['designation']} • {emp['department']}</span>
                        </div>
                        <span style="font-weight: 800; font-size: 16px; color: #38BDF8;">{progress_pct}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(progress_pct / 100.0)
        else:
            st.info("No employees currently in onboarding.")


# ==============================================================================
# PAGE 2: 📋 RECRUITMENT MANAGEMENT
# ==============================================================================
elif selected_page == "📋 Recruitment Management":
    st.title("📋 Recruitment Management")
    st.markdown("Manage end-to-end recruitment pipelines, create AI-generated Job Descriptions, and update candidate stages.")

    tab1, tab2 = st.tabs(["💼 Job Openings & AI Generator", "👥 Candidate Pipeline Tracker"])

    # --- TAB 1: JOB OPENINGS ---
    with tab1:
        col_list, col_form = st.columns([1, 1.2])

        with col_list:
            st.markdown("### Current Active Openings")
            jobs = db.get_all_jobs()
            if jobs:
                for j in jobs:
                    with st.expander(f"📌 {j['title']} ({j['department']})", expanded=False):
                        st.markdown(f"**Experience**: {j['experience_required']}")
                        st.markdown(f"**Salary**: {j['salary_range']}")
                        st.markdown(f"**Required Skills**: `{j['skills_required']}`")
                        st.markdown(f"**Status**: `{j['status']}` | **Created**: {j['created_at']}")
                        st.markdown("---")
                        st.markdown(j['job_description'][:400] + "..." if len(j['job_description']) > 400 else j['job_description'])
            else:
                st.info("No job openings created yet.")

        with col_form:
            st.markdown("### ➕ Create Job Opening with AI Assistant")
            with st.form("create_job_form"):
                j_title = st.text_input("Job Title*", placeholder="e.g. Lead Machine Learning Engineer")
                col_dep, col_exp = st.columns(2)
                with col_dep:
                    j_dept = st.selectbox("Department*", ["Engineering", "Data & Analytics", "Product", "Human Resources", "Sales & Marketing", "Finance & Operations"])
                with col_exp:
                    j_exp = st.selectbox("Experience Required*", ["0-2 years (Entry)", "2-4 years (Mid)", "4-7 years (Senior)", "7+ years (Lead/Principal)"])

                j_skills = st.text_input("Required Skills (comma separated)*", placeholder="e.g. Python, PyTorch, Docker, MLOps, AWS")
                j_salary = st.text_input("Salary Range*", placeholder="e.g. ₹18,00,000 - ₹26,00,000 PA")

                generate_ai_jd = st.checkbox("🤖 Automatically generate professional Job Description with AI", value=True)
                submitted_draft = st.form_submit_button("Generate & Draft Opening")

            if submitted_draft:
                if not j_title or not j_skills:
                    st.error("Please fill in Job Title and Required Skills.")
                else:
                    with st.spinner("AI Agent is crafting job description..."):
                        if generate_ai_jd:
                            ai_jd = agent.generate_job_description(j_title, j_dept, j_exp, j_skills, j_salary)
                        else:
                            ai_jd = f"Job Opening for {j_title} in {j_dept}. Required skills: {j_skills}. Experience: {j_exp}."

                        st.session_state["draft_jd"] = ai_jd
                        st.session_state["draft_title"] = j_title
                        st.session_state["draft_dept"] = j_dept
                        st.session_state["draft_exp"] = j_exp
                        st.session_state["draft_skills"] = j_skills
                        st.session_state["draft_salary"] = j_salary
                        st.success("Job description generated! Review and edit below before saving.")

            # Review & Edit AI Generated JD
            if "draft_jd" in st.session_state:
                st.markdown("#### 📝 Review & Refine Generated Job Description")
                st.caption("Human-in-the-loop: Edit content as desired before saving to database.")
                edited_jd = st.text_area("Job Description Markdown", value=st.session_state["draft_jd"], height=260)

                if st.button("💾 Save Job Opening to Database", type="primary"):
                    new_id = db.create_job(
                        st.session_state["draft_title"],
                        st.session_state["draft_dept"],
                        st.session_state["draft_exp"],
                        st.session_state["draft_skills"],
                        st.session_state["draft_salary"],
                        edited_jd
                    )
                    st.success(f"Job opening #{new_id} '{st.session_state['draft_title']}' saved successfully!")
                    del st.session_state["draft_jd"]
                    st.rerun()

    # --- TAB 2: CANDIDATE PIPELINE ---
    with tab2:
        st.markdown("### 🎯 Candidate Pipeline & Status Management")

        # Search & Filters
        search_query = st.text_input(
            "🔍 Search Candidate by Name, Skill, or Email:",
            placeholder="Type a candidate name (e.g. Mary, Priya, Milkha, Rahul) or skill (e.g. Python, SQL, React, AWS)...",
            key="candidate_search_input"
        )

        f_col1, f_col2 = st.columns([1.2, 1])
        with f_col1:
            all_jobs = db.get_all_jobs()
            job_opts = {0: "All Job Openings"}
            for j in all_jobs:
                job_opts[j['id']] = f"{j['title']} ({j['department']})"
            selected_job_filter = st.selectbox("Filter by Role:", options=list(job_opts.keys()), format_func=lambda x: job_opts[x])
        with f_col2:
            status_filter = st.selectbox("Filter by Application Status:", ["All", "Applied", "Shortlisted", "Interview Scheduled", "Selected", "Rejected"])

        target_job_id = selected_job_filter if selected_job_filter != 0 else None
        candidates = db.get_all_candidates(job_id=target_job_id, status=status_filter)

        # Filter by search query
        if search_query.strip():
            sq = search_query.strip().lower()
            candidates = [
                c for c in candidates
                if sq in c['name'].lower()
                or sq in (c.get('email') or '').lower()
                or sq in (c.get('skills') or '').lower()
                or sq in (c.get('job_title') or '').lower()
                or sq in (c.get('ai_summary') or '').lower()
            ]

        if candidates:
            if search_query.strip():
                st.markdown(f"Found **{len(candidates)}** candidate(s) matching search *'{search_query}'*:")
            else:
                st.markdown(f"Found **{len(candidates)}** candidate(s):")
            for c in candidates:
                rec_badge = "badge-strong" if c['match_score'] >= 80 else ("badge-potential" if c['match_score'] >= 60 else "badge-low")
                with st.expander(f"👤 {c['name']} — {c['job_title'] or 'General'} (Score: {c['match_score']}%) — [{c['status']}]", expanded=False):
                    c_col1, c_col2 = st.columns([1.5, 1])
                    with c_col1:
                        st.markdown(f"**Email**: `{c['email']}` | **Phone**: `{c['phone']}`")
                        st.markdown(f"**Experience**: {c['experience_years']} | **Education**: {c['education']}")
                        st.markdown(f"**Extracted Skills**: `{c['skills']}`")
                        st.markdown(f"**AI Recommendation**: <span class='{rec_badge}'>{c['ai_recommendation']} ({c['match_score']}%)</span>", unsafe_allow_html=True)
                        st.markdown(f"**AI Summary**: *{c['ai_summary']}*")
                    with c_col2:
                        st.markdown("#### ⚡ Human-in-the-Loop Action")
                        current_status = c['status']
                        new_status = st.selectbox(
                            f"Update Status for {c['name']}:",
                            ["Applied", "Shortlisted", "Interview Scheduled", "Selected", "Rejected"],
                            index=["Applied", "Shortlisted", "Interview Scheduled", "Selected", "Rejected"].index(current_status),
                            key=f"status_sel_{c['id']}"
                        )
                        if st.button(f"Update Status", key=f"btn_stat_{c['id']}"):
                            db.update_candidate_status(c['id'], new_status, actor="HR Admin")
                            st.success(f"Status updated to '{new_status}'!")
                            st.rerun()

                        if c['status'] == "Selected":
                            st.info("Candidate selected! You can now register them as an employee in 'Employee Management'.")
        else:
            st.info("No candidates match the selected filters.")


# ==============================================================================
# PAGE 3: 📄 RESUME SCREENING
# ==============================================================================
elif selected_page == "📄 Resume Screening":
    st.title("📄 AI-Powered Resume Screening & Skill Matching")
    st.markdown("""
    <div class="human-loop-banner">
        <strong>🤖 Autonomous Agent Operation:</strong> HireFlow AI extracts resume text, detects candidate attributes, calculates semantic skill match scores, and highlights skill gaps. All final candidate shortlisting and rejection decisions are explicitly reserved for HR approval.
    </div>
    """, unsafe_allow_html=True)

    # 1. Select Target Job Opening
    jobs = db.get_all_jobs()
    if not jobs:
        st.warning("Please create at least one job opening in 'Recruitment Management' first.")
    else:
        job_map = {j['id']: f"{j['title']} ({j['department']}) - Req: {j['skills_required']}" for j in jobs}
        selected_job_id = st.selectbox("Select Target Job Opening for Screening:", options=list(job_map.keys()), format_func=lambda x: job_map[x])
        target_job = db.get_job_by_id(selected_job_id)

        st.markdown("---")

        # 2. Upload or Preloaded Sample Resume
        col_up, col_sample = st.columns([1.2, 1])

        uploaded_file = None
        sample_chosen = None

        with col_up:
            st.markdown("#### Option A: Upload Candidate Resume (PDF)")
            uploaded_file = st.file_uploader("Upload resume in PDF format", type=["pdf"], key="resume_uploader")

        with col_sample:
            st.markdown("#### Option B: Or Use Preloaded Sample PDF")
            sample_resumes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_resumes")
            if os.path.exists(sample_resumes_dir):
                sample_files = [f for f in os.listdir(sample_resumes_dir) if f.endswith(".pdf")]
                selected_sample = st.selectbox("Select a generated sample resume to test immediately:", ["-- None --"] + sample_files)
                if selected_sample != "-- None --":
                    sample_chosen = os.path.join(sample_resumes_dir, selected_sample)

        # Process Resume
        resume_bytes_or_path = None
        filename_label = ""
        if uploaded_file is not None:
            resume_bytes_or_path = uploaded_file.read()
            filename_label = uploaded_file.name
        elif sample_chosen is not None:
            with open(sample_chosen, "rb") as sf:
                resume_bytes_or_path = sf.read()
            filename_label = os.path.basename(sample_chosen)

        if resume_bytes_or_path:
            st.markdown("---")
            with st.spinner("Extracting text and analyzing resume with HireFlow AI..."):
                raw_text = resume_parser.extract_text_from_pdf(resume_bytes_or_path)
                candidate_info = resume_parser.extract_candidate_info(raw_text)
                screening_result = agent.screen_resume(raw_text, candidate_info, target_job)

            # Display Screening Results
            st.markdown(f"### 📋 Candidate Evaluation: **{candidate_info['name']}**")
            st.caption(f"Screened against opening: **{target_job['title']}** ({target_job['department']}) | File: `{filename_label}`")

            # Score Gauge & Overview
            res_col1, res_col2 = st.columns([1, 2])

            with res_col1:
                score = screening_result['match_score']
                badge_class = "badge-strong" if score >= 80 else ("badge-potential" if score >= 60 else "badge-low")

                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={'text': "AI Match Score", 'font': {'size': 18, 'color': '#F1F5F9'}},
                    number={'font': {'color': '#38BDF8', 'size': 38}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#94A3B8', 'tickfont': {'color': '#94A3B8'}},
                        'bar': {'color': "#38BDF8"},
                        'steps': [
                            {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.25)"},
                            {'range': [50, 75], 'color': "rgba(245, 158, 11, 0.25)"},
                            {'range': [75, 100], 'color': "rgba(34, 197, 94, 0.25)"}
                        ]
                    }
                ))
                fig_gauge.update_layout(height=240, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#F1F5F9"))
                st.plotly_chart(fig_gauge, use_container_state=True, use_container_width=True)

                st.markdown(f"<div style='text-align: center;'><span class='{badge_class}' style='font-size: 14px;'>Recommendation: {screening_result['ai_recommendation']}</span></div>", unsafe_allow_html=True)

            with res_col2:
                st.markdown("#### Extracted Candidate Details")
                st.markdown(f"**Full Name**: {candidate_info['name']}")
                st.markdown(f"**Contact**: 📧 `{candidate_info['email']}` | 📞 `{candidate_info['phone']}`")
                st.markdown(f"**Experience**: {candidate_info['experience']} | **Education**: {candidate_info['education']}")

                st.markdown("#### 🎯 Skill Gap Analysis")
                st.markdown("**Matching Skills Identified:**")
                match_skills = [s.strip() for s in screening_result['matching_skills'].split(',') if s.strip()]
                if match_skills:
                    for s in match_skills:
                        st.markdown(f"<span class='skill-pill-match'>✓ {s}</span>", unsafe_allow_html=True)
                else:
                    st.write("None identified")

                st.markdown("<br>**Missing / Gap Skills:**", unsafe_allow_html=True)
                miss_skills = [s.strip() for s in screening_result['missing_skills'].split(',') if s.strip()]
                if miss_skills:
                    for s in miss_skills:
                        st.markdown(f"<span class='skill-pill-miss'>✗ {s}</span>", unsafe_allow_html=True)
                else:
                    st.write("None (Meets all required skills)")

                st.markdown("<br>**AI Candidate Summary:**", unsafe_allow_html=True)
                st.info(screening_result['ai_summary'])

            st.markdown("---")

            # Human-in-the-Loop Save to Candidate Database
            st.markdown("#### 📥 Human Approval: Add Candidate to Pipeline")
            st.write("Review and confirm whether to register this candidate into the recruitment database.")

            col_s1, col_s2 = st.columns([1, 2])
            with col_s1:
                initial_status = st.selectbox("Assign Initial Stage:", ["Applied", "Shortlisted", "Interview Scheduled", "Rejected"], index=1 if score >= 75 else 0)
            with col_s2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ Confirm & Save to Recruitment Database", type="primary"):
                    cand_id = db.add_candidate(
                        job_id=target_job['id'],
                        name=candidate_info['name'],
                        email=candidate_info['email'],
                        phone=candidate_info['phone'],
                        experience_years=candidate_info['experience'],
                        education=candidate_info['education'],
                        skills=", ".join(candidate_info['skills']),
                        match_score=screening_result['match_score'],
                        matching_skills=screening_result['matching_skills'],
                        missing_skills=screening_result['missing_skills'],
                        ai_summary=screening_result['ai_summary'],
                        ai_recommendation=screening_result['ai_recommendation'],
                        resume_filename=filename_label
                    )
                    # If user chose a non-Applied status initially, update it
                    if initial_status != "Applied":
                        db.update_candidate_status(cand_id, initial_status, actor="HR Admin")

                    st.success(f"Candidate #{cand_id} '{candidate_info['name']}' saved to database under stage '{initial_status}'!")
                    st.balloons()


# ==============================================================================
# PAGE 4: 🎯 INTERVIEW ASSISTANT
# ==============================================================================
elif selected_page == "🎯 Interview Assistant":
    st.title("🎯 AI Interview Question Generator & Scheduler")
    st.markdown("Generate tailored technical, behavioral, and HR questions based on the candidate's profile and job role.")

    candidates = db.get_all_candidates()
    if not candidates:
        st.warning("No candidates available. Please add or screen candidates first.")
    else:
        cand_map = {c['id']: f"{c['name']} (Applied: {c['job_title'] or 'General'} - Status: {c['status']})" for c in candidates}
        selected_cand_id = st.selectbox("Select Candidate for Interview:", options=list(cand_map.keys()), format_func=lambda x: cand_map[x])
        candidate = db.get_candidate_by_id(selected_cand_id)

        col_q1, col_q2 = st.columns([1, 1.2])

        with col_q1:
            st.markdown("### Interview Configuration")
            i_round = st.selectbox("Interview Round Type:", [
                "Technical Round 1 (Foundations & Architecture)",
                "Technical Round 2 (System Design & Code Quality)",
                "Managerial & Problem Solving (STAR Method)",
                "HR & Cultural Alignment",
                "Comprehensive Evaluation"
            ])
            i_interviewer = st.text_input("Lead Interviewer Name & Title:", value="Dr. Arvind Sen (VP Analytics)" if "Data" in (candidate['job_title'] or "") else "Vikramaditya Roy (Engineering Lead)")
            i_date = st.date_input("Scheduled Date:", min_value=date.today())
            i_time = st.selectbox("Scheduled Time:", ["10:00 AM - 11:00 AM", "11:30 AM - 12:30 PM", "02:00 PM - 03:00 PM", "04:30 PM - 05:30 PM"])

            if st.button("🤖 AI Generate Interview Question Bank", type="primary"):
                with st.spinner("Generating targeted questions..."):
                    q_bank = agent.generate_interview_questions(
                        job_title=candidate['job_title'] or "Software Specialist",
                        skills=candidate['job_skills'] or candidate['skills'] or "General Domain Skills",
                        experience=candidate['experience_years'] or "3+ years",
                        round_type=i_round
                    )
                    st.session_state["generated_q_bank"] = q_bank
                    st.session_state["last_round"] = i_round

        with col_q2:
            st.markdown("### 📝 AI Question Bank & Evaluation Sheet")
            q_content = st.session_state.get("generated_q_bank", "")
            if not q_content:
                st.info("Click 'AI Generate Interview Question Bank' on the left to prepare questions.")
            else:
                editable_q = st.text_area("Review & Edit Questions Before Scheduling:", value=q_content, height=350)
                
                if st.button("📅 Confirm & Schedule Interview in Database"):
                    interview_datetime = f"{i_date.strftime('%Y-%m-%d')} at {i_time}"
                    int_id = db.schedule_interview(
                        candidate_id=candidate['id'],
                        job_id=candidate['job_id'],
                        interview_date=interview_datetime,
                        interviewer=i_interviewer,
                        round_name=i_round,
                        questions=editable_q
                    )
                    st.success(f"Interview #{int_id} confirmed for {candidate['name']} on {interview_datetime} with {i_interviewer}!")
                    st.info("Candidate status has been automatically updated to 'Interview Scheduled'.")

        st.markdown("---")
        st.markdown("### 📋 Scheduled Interviews History")
        interviews = db.get_all_interviews()
        if interviews:
            int_df = pd.DataFrame([
                {
                    "Candidate": i['candidate_name'],
                    "Role": i['job_title'],
                    "Date & Time": i['interview_date'],
                    "Interviewer": i['interviewer'],
                    "Round": i['round'],
                    "Status": i['status']
                } for i in interviews
            ])
            st.dataframe(int_df, use_container_width=True)
        else:
            st.write("No interviews scheduled yet.")


# ==============================================================================
# PAGE 5: ✉️ COMMUNICATIONS HUB
# ==============================================================================
elif selected_page == "✉️ Communications Hub":
    st.title("✉️ Automated Recruitment Email Generator")
    st.markdown("""
    <div class="human-loop-banner">
        <strong>🔒 Human Approval Required:</strong> AI assists in generating personalized drafts based on candidate data and job roles. No communication is dispatched without direct human review and approval.
    </div>
    """, unsafe_allow_html=True)

    candidates = db.get_all_candidates()
    if not candidates:
        st.warning("No candidates available.")
    else:
        col_cfg, col_preview = st.columns([1, 1.3])

        with col_cfg:
            st.markdown("### 1. Select Recipient & Template")
            cand_map = {c['id']: f"{c['name']} ({c['job_title'] or 'General'} - Current: {c['status']})" for c in candidates}
            selected_cand_id = st.selectbox("Recipient Candidate:", options=list(cand_map.keys()), format_func=lambda x: cand_map[x])
            candidate = db.get_candidate_by_id(selected_cand_id)

            email_type = st.selectbox("Communication Purpose:", [
                "Application Acknowledgement",
                "Shortlisting Notification",
                "Interview Invitation",
                "Selection & Offer Confirmation",
                "Polite Rejection Notification"
            ])
            company_name = st.text_input("Company Name:", value="HireFlow AI Corp")
            extra_notes = st.text_area("Optional Specific Notes (e.g. meeting link, dates):", placeholder="e.g. Meeting link: https://meet.google.com/xyz-abc")

            if st.button("🤖 Generate Personalized Email Draft", type="primary"):
                with st.spinner("AI drafting personalized communication..."):
                    draft = agent.generate_email_draft(
                        email_type=email_type,
                        candidate_name=candidate['name'],
                        job_title=candidate['job_title'] or "Specialist",
                        company_name=company_name,
                        extra_notes=extra_notes
                    )
                    st.session_state["email_subject"] = draft["subject"]
                    st.session_state["email_body"] = draft["body"]
                    st.session_state["email_type_chosen"] = email_type

        with col_preview:
            st.markdown("### 2. HR Review & Approval")
            subj = st.session_state.get("email_subject", "")
            body = st.session_state.get("email_body", "")

            if not subj and not body:
                st.info("Select a candidate and purpose on the left, then click 'Generate Personalized Email Draft'.")
            else:
                edit_subj = st.text_input("Subject Line:", value=subj)
                edit_body = st.text_area("Email Body:", value=body, height=300)

                st.markdown("---")
                approval = st.checkbox("✅ I have reviewed this email draft and authorize sending.")

                if st.button("🚀 Approve & Record Communication", disabled=not approval):
                    db.log_activity("EMAIL_DRAFTED", f"Dispatched '{st.session_state.get('email_type_chosen', 'Email')}' to {candidate['name']} ({candidate['email']})", actor="HR Admin")
                    st.success(f"Email successfully approved and logged for {candidate['name']}!")
                    st.balloons()


# ==============================================================================
# PAGE 6: 👥 EMPLOYEE MANAGEMENT
# ==============================================================================
elif selected_page == "👥 Employee Management":
    st.title("👥 Employee Management & Conversion")
    st.markdown("Convert selected candidates into active employee records and manage organization personnel.")

    tab_conv, tab_dir = st.tabs(["🎉 Convert Selected Candidate to Employee", "📋 Employee Directory"])

    with tab_conv:
        st.markdown("### 🌟 Convert Selected Candidate into Employee")
        # Find candidates who are 'Selected' or any candidate
        all_cands = db.get_all_candidates()
        selected_candidates = [c for c in all_cands if c['status'] == "Selected"]

        if not selected_candidates:
            st.info("No candidates currently have the 'Selected' status. You can mark a candidate as 'Selected' in the Recruitment Management tab, or choose from all candidates below:")
            cand_choices = all_cands
        else:
            cand_choices = selected_candidates

        if not cand_choices:
            st.warning("No candidates found in database.")
        else:
            c_opts = {c['id']: f"{c['name']} (Role: {c['job_title'] or 'General'} - Status: {c['status']})" for c in cand_choices}
            chosen_cand_id = st.selectbox("Select Candidate to Register as Employee:", options=list(c_opts.keys()), format_func=lambda x: c_opts[x])
            c_data = db.get_candidate_by_id(chosen_cand_id)

            with st.form("employee_registration_form"):
                st.markdown(f"#### Employee Profile Details for **{c_data['name']}**")
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    e_name = st.text_input("Full Name*", value=c_data['name'])
                    e_email = st.text_input("Corporate Email*", value=f"{c_data['name'].lower().replace(' ', '.')}@hireflow.internal")
                    e_dept = st.text_input("Department*", value=c_data['job_department'] or "Engineering")
                with col_e2:
                    e_desig = st.text_input("Designation / Title*", value=c_data['job_title'] or "Associate")
                    e_manager = st.text_input("Reporting Manager*", value="Meera Kapoor (Director of Engineering)")
                    e_date = st.date_input("Official Joining Date*", min_value=date.today())

                st.markdown("---")
                st.caption("Automatic Action: Registering this employee will initialize their onboarding checklist and document compliance records in SQLite.")
                reg_submitted = st.form_submit_button("🎉 Register Employee & Initialize Onboarding", type="primary")

                if reg_submitted:
                    new_emp_id = db.register_employee(
                        candidate_id=c_data['id'],
                        name=e_name,
                        email=e_email,
                        department=e_dept,
                        designation=e_desig,
                        joining_date=e_date.strftime("%Y-%m-%d"),
                        reporting_manager=e_manager
                    )
                    st.success(f"Employee {e_name} successfully registered with ID: **{new_emp_id}**!")
                    st.balloons()

    with tab_dir:
        st.markdown("### 🏢 Current Employee Directory")
        employees = db.get_all_employees()
        if employees:
            emp_search = st.text_input("🔍 Search Employee by Name, ID, or Department:", placeholder="e.g. Ananya, EMP-2026, HR, Engineering...", key="emp_dir_search")
            if emp_search.strip():
                es = emp_search.strip().lower()
                employees = [e for e in employees if es in e['name'].lower() or es in e['employee_id'].lower() or es in e['department'].lower() or es in e['designation'].lower()]
            emp_df = pd.DataFrame([
                {
                    "Employee ID": e['employee_id'],
                    "Name": e['name'],
                    "Email": e['email'],
                    "Department": e['department'],
                    "Designation": e['designation'],
                    "Joining Date": e['joining_date'],
                    "Reporting Manager": e['reporting_manager'],
                    "Status": e['status']
                } for e in employees
            ])
            st.dataframe(emp_df, use_container_width=True)
        else:
            st.info("No employees registered yet.")


# ==============================================================================
# PAGE 7: 🚀 ONBOARDING MANAGEMENT
# ==============================================================================
elif selected_page == "🚀 Onboarding Management":
    st.title("🚀 Employee Onboarding Management")
    st.markdown("Track document submission compliance, manage IT & HR onboarding tasks, and access the AI Onboarding Assistant.")

    employees = db.get_all_employees()
    if not employees:
        st.warning("No employees currently registered. Register an employee in 'Employee Management' first.")
    else:
        emp_map = {e['employee_id']: f"{e['name']} ({e['employee_id']} - {e['designation']} - {e['department']})" for e in employees}
        selected_emp_id = st.selectbox("Select Employee to Manage Onboarding:", options=list(emp_map.keys()), format_func=lambda x: emp_map[x])
        emp = db.get_employee_by_id(selected_emp_id)

        # Onboarding Progress Overview
        tasks = db.get_onboarding_tasks(selected_emp_id)
        docs = db.get_documents_for_employee(selected_emp_id)

        total_items = max(len(tasks) + len(docs), 1)
        completed_items = sum(1 for t in tasks if t['status'] == 'Completed') + sum(1 for d in docs if d['status'] == 'Verified')
        progress_pct = int((completed_items / total_items) * 100)

        st.markdown(f"#### Onboarding Completion Meter: **{progress_pct}%**")
        st.progress(progress_pct / 100.0)

        st.markdown("---")

        ob_tab1, ob_tab2, ob_tab3 = st.tabs(["📑 Document Compliance Checklist", "📋 Onboarding Task Tracker", "🤖 AI Welcome Kit & Policy FAQ"])

        # TAB 1: DOCUMENTS
        with ob_tab1:
            st.markdown(f"### Required Documents for {emp['name']}")
            st.caption("Verify and record status of employee compliance documents (Sample documents used; no sensitive personal data stored).")

            if docs:
                for d in docs:
                    d_col1, d_col2, d_col3, d_col4 = st.columns([2, 1.2, 1.5, 1])
                    with d_col1:
                        st.markdown(f"**{d['document_name']}**")
                        st.caption(f"Last updated: {d['updated_at']}")
                    with d_col2:
                        status_options = ["Pending", "Submitted", "Verified", "Rejected"]
                        curr_idx = status_options.index(d['status']) if d['status'] in status_options else 0
                        new_d_stat = st.selectbox("Status", status_options, index=curr_idx, key=f"doc_stat_{d['id']}")
                    with d_col3:
                        new_notes = st.text_input("HR Notes", value=d['notes'] or "", key=f"doc_notes_{d['id']}")
                    with d_col4:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Update", key=f"doc_btn_{d['id']}"):
                            db.update_document_status(d['id'], new_d_stat, new_notes)
                            st.success(f"Updated {d['document_name']}")
                            st.rerun()
                    st.markdown("<hr style='margin: 4px 0 10px 0;'>", unsafe_allow_html=True)
            else:
                st.info("No documents initialized for this employee.")

        # TAB 2: TASKS
        with ob_tab2:
            st.markdown(f"### Onboarding Checklist for {emp['name']}")
            if tasks:
                for t in tasks:
                    t_col1, t_col2, t_col3 = st.columns([2, 1, 1])
                    with t_col1:
                        icon = "✅" if t['status'] == "Completed" else "⏳"
                        st.markdown(f"**{icon} {t['task_name']}**")
                        st.caption(f"Category: `{t['category']}` | Due Date: `{t['due_date']}`")
                    with t_col2:
                        t_opts = ["Pending", "In Progress", "Completed"]
                        t_idx = t_opts.index(t['status']) if t['status'] in t_opts else 0
                        new_t_stat = st.selectbox("Task Status", t_opts, index=t_idx, key=f"task_stat_{t['id']}")
                    with t_col3:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Save", key=f"task_btn_{t['id']}"):
                            db.update_onboarding_task(t['id'], new_t_stat)
                            st.success(f"Task updated to {new_t_stat}")
                            st.rerun()
                    st.markdown("<hr style='margin: 4px 0 10px 0;'>", unsafe_allow_html=True)
            else:
                st.info("No tasks recorded.")

        # TAB 3: AI ASSISTANT & WELCOME
        with ob_tab3:
            st.markdown("### 🌟 AI Onboarding Assistant & Policy Guide")
            col_w1, col_w2 = st.columns([1, 1.2])

            with col_w1:
                st.markdown("#### 1. Generate Welcome Letter & Roadmap")
                if st.button("🤖 Generate Welcome Kit with AI", type="primary"):
                    welcome_doc = agent.generate_onboarding_welcome(
                        name=emp['name'],
                        designation=emp['designation'],
                        department=emp['department'],
                        manager=emp['reporting_manager'],
                        joining_date=emp['joining_date']
                    )
                    st.session_state["welcome_doc"] = welcome_doc

                if "welcome_doc" in st.session_state:
                    st.markdown(st.session_state["welcome_doc"])

            with col_w2:
                st.markdown("#### 2. HR Policy FAQ & Employee Guide")
                st.caption("Ask questions about leaves, working hours, probation, health insurance, and conduct.")

                # Quick Question Pills
                pill_col1, pill_col2 = st.columns(2)
                quick_query = None
                with pill_col1:
                    if st.button("🌴 Leave Policy Details"):
                        quick_query = "What is the annual leave and sick leave policy?"
                    if st.button("🏥 Medical Insurance"):
                        quick_query = "What are the health and insurance benefits?"
                with pill_col2:
                    if st.button("⏰ Working Hours & Hybrid"):
                        quick_query = "What are the working hours and hybrid work policies?"
                    if st.button("⏳ Probation Guidelines"):
                        quick_query = "How long is probation and when is confirmation?"

                custom_query = st.text_input("Or enter an HR policy question:", placeholder="e.g. When is monthly salary credited?")
                q_to_run = custom_query or quick_query

                if q_to_run:
                    with st.spinner("AI Onboarding Assistant retrieving policy answers..."):
                        answer = agent.answer_onboarding_faq(q_to_run)
                        st.markdown(answer)


# ==============================================================================
# PAGE 8: 🤖 AI HR ASSISTANT (CHATBOT)
# ==============================================================================
elif selected_page == "🤖 AI HR Assistant (Chatbot)":
    st.title("🤖 HireFlow AI HR Copilot")
    st.markdown("An interactive AI HR agent capable of analyzing recruitment pipelines, generating HR artifacts, and answering policy queries.")

    # Quick Prompt Pills
    st.markdown("##### 💡 Suggested Quick Prompts:")
    p_col1, p_col2, p_col3 = st.columns(3)
    prompt_clicked = None
    with p_col1:
        if st.button("📊 Show recruitment pipeline summary"):
            prompt_clicked = "Show current recruitment pipeline summary and applicant counts."
        if st.button("📝 Create JD for Business Analyst"):
            prompt_clicked = "Create a job description for a Business Analyst in Analytics department."
    with p_col2:
        if st.button("🎯 Interview questions for Python Dev"):
            prompt_clicked = "Generate interview questions for Senior Python Developer."
        if st.button("🌴 Explain company leave policy"):
            prompt_clicked = "What is the company leave policy for new employees?"
    with p_col3:
        if st.button("🚀 Prepare onboarding checklist"):
            prompt_clicked = "Prepare an onboarding checklist for a new software engineer."
        if st.button("👥 Show shortlisted candidates"):
            prompt_clicked = "Show all shortlisted candidates and their match scores."

    st.markdown("---")

    # Display Chat History
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # Chat Input
    user_input = st.chat_input("Ask HireFlow AI anything regarding recruitment, candidates, or onboarding...") or prompt_clicked

    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("HireFlow AI is reasoning..."):
                current_metrics = db.get_dashboard_metrics()
                agent_reply = agent.chat_with_agent(
                    user_msg=user_input,
                    chat_history=st.session_state["messages"],
                    db_summary=current_metrics
                )
                st.markdown(agent_reply)
                st.session_state["messages"].append({"role": "assistant", "content": agent_reply})


# ==============================================================================
# PAGE 9: ⚙️ SETTINGS & SYSTEM CONTROLS
# ==============================================================================
elif selected_page == "⚙️ Settings & System Controls":
    st.title("⚙️ System Configuration & Diagnostics")
    st.markdown("Manage AI engine credentials, view architecture specifications, and reset database states.")

    col_set1, col_set2 = st.columns([1, 1])

    with col_set1:
        st.markdown("### 🤖 Google Gemini API Configuration")
        curr_key = st.session_state.get("api_key", "")
        masked_key = f"{curr_key[:6]}...{curr_key[-4:]}" if len(curr_key) > 10 else "Not Configured"
        st.write(f"Current Status: **{masked_key}**")

        new_key = st.text_input("Enter Google Gemini API Key:", type="password", placeholder="AIzaSy...")
        if st.button("Save API Key"):
            st.session_state["api_key"] = new_key.strip()
            os.environ["GEMINI_API_KEY"] = new_key.strip()
            st.success("API Key updated for this session!")
            st.rerun()

        st.markdown("---")
        st.markdown("### 🔄 Database Reset & Reseed")
        st.write("Reset SQLite database to original sample candidates, job openings, and onboarding tasks for testing.")
        if st.button("⚠️ Reset & Reseed Demo Data", type="secondary"):
            db.reset_and_reseed_db()
            st.success("Database reset and reseeded with realistic demo data!")
            st.rerun()

    with col_set2:
        st.markdown("### 🎓 Academic Project Information")
        st.markdown("""
        <div style="background: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 18px;">
            <h4 style="margin-top: 0; color: #38BDF8; font-weight: 700;">HireFlow AI Architecture</h4>
            <p style="font-size: 13px; color: #CBD5E1; line-height: 1.6;">
                <strong style="color: #F8FAFC;">Subject</strong>: AI Agents & Autonomous Business Operations<br>
                <strong style="color: #F8FAFC;">Architecture</strong>: Autonomous HR Agent with Human-in-the-Loop Controls<br>
                <strong style="color: #F8FAFC;">Frontend</strong>: Streamlit (Custom Responsive Dark SaaS CSS)<br>
                <strong style="color: #F8FAFC;">Data Layer</strong>: SQLite relational tables (Candidates, Jobs, Employees, Documents, Tasks, Activities)<br>
                <strong style="color: #F8FAFC;">Resume Engine</strong>: PDFPlumber / PyPDF2 parsing pipeline<br>
                <strong style="color: #F8FAFC;">Visualizations</strong>: Plotly Interactive Funnels and Distribution charts<br>
                <strong style="color: #F8FAFC;">LLM Integration</strong>: Gemini REST API + Fallback Deterministic Reasoning Engine
            </p>
            <div style="background: rgba(30, 58, 138, 0.3); border-left: 3px solid #38BDF8; padding: 10px 12px; font-size: 12px; color: #E0F2FE; margin-top: 10px; border-radius: 6px;">
                💡 <strong style="color: #38BDF8;">Core Principle:</strong> AI agents automate mundane extraction, semantic matching, and communication drafting, while high-stakes decisions (shortlisting, hiring, document approval) remain firmly under human oversight.
            </div>
        </div>
        """, unsafe_allow_html=True)

