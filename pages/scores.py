"""
pages/scores.py
Score Breakdown — bar and radar charts for each company's factor scores.
Data lives in data/scores.csv — edit that file to update.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import (
    load_scores, WATCHLIST, TICKER_COLORS, chart_layout,
    TEXT_DIM, TEXT_MAIN, BORDER_CLR, PANEL_BG, BASE_BG, CHART_COLORS
)


SCORE_LABELS = {
    "analyst":           "Analyst",
    "quality":           "Quality",
    "growth":            "Growth",
    "balance_sheet":     "Balance Sheet",
    "valuation":         "Valuation",
    "capital_allocation":"Cap. Allocation",
    "pipeline":          "Pipeline",
    "platform":          "Platform",
}


def _bar_chart(df_row, color):
    """Horizontal bar chart for one company's scores."""
    labels = list(SCORE_LABELS.values())
    values = [df_row.get(k, 0) for k in SCORE_LABELS.keys()]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=color,
        hovertemplate="<b>%{y}</b>: %{x}<extra></extra>",
        text=values,
        textposition="outside",
        textfont=dict(color=TEXT_MAIN, size=11),
    ))
    layout = chart_layout(height=300, legend=False, hovermode="y unified")
    layout["xaxis"]["range"] = [0, 110]
    layout["xaxis"]["showgrid"] = True
    layout["yaxis"]["autorange"] = "reversed"
    layout["margin"] = dict(l=0, r=40, t=10, b=0)
    fig.update_layout(**layout)
    return fig


def _radar_chart(df_row, color):
    """Radar chart for one company's scores."""
    categories = list(SCORE_LABELS.values())
    values = [df_row.get(k, 0) for k in SCORE_LABELS.keys()]

    hex_c = color.lstrip("#")
    r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)

    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor=f"rgba({r},{g},{b},0.15)",
        line=dict(color=color, width=2),
    ))
    layout = chart_layout(height=320, legend=False, hovermode="closest")
    layout["polar"] = dict(
        bgcolor=PANEL_BG,
        radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363d", tickfont=dict(color=TEXT_DIM, size=9)),
        angularaxis=dict(gridcolor="#30363d", tickfont=dict(color=TEXT_MAIN, size=10)),
    )
    layout["margin"] = dict(l=20, r=20, t=30, b=20)
    fig.update_layout(**layout)
    return fig


def render():
    st.title("Score Breakdown")
    st.markdown(
        "<p style='color:#8b949e;margin-top:-12px'>Factor scores across all watchlist companies · Edit data/scores.csv to update</p>",
        unsafe_allow_html=True
    )

    df = load_scores()
    if df.empty:
        st.info("No score data found. Add entries to data/scores.csv.")
        return

    # ── Rankings overview ─────────────────────────────────────────────────
    st.subheader("Rankings Overview")

    display_df = df[["ticker", "company", "total_score"] + list(SCORE_LABELS.keys()) + ["dilution_penalty"]].copy()
    display_df = display_df.sort_values("total_score", ascending=False).reset_index(drop=True)
    display_df.insert(0, "Rank", range(1, len(display_df) + 1))

    # Rename columns for display
    rename = {"ticker": "Ticker", "company": "Company", "total_score": "Total Score",
               "dilution_penalty": "Dilution Penalty"}
    rename.update({k: v for k, v in SCORE_LABELS.items()})
    display_df = display_df.rename(columns=rename)

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Overall comparison bar chart ──────────────────────────────────────
    st.subheader("Total Score Comparison")

    sorted_df = df.sort_values("total_score", ascending=True)
    fig_overview = go.Figure(go.Bar(
        x=sorted_df["total_score"],
        y=sorted_df["ticker"],
        orientation="h",
        marker_color=[TICKER_COLORS.get(t, "#58a6ff") for t in sorted_df["ticker"]],
        hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>",
        text=sorted_df["total_score"].round(1),
        textposition="outside",
        textfont=dict(color=TEXT_MAIN, size=11),
    ))
    layout = chart_layout(height=300, legend=False)
    layout["xaxis"]["range"] = [0, 110]
    layout["xaxis"]["title"] = "Total Score"
    layout["margin"] = dict(l=0, r=40, t=10, b=0)
    fig_overview.update_layout(**layout)
    st.plotly_chart(fig_overview, use_container_width=True)

    st.markdown("---")

    # ── Per-company deep dive ─────────────────────────────────────────────
    st.subheader("Individual Score Breakdown")

    ticker_list = [t for t in WATCHLIST if t in df["ticker"].values]
    selected = st.selectbox("Select Company", ticker_list,
                            format_func=lambda t: f"{t} — {df[df['ticker']==t]['company'].values[0]}")

    row = df[df["ticker"] == selected].iloc[0].to_dict()
    color = TICKER_COLORS.get(selected, "#58a6ff")

    col_bar, col_radar = st.columns([1, 1])
    with col_bar:
        st.markdown(f"<p style='color:{TEXT_DIM};font-size:13px'>Factor scores (0–100)</p>", unsafe_allow_html=True)
        st.plotly_chart(_bar_chart(row, color), use_container_width=True)
    with col_radar:
        st.markdown(f"<p style='color:{TEXT_DIM};font-size:13px'>Radar view</p>", unsafe_allow_html=True)
        st.plotly_chart(_radar_chart(row, color), use_container_width=True)

    # Score detail table
    dp = int(row.get("dilution_penalty", 0))
    total = row.get("total_score", 0)
    notes = row.get("notes", "")

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Score", f"{total:.1f}")
    col_m2.metric("Dilution Penalty", str(dp))
    col_m3.metric("Pipeline Score", int(row.get("pipeline", 0)))

    if notes:
        st.markdown(f"""
        <div style="background:{PANEL_BG};border:1px solid {BORDER_CLR};border-radius:6px;
                    padding:12px 16px;margin-top:8px;color:{TEXT_DIM};font-size:13px;line-height:1.6">
            <b style="color:{TEXT_MAIN}">Analyst Notes:</b> {notes}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Factor heatmap across all companies ──────────────────────────────
    st.subheader("Factor Heatmap — All Companies")

    heat_df = df.set_index("ticker")[list(SCORE_LABELS.keys())].copy()
    heat_df.columns = list(SCORE_LABELS.values())

    fig_heat = go.Figure(go.Heatmap(
        z=heat_df.values,
        x=heat_df.columns.tolist(),
        y=heat_df.index.tolist(),
        colorscale=[[0, "#0d1117"], [0.5, "#1f6feb"], [1, "#58a6ff"]],
        text=heat_df.values.astype(int),
        texttemplate="%{text}",
        textfont=dict(color="white", size=11),
        hovertemplate="<b>%{y} · %{x}</b><br>Score: %{z}<extra></extra>",
        showscale=True,
        colorbar=dict(tickfont=dict(color=TEXT_DIM)),
    ))
    layout = chart_layout(height=320, legend=False, hovermode="closest")
    layout["margin"] = dict(l=0, r=60, t=10, b=0)
    fig_heat.update_layout(**layout)
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")
    st.caption("Scores are qualitative assessments — edit data/scores.csv to update · Not investment advice")
