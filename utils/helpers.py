"""
utils/helpers.py
Shared utilities: CSS injection, chart theme, data loaders with error handling.
"""

import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go

# ── Constants ─────────────────────────────────────────────────────────────────

WATCHLIST = ["NBTX", "IONS", "CYTK", "GRAL", "CDNA", "CTMX", "GPCR", "IDYA", "NRIX"]

CHART_COLORS = {
    "primary":   "#58a6ff",
    "red":       "#f78166",
    "purple":    "#d2a8ff",
    "green":     "#7ee787",
    "yellow":    "#e3b341",
    "orange":    "#ffa657",
    "teal":      "#39d353",
    "pink":      "#f778ba",
    "white":     "#e6edf3",
    "muted":     "#8b949e",
}

TICKER_COLORS = {
    "NBTX": "#58a6ff",
    "IONS": "#d2a8ff",
    "CYTK": "#7ee787",
    "GRAL": "#ffa657",
    "CDNA": "#f778ba",
    "CTMX": "#f78166",
    "GPCR": "#39d353",
    "IDYA": "#e3b341",
    "NRIX": "#79c0ff",
}

CATALYST_TYPE_COLORS = {
    "clinical":    "#58a6ff",
    "regulatory":  "#7ee787",
    "earnings":    "#e3b341",
    "partnership": "#d2a8ff",
    "commercial":  "#ffa657",
}

IMPORTANCE_LABELS = {1: "Low", 2: "Moderate", 3: "Notable", 4: "High", 5: "Critical"}

BASE_BG    = "#0d1117"
PANEL_BG   = "#161b22"
BORDER_CLR = "#30363d"
GRID_CLR   = "#21262d"
TEXT_DIM   = "#8b949e"
TEXT_MAIN  = "#c9d1d9"
TEXT_BRIGHT= "#e6edf3"


# ── CSS ───────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {BASE_BG}; color: {TEXT_BRIGHT}; }}
        [data-testid="stSidebar"] {{ background-color: {PANEL_BG}; border-right: 1px solid {BORDER_CLR}; }}
        [data-testid="metric-container"] {{
            background: {PANEL_BG};
            border: 1px solid {BORDER_CLR};
            border-radius: 8px;
            padding: 16px;
        }}
        [data-testid="metric-container"] label {{
            color: {TEXT_DIM} !important;
            font-size: 12px !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        [data-testid="metric-container"] [data-testid="stMetricValue"] {{
            color: {CHART_COLORS["primary"]} !important;
            font-size: 28px !important;
            font-weight: 700;
        }}
        h1 {{ color: {TEXT_BRIGHT} !important; font-weight: 700; letter-spacing: -0.02em; }}
        h2, h3 {{ color: {TEXT_MAIN} !important; }}
        [data-testid="stDataFrame"] {{ border: 1px solid {BORDER_CLR}; border-radius: 8px; }}
        .ticker-badge {{
            display: inline-block;
            background: #1f6feb22;
            border: 1px solid #1f6feb;
            color: {CHART_COLORS["primary"]};
            border-radius: 4px;
            padding: 2px 8px;
            font-family: monospace;
            font-weight: 700;
            font-size: 13px;
        }}
        .section-label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: {TEXT_DIM};
            margin-bottom: 4px;
        }}
        .thesis-card {{
            background: {PANEL_BG};
            border: 1px solid {BORDER_CLR};
            border-left: 3px solid {CHART_COLORS["primary"]};
            border-radius: 6px;
            padding: 16px 20px;
            margin-top: 8px;
            line-height: 1.6;
            color: {TEXT_MAIN};
        }}
        .bull-card {{
            background: #0f291e;
            border: 1px solid #238636;
            border-radius: 6px;
            padding: 14px 18px;
            margin-top: 8px;
            line-height: 1.6;
            color: #7ee787;
        }}
        .bear-card {{
            background: #2d1117;
            border: 1px solid #6e1c1c;
            border-radius: 6px;
            padding: 14px 18px;
            margin-top: 8px;
            line-height: 1.6;
            color: #f78166;
        }}
        .risk-card {{
            background: {PANEL_BG};
            border: 1px solid #e3b341;
            border-left: 3px solid #e3b341;
            border-radius: 6px;
            padding: 14px 18px;
            margin-top: 8px;
            line-height: 1.6;
            color: {TEXT_MAIN};
        }}
        .perf-callout {{
            background: #0f291e;
            border: 1px solid #238636;
            border-radius: 8px;
            padding: 12px 16px;
            color: #3fb950;
            font-weight: 600;
        }}
        .info-pill {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 6px;
        }}
        .stSelectbox label {{ color: {TEXT_DIM} !important; font-size: 12px !important; }}
        .stMultiSelect label {{ color: {TEXT_DIM} !important; font-size: 12px !important; }}
        .stRadio label {{ color: {TEXT_MAIN} !important; }}
    </style>
    """, unsafe_allow_html=True)


# ── Chart theme helper ────────────────────────────────────────────────────────

def chart_layout(height=380, legend=True, hovermode="x unified", margin=None):
    """Return a standard dark plotly layout dict."""
    m = margin or dict(l=0, r=0, t=30, b=0)
    layout = dict(
        plot_bgcolor=BASE_BG,
        paper_bgcolor=BASE_BG,
        font=dict(color=TEXT_DIM),
        xaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=TEXT_DIM), showline=False),
        yaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=TEXT_DIM)),
        margin=m,
        height=height,
        hovermode=hovermode,
    )
    if legend:
        layout["legend"] = dict(
            orientation="h", y=1.08,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT_MAIN)
        )
    return layout


# ── Data loaders ─────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _path(filename):
    return os.path.join(DATA_DIR, filename)


@st.cache_data
def load_excel_data():
    """Load backtest stats, index series, drawdown, factor data, and prices from data.xlsx."""
    fpath = _path("data.xlsx")
    if not os.path.exists(fpath):
        st.error("data.xlsx not found in /data folder.")
        return None, None, None, None, None

    xl = pd.ExcelFile(fpath)
    raw = pd.read_excel(xl, "Backtest", header=None)

    # Summary stats table
    stats_df = raw.iloc[2:7, 0:6].copy()
    stats_df.columns = stats_df.iloc[0]
    stats_df = stats_df[1:].reset_index(drop=True)
    stats_df.columns.name = None

    # Cumulative index series
    idx_df = raw.iloc[2:, 7:12].copy()
    idx_df.columns = idx_df.iloc[0]
    idx_df = idx_df[1:].dropna(subset=["Month"]).reset_index(drop=True)
    idx_df.columns.name = None
    idx_df["Month"] = pd.to_datetime(idx_df["Month"].astype(str))
    for c in ["Watchlist Index", "XBI Index", "IBB Index", "SPY Index"]:
        idx_df[c] = pd.to_numeric(idx_df[c], errors="coerce")

    # Drawdown series
    dd_df = raw.iloc[2:, 13:18].copy()
    dd_df.columns = dd_df.iloc[0]
    dd_df = dd_df[1:].dropna(subset=["Month"]).reset_index(drop=True)
    dd_df.columns.name = None
    dd_df["Month"] = pd.to_datetime(dd_df["Month"].astype(str))
    for c in ["Watchlist DD", "XBI DD", "IBB DD", "SPY DD"]:
        dd_df[c] = pd.to_numeric(dd_df[c], errors="coerce")

    factor = pd.read_excel(xl, "Factor_Data")

    prices = pd.read_excel(xl, "Monthly_Prices")
    prices["Month"] = pd.to_datetime(prices["Month"].astype(str))

    return stats_df, idx_df, dd_df, factor, prices


@st.cache_data
def load_catalysts():
    """Load catalyst calendar from data/catalysts.csv."""
    fpath = _path("catalysts.csv")
    if not os.path.exists(fpath):
        st.warning("catalysts.csv not found. Add it to the /data folder.")
        return pd.DataFrame()
    df = pd.read_csv(fpath, on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    required = ["ticker", "company", "catalyst", "catalyst_type",
                "expected_timing", "quarter", "importance", "bull_impact", "bear_risk"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"catalysts.csv missing columns: {missing}")
        return pd.DataFrame()
    df["importance"] = pd.to_numeric(df["importance"], errors="coerce").fillna(3).astype(int)
    return df


@st.cache_data
def load_theses():
    """Load company theses from data/theses.json."""
    fpath = _path("theses.json")
    if not os.path.exists(fpath):
        st.warning("theses.json not found. Add it to the /data folder.")
        return {}
    with open(fpath, "r") as f:
        return json.load(f)


@st.cache_data
def load_pipeline():
    """Load pipeline database from data/pipeline.csv."""
    fpath = _path("pipeline.csv")
    if not os.path.exists(fpath):
        st.warning("pipeline.csv not found. Add it to the /data folder.")
        return pd.DataFrame()
    df = pd.read_csv(fpath, on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    return df


@st.cache_data
def load_scores():
    """Load factor scores from data/scores.csv. Calculates total_score."""
    fpath = _path("scores.csv")
    if not os.path.exists(fpath):
        st.warning("scores.csv not found. Add it to the /data folder.")
        return pd.DataFrame()
    df = pd.read_csv(fpath, on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    score_cols = ["analyst", "quality", "growth", "balance_sheet",
                  "valuation", "capital_allocation", "pipeline", "platform", "dilution_penalty"]
    for c in score_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    # Weighted total: average positive scores + dilution penalty
    pos_cols = [c for c in score_cols if c != "dilution_penalty"]
    df["total_score"] = df[pos_cols].mean(axis=1).round(1) + df["dilution_penalty"]
    return df
