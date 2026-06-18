"""
pages/dashboard.py
Dashboard — KPI metrics, cumulative performance, drawdown chart, stats table.
"""

import streamlit as st
import plotly.graph_objects as go
from utils.helpers import (
    load_excel_data, chart_layout,
    TEXT_DIM, TEXT_MAIN, BORDER_CLR, PANEL_BG
)


def render():
    stats_df, idx_df, dd_df, factor, prices = load_excel_data()

    if stats_df is None:
        st.error("Could not load data. Ensure data/data.xlsx exists.")
        return

    st.title("Biotech Watchlist Index")
    st.markdown(
        "<p style='color:#8b949e;margin-top:-12px'>Equal-weight 9-stock watchlist · Backtested June 2024 – June 2026</p>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='perf-callout'>📈 Watchlist returned +128.7% over the period vs. XBI +44.9% · IBB +26.1% · SPY +41.1%</div>",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI metrics ───────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Return",   "128.7%", "+84pp vs XBI")
    col2.metric("CAGR",           "51.2%",  "+31pp vs XBI")
    col3.metric("Sharpe Ratio",   "1.01",   "vs SPY 1.21")
    col4.metric("Max Drawdown",   "-33.7%", "vs XBI -21.8%")

    st.markdown("---")

    # ── Cumulative performance chart ───────────────────────────────────────
    st.subheader("Cumulative Performance (Base 100)")

    colors = {
        "Watchlist Index": "#58a6ff",
        "XBI Index":       "#f78166",
        "IBB Index":       "#d2a8ff",
        "SPY Index":       "#7ee787",
    }
    labels = {
        "Watchlist Index": "Watchlist",
        "XBI Index":       "XBI",
        "IBB Index":       "IBB",
        "SPY Index":       "SPY",
    }

    fig = go.Figure()
    for col, color in colors.items():
        fig.add_trace(go.Scatter(
            x=idx_df["Month"],
            y=idx_df[col],
            name=labels[col],
            line=dict(color=color, width=2.5 if col == "Watchlist Index" else 1.5),
            hovertemplate=f"<b>{labels[col]}</b><br>%{{x|%b %Y}}<br>Index: %{{y:.1f}}<extra></extra>"
        ))

    fig.update_layout(**chart_layout(height=380))
    st.plotly_chart(fig, use_container_width=True)

    # ── Drawdown chart ────────────────────────────────────────────────────
    st.subheader("Drawdown from Peak")

    dd_colors = {
        "Watchlist DD": "#58a6ff",
        "XBI DD":       "#f78166",
        "IBB DD":       "#d2a8ff",
        "SPY DD":       "#7ee787",
    }
    dd_labels = {"Watchlist DD": "Watchlist", "XBI DD": "XBI", "IBB DD": "IBB", "SPY DD": "SPY"}
    fill_colors = {
        "Watchlist DD": "rgba(88,166,255,0.08)",
        "XBI DD":       "rgba(247,129,102,0.08)",
        "IBB DD":       "rgba(210,168,255,0.08)",
        "SPY DD":       "rgba(126,231,135,0.08)",
    }

    fig2 = go.Figure()
    for col, color in dd_colors.items():
        fig2.add_trace(go.Scatter(
            x=dd_df["Month"],
            y=dd_df[col] * 100,
            name=dd_labels[col],
            fill="tozeroy",
            fillcolor=fill_colors[col],
            line=dict(color=color, width=1.5),
            hovertemplate=f"<b>{dd_labels[col]}</b><br>%{{x|%b %Y}}<br>DD: %{{y:.1f}}%<extra></extra>"
        ))

    layout2 = chart_layout(height=260)
    layout2["yaxis"]["ticksuffix"] = "%"
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True)

    # ── Stats table ───────────────────────────────────────────────────────
    st.subheader("Summary Statistics")

    display_stats = stats_df.copy()
    try:
        display_stats["Total Return"]   = (display_stats["Total Return"].astype(float) * 100).map("{:.1f}%".format)
        display_stats["CAGR"]           = (display_stats["CAGR"].astype(float) * 100).map("{:.1f}%".format)
        display_stats["Volatility"]     = (display_stats["Volatility"].astype(float) * 100).map("{:.1f}%".format)
        display_stats["Sharpe (4% rf)"] = display_stats["Sharpe (4% rf)"].astype(float).map("{:.2f}".format)
        display_stats["Max Drawdown"]   = (display_stats["Max Drawdown"].astype(float) * 100).map("{:.1f}%".format)
    except Exception as e:
        st.warning(f"Stats formatting issue: {e}")

    st.dataframe(display_stats, use_container_width=True, hide_index=True)
