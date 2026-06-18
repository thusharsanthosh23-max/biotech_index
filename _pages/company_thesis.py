"""
pages/company_thesis.py
Company Thesis Pages — dropdown-based deep-dive per ticker.
Data lives in data/theses.json — edit that file to update content.
"""

import streamlit as st
import pandas as pd
from utils.helpers import (
    load_theses, load_scores, load_catalysts, load_excel_data,
    WATCHLIST, TICKER_COLORS, chart_layout,
    TEXT_DIM, TEXT_MAIN, BORDER_CLR, PANEL_BG, BASE_BG
)
import plotly.graph_objects as go


def _score_radar(row):
    """Build a radar chart for a single company's factor scores."""
    categories = ["Analyst", "Quality", "Growth", "Balance Sheet",
                  "Valuation", "Cap Alloc", "Pipeline", "Platform"]
    values = [
        row.get("analyst", 0),
        row.get("quality", 0),
        row.get("growth", 0),
        row.get("balance_sheet", 0),
        row.get("valuation", 0),
        row.get("capital_allocation", 0),
        row.get("pipeline", 0),
        row.get("platform", 0),
    ]
    color = TICKER_COLORS.get(row.get("ticker", ""), "#58a6ff")

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor=color.replace("#", "rgba(") + "22)" if color.startswith("#") else color,
        line=dict(color=color, width=2),
        name=row.get("ticker", ""),
    ))
    # Build fill color with transparency
    hex_color = color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    fig.update_traces(fillcolor=f"rgba({r},{g},{b},0.15)")

    layout = chart_layout(height=320, legend=False, hovermode="closest")
    layout["polar"] = dict(
        bgcolor=PANEL_BG,
        radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363d", tickfont=dict(color=TEXT_DIM)),
        angularaxis=dict(gridcolor="#30363d", tickfont=dict(color=TEXT_MAIN)),
    )
    fig.update_layout(**layout)
    return fig


def render():
    st.title("Company Deep Dive")
    st.markdown(
        "<p style='color:#8b949e;margin-top:-12px'>Investment thesis, bull/bear case, and score breakdown per ticker · Edit data/theses.json to update</p>",
        unsafe_allow_html=True
    )

    theses = load_theses()
    scores_df = load_scores()
    catalysts_df = load_catalysts()
    _, _, _, _, prices = load_excel_data()

    if not theses:
        st.info("No thesis data found. Add entries to data/theses.json.")
        return

    # ── Ticker selector ────────────────────────────────────────────────────
    ticker_options = [t for t in WATCHLIST if t in theses]
    ticker = st.selectbox(
        "Select Company",
        ticker_options,
        format_func=lambda t: f"{t} — {theses[t]['name']}"
    )

    data = theses[ticker]
    color = TICKER_COLORS.get(ticker, "#58a6ff")
    hex_color = color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # ── Header ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">
        <span class='ticker-badge' style="font-size:16px;padding:4px 12px">{ticker}</span>
        <span style="color:{color};font-size:14px;font-weight:600">{data.get('theme','')}</span>
    </div>
    <h2 style="margin-top:4px">{data.get('name','')}</h2>
    """, unsafe_allow_html=True)

    # ── Why it's in the index ──────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:rgba({r},{g},{b},0.08);border:1px solid rgba({r},{g},{b},0.3);
                border-radius:6px;padding:12px 16px;margin-bottom:16px">
        <div style="font-size:11px;text-transform:uppercase;color:{color};letter-spacing:0.08em;margin-bottom:4px">
            Why it's in the index
        </div>
        <div style="color:{TEXT_MAIN};line-height:1.6">{data.get('why_in_index','')}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Thesis / Bull / Bear / Risks ───────────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("**Investment Thesis**")
        st.markdown(f"<div class='thesis-card'>{data.get('thesis','')}</div>", unsafe_allow_html=True)

        st.markdown("<br>**Key Risks**", unsafe_allow_html=True)
        st.markdown(f"<div class='risk-card'>{data.get('key_risks','')}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("**Bull Case**")
        st.markdown(f"<div class='bull-card'>{data.get('bull_case','')}</div>", unsafe_allow_html=True)

        st.markdown("<br>**Bear Case**", unsafe_allow_html=True)
        st.markdown(f"<div class='bear-card'>{data.get('bear_case','')}</div>", unsafe_allow_html=True)

    # ── Recent Developments ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Recent Developments**")
    st.markdown(f"<div class='thesis-card'>{data.get('recent_developments','')}</div>", unsafe_allow_html=True)

    # ── Score radar ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Factor Score Breakdown")

    if not scores_df.empty:
        score_row = scores_df[scores_df["ticker"] == ticker]
        if not score_row.empty:
            row = score_row.iloc[0].to_dict()
            col_radar, col_metrics = st.columns([1, 1])
            with col_radar:
                fig = _score_radar(row)
                st.plotly_chart(fig, use_container_width=True)
            with col_metrics:
                score_cols = {
                    "Analyst":           "analyst",
                    "Quality":           "quality",
                    "Growth":            "growth",
                    "Balance Sheet":     "balance_sheet",
                    "Valuation":         "valuation",
                    "Capital Allocation":"capital_allocation",
                    "Pipeline":          "pipeline",
                    "Platform":          "platform",
                }
                st.markdown(f"<p style='color:{TEXT_DIM};font-size:13px'>Total Score: <b style='color:{color}'>{row.get('total_score','—'):.1f}</b> / 100</p>", unsafe_allow_html=True)
                for label, key in score_cols.items():
                    val = int(row.get(key, 0))
                    bar_width = val
                    st.markdown(f"""
                    <div style="margin-bottom:6px">
                        <div style="display:flex;justify-content:space-between;font-size:12px;color:{TEXT_DIM};margin-bottom:2px">
                            <span>{label}</span><span style="color:{TEXT_MAIN}">{val}</span>
                        </div>
                        <div style="background:#21262d;border-radius:3px;height:6px">
                            <div style="background:{color};width:{bar_width}%;height:6px;border-radius:3px"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                dp = int(row.get("dilution_penalty", 0))
                st.markdown(f"""
                <div style="margin-top:8px;padding:8px 12px;background:#2d1117;border:1px solid #6e1c1c;border-radius:4px;font-size:12px;color:#f78166">
                    Dilution Penalty: {dp}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No score data found for this ticker. Add a row to data/scores.csv.")
    else:
        st.info("scores.csv not found or empty.")

    # ── Upcoming Catalysts ────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Upcoming Catalysts")

    if not catalysts_df.empty:
        ticker_cats = catalysts_df[catalysts_df["ticker"] == ticker].sort_values("importance", ascending=False)
        if ticker_cats.empty:
            st.info("No catalysts found for this ticker.")
        else:
            for _, row_c in ticker_cats.iterrows():
                from utils.helpers import CATALYST_TYPE_COLORS, IMPORTANCE_LABELS
                type_color = CATALYST_TYPE_COLORS.get(row_c["catalyst_type"], "#8b949e")
                stars = "★" * int(row_c["importance"]) + "☆" * (5 - int(row_c["importance"]))
                st.markdown(f"""
                <div style="background:{PANEL_BG};border:1px solid {BORDER_CLR};border-left:2px solid {type_color};
                            border-radius:5px;padding:10px 14px;margin-bottom:8px">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                        <span style="background:{type_color}22;border:1px solid {type_color};color:{type_color};
                                     border-radius:10px;padding:1px 8px;font-size:11px;font-weight:600">{row_c['catalyst_type']}</span>
                        <span style="color:#e3b341;font-size:13px">{stars}</span>
                        <span style="color:{TEXT_DIM};font-size:12px;margin-left:auto">{row_c['expected_timing']}</span>
                    </div>
                    <div style="color:{TEXT_MAIN};font-size:14px;font-weight:500">{row_c['catalyst']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("catalysts.csv not found or empty.")

    st.markdown("---")
    st.caption("Edit data/theses.json to update thesis content · Not investment advice")
