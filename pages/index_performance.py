"""
pages/index_performance.py
Index Performance — full comparison of watchlist vs XBI, IBB, SPY.
Reads from data.xlsx backtest sheet (already loaded) or data/index_prices.csv as fallback.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import (
    load_excel_data, chart_layout,
    TEXT_DIM, TEXT_MAIN, BORDER_CLR, PANEL_BG, BASE_BG, CHART_COLORS
)


INDEX_COLORS = {
    "Watchlist Index": "#58a6ff",
    "XBI Index":       "#f78166",
    "IBB Index":       "#d2a8ff",
    "SPY Index":       "#7ee787",
}
INDEX_LABELS = {
    "Watchlist Index": "Watchlist",
    "XBI Index":       "XBI",
    "IBB Index":       "IBB",
    "SPY Index":       "SPY",
}
DD_COLORS = {
    "Watchlist DD": "#58a6ff",
    "XBI DD":       "#f78166",
    "IBB DD":       "#d2a8ff",
    "SPY DD":       "#7ee787",
}
DD_FILL = {
    "Watchlist DD": "rgba(88,166,255,0.08)",
    "XBI DD":       "rgba(247,129,102,0.08)",
    "IBB DD":       "rgba(210,168,255,0.08)",
    "SPY DD":       "rgba(126,231,135,0.08)",
}
DD_LABELS = {
    "Watchlist DD": "Watchlist",
    "XBI DD":       "XBI",
    "IBB DD":       "IBB",
    "SPY DD":       "SPY",
}


def _fmt_pct(val, multiply=True):
    try:
        v = float(val)
        if multiply:
            v *= 100
        return f"{v:+.1f}%" if v != 0 else f"{v:.1f}%"
    except Exception:
        return "—"


def render():
    st.title("Index Performance")
    st.markdown(
        "<p style='color:#8b949e;margin-top:-12px'>Equal-weight watchlist vs XBI · IBB · SPY · June 2024 – June 2026</p>",
        unsafe_allow_html=True
    )

    stats_df, idx_df, dd_df, _, _ = load_excel_data()

    if stats_df is None:
        st.error("Could not load backtest data. Ensure data.xlsx is in the /data folder.")
        return

    # ── KPI metrics ────────────────────────────────────────────────────────
    watchlist_stats = stats_df[stats_df["Portfolio / Benchmark"].str.contains("Watchlist", na=False)]
    xbi_stats       = stats_df[stats_df["Portfolio / Benchmark"] == "XBI"]

    if not watchlist_stats.empty:
        ws = watchlist_stats.iloc[0]
        wl_ret  = float(ws.get("Total Return", 0)) * 100
        wl_cagr = float(ws.get("CAGR", 0)) * 100
        wl_vol  = float(ws.get("Volatility", 0)) * 100
        wl_mdd  = float(ws.get("Max Drawdown", 0)) * 100
        wl_sharpe = float(ws.get("Sharpe (4% rf)", 0))
    else:
        wl_ret = wl_cagr = wl_vol = wl_mdd = wl_sharpe = 0

    if not xbi_stats.empty:
        xs = xbi_stats.iloc[0]
        xbi_ret  = float(xs.get("Total Return", 0)) * 100
        xbi_cagr = float(xs.get("CAGR", 0)) * 100
    else:
        xbi_ret = xbi_cagr = 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Return",   f"{wl_ret:.1f}%",   f"{wl_ret - xbi_ret:+.1f}pp vs XBI")
    col2.metric("CAGR",           f"{wl_cagr:.1f}%",  f"{wl_cagr - xbi_cagr:+.1f}pp vs XBI")
    col3.metric("Volatility",     f"{wl_vol:.1f}%")
    col4.metric("Max Drawdown",   f"{wl_mdd:.1f}%")
    col5.metric("Sharpe (4% rf)", f"{wl_sharpe:.2f}")

    st.markdown("---")

    # ── Cumulative return chart ────────────────────────────────────────────
    st.subheader("Cumulative Return (Base 100)")

    fig1 = go.Figure()
    for col, color in INDEX_COLORS.items():
        if col not in idx_df.columns:
            continue
        is_watchlist = col == "Watchlist Index"
        fig1.add_trace(go.Scatter(
            x=idx_df["Month"],
            y=idx_df[col],
            name=INDEX_LABELS[col],
            line=dict(color=color, width=3 if is_watchlist else 1.5,
                      dash="solid" if is_watchlist else "dot"),
            hovertemplate=f"<b>{INDEX_LABELS[col]}</b><br>%{{x|%b %Y}}<br>Index: %{{y:.1f}}<extra></extra>"
        ))

    layout1 = chart_layout(height=400)
    layout1["yaxis"]["title"] = "Index Value (100 = Jun 2024)"
    fig1.update_layout(**layout1)
    st.plotly_chart(fig1, use_container_width=True)

    # ── Drawdown chart ─────────────────────────────────────────────────────
    st.subheader("Drawdown from Peak")

    fig2 = go.Figure()
    for col, color in DD_COLORS.items():
        if col not in dd_df.columns:
            continue
        fig2.add_trace(go.Scatter(
            x=dd_df["Month"],
            y=dd_df[col] * 100,
            name=DD_LABELS[col],
            fill="tozeroy",
            fillcolor=DD_FILL[col],
            line=dict(color=color, width=1.5),
            hovertemplate=f"<b>{DD_LABELS[col]}</b><br>%{{x|%b %Y}}<br>DD: %{{y:.1f}}%<extra></extra>"
        ))

    layout2 = chart_layout(height=280)
    layout2["yaxis"]["ticksuffix"] = "%"
    layout2["yaxis"]["title"] = "Drawdown %"
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Full stats table ───────────────────────────────────────────────────
    st.subheader("Summary Statistics")

    display = stats_df.copy()
    try:
        display["Total Return"] = (display["Total Return"].astype(float) * 100).map("{:.1f}%".format)
        display["CAGR"]         = (display["CAGR"].astype(float) * 100).map("{:.1f}%".format)
        display["Volatility"]   = (display["Volatility"].astype(float) * 100).map("{:.1f}%".format)
        display["Sharpe (4% rf)"] = display["Sharpe (4% rf)"].astype(float).map("{:.2f}".format)
        display["Max Drawdown"] = (display["Max Drawdown"].astype(float) * 100).map("{:.1f}%".format)
    except Exception as e:
        st.warning(f"Could not format stats table: {e}")

    st.dataframe(display, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Monthly returns heatmap ─────────────────────────────────────────────
    st.subheader("Watchlist Monthly Returns")

    if "Watchlist Index" in idx_df.columns:
        idx_copy = idx_df[["Month", "Watchlist Index"]].copy().dropna()
        idx_copy["Return"] = idx_copy["Watchlist Index"].pct_change() * 100
        idx_copy["Year"]   = idx_copy["Month"].dt.year.astype(str)
        idx_copy["MonthName"] = idx_copy["Month"].dt.strftime("%b")
        idx_copy = idx_copy.dropna(subset=["Return"])

        month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        pivot = idx_copy.pivot_table(index="Year", columns="MonthName", values="Return")
        pivot = pivot.reindex(columns=[m for m in month_order if m in pivot.columns])

        fig3 = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0, "#6e1c1c"], [0.5, "#161b22"], [1, "#0f291e"]],
            zmid=0,
            text=[[f"{v:.1f}%" if not pd.isna(v) else "" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(color="white", size=11),
            hovertemplate="<b>%{y} %{x}</b><br>Return: %{z:.1f}%<extra></extra>",
            showscale=True,
            colorbar=dict(tickfont=dict(color=TEXT_DIM), ticksuffix="%"),
        ))
        layout3 = chart_layout(height=200, legend=False, hovermode="closest")
        layout3["margin"] = dict(l=0, r=60, t=10, b=0)
        fig3.update_layout(**layout3)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.caption("Backtest period: June 2024 – June 2026 · Equal-weight · Monthly rebalanced · 4% risk-free rate · Not investment advice")
