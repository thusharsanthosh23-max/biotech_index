"""
app.py — Biotech Intelligence Dashboard
Entry point. All page logic lives in /pages/. Shared utils in /utils/.
Data files: /data/data.xlsx, catalysts.csv, theses.json, pipeline.csv, scores.csv
"""

import sys
import os

# Ensure local modules are importable when running from repo root
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.helpers import inject_css, load_excel_data, WATCHLIST, TICKER_COLORS, chart_layout, TEXT_DIM, TEXT_MAIN

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Biotech Intelligence Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧬 Biotech Index")
    st.markdown("<div class='section-label'>Navigation</div>", unsafe_allow_html=True)

    page = st.radio("", [
        "📊 Dashboard",
        "📈 Index Performance",
        "🏢 Holdings",
        "📅 Catalyst Calendar",
        "🔬 Company Deep Dive",
        "🧪 Pipeline",
        "⭐ Score Breakdown",
        "📋 Methodology",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<div class='section-label'>Backtest Period</div>", unsafe_allow_html=True)
    st.markdown("Jun 2024 – Jun 2026")
    st.markdown("<div class='section-label' style='margin-top:12px'>Universe</div>", unsafe_allow_html=True)
    st.markdown("9 stocks · Equal weight · Monthly rebalanced")
    st.markdown("<div class='section-label' style='margin-top:12px'>Benchmarks</div>", unsafe_allow_html=True)
    st.markdown("XBI · IBB · SPY")


# ── Page routing ──────────────────────────────────────────────────────────────

if page == "📊 Dashboard":
    from pages import dashboard
    dashboard.render()

elif page == "📈 Index Performance":
    from pages import index_performance
    index_performance.render()

elif page == "🏢 Holdings":
    from pages import holdings
    holdings.render()

elif page == "📅 Catalyst Calendar":
    from pages import catalyst_calendar
    catalyst_calendar.render()

elif page == "🔬 Company Deep Dive":
    from pages import company_thesis
    company_thesis.render()

elif page == "🧪 Pipeline":
    from pages import pipeline
    pipeline.render()

elif page == "⭐ Score Breakdown":
    from pages import scores
    scores.render()

elif page == "📋 Methodology":
    from pages import methodology
    methodology.render()
