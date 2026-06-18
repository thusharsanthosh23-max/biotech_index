"""
pages/catalyst_calendar.py
Catalyst Calendar — filterable table of upcoming binary events.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import (
    load_catalysts, WATCHLIST, CATALYST_TYPE_COLORS,
    IMPORTANCE_LABELS, chart_layout, TEXT_DIM, TEXT_MAIN, BORDER_CLR, PANEL_BG
)


def render():
    st.title("Catalyst Calendar")
    st.markdown(
        "<p style='color:#8b949e;margin-top:-12px'>Upcoming binary events across the watchlist · Edit data/catalysts.csv to update</p>",
        unsafe_allow_html=True
    )

    df = load_catalysts()
    if df.empty:
        st.info("No catalyst data found. Add entries to data/catalysts.csv.")
        return

    # ── Filters ────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        tickers = ["All"] + sorted(df["ticker"].unique().tolist())
        selected_ticker = st.selectbox("Filter by Ticker", tickers)

    with col2:
        types = ["All"] + sorted(df["catalyst_type"].unique().tolist())
        selected_type = st.selectbox("Filter by Type", types)

    with col3:
        quarters = ["All"] + sorted(df["quarter"].unique().tolist())
        selected_quarter = st.selectbox("Filter by Quarter", quarters)

    # Apply filters
    filtered = df.copy()
    if selected_ticker != "All":
        filtered = filtered[filtered["ticker"] == selected_ticker]
    if selected_type != "All":
        filtered = filtered[filtered["catalyst_type"] == selected_type]
    if selected_quarter != "All":
        filtered = filtered[filtered["quarter"] == selected_quarter]

    filtered = filtered.sort_values(["importance", "quarter"], ascending=[False, True])

    st.markdown(f"<p style='color:{TEXT_DIM};font-size:13px'>{len(filtered)} catalysts shown</p>", unsafe_allow_html=True)
    st.markdown("---")

    # ── Importance summary bar ────────────────────────────────────────────
    critical = filtered[filtered["importance"] == 5]
    high = filtered[filtered["importance"] == 4]
    c1, c2, c3 = st.columns(3)
    c1.metric("Critical (★5)", len(critical))
    c2.metric("High Impact (★4)", len(high))
    c3.metric("Total Catalysts", len(filtered))

    st.markdown("---")

    # ── Catalyst cards ────────────────────────────────────────────────────
    for _, row in filtered.iterrows():
        type_color = CATALYST_TYPE_COLORS.get(row["catalyst_type"], "#8b949e")
        importance_stars = "★" * int(row["importance"]) + "☆" * (5 - int(row["importance"]))
        importance_label = IMPORTANCE_LABELS.get(int(row["importance"]), "")
        source_html = ""
        if pd.notna(row.get("source")) and str(row.get("source", "")).startswith("http"):
            source_html = f"<a href='{row['source']}' target='_blank' style='color:#58a6ff;font-size:12px;text-decoration:none'>↗ Source</a>"

        st.markdown(f"""
        <div style="background:{PANEL_BG};border:1px solid {BORDER_CLR};border-left:3px solid {type_color};
                    border-radius:6px;padding:14px 18px;margin-bottom:10px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap">
                <span class='ticker-badge'>{row['ticker']}</span>
                <span style="background:{type_color}22;border:1px solid {type_color};color:{type_color};
                             border-radius:10px;padding:2px 9px;font-size:11px;font-weight:600;text-transform:uppercase">
                    {row['catalyst_type']}
                </span>
                <span style="color:#e3b341;font-size:14px" title="{importance_label}">{importance_stars}</span>
                <span style="color:{TEXT_DIM};font-size:12px;margin-left:auto">{row['expected_timing']} · {row['quarter']}</span>
                {source_html}
            </div>
            <div style="color:#e6edf3;font-weight:600;font-size:15px;margin-bottom:8px">{row['catalyst']}</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:6px">
                <div>
                    <div style="font-size:11px;text-transform:uppercase;color:#3fb950;letter-spacing:0.08em;margin-bottom:3px">Bull Impact</div>
                    <div style="color:{TEXT_MAIN};font-size:13px;line-height:1.5">{row['bull_impact']}</div>
                </div>
                <div>
                    <div style="font-size:11px;text-transform:uppercase;color:#f78166;letter-spacing:0.08em;margin-bottom:3px">Bear Risk</div>
                    <div style="color:{TEXT_MAIN};font-size:13px;line-height:1.5">{row['bear_risk']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Edit data/catalysts.csv to add, remove, or update catalysts · Not investment advice")
