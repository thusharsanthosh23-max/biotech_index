"""
pages/pipeline.py
Pipeline Database — filterable table of all drug assets across the watchlist.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import (
    load_pipeline, TICKER_COLORS, chart_layout,
    TEXT_DIM, TEXT_MAIN, BORDER_CLR, PANEL_BG
)

PHASE_ORDER = [
    "Preclinical", "Phase 1", "Phase 1/2", "Phase 2", "Phase 2b",
    "Phase 3", "NDA Filed", "Approved", "Commercial"
]

PHASE_COLORS = {
    "Preclinical":  "#8b949e",
    "Phase 1":      "#58a6ff",
    "Phase 1/2":    "#79c0ff",
    "Phase 2":      "#d2a8ff",
    "Phase 2b":     "#bc8cff",
    "Phase 3":      "#ffa657",
    "NDA Filed":    "#e3b341",
    "Approved":     "#7ee787",
    "Commercial":   "#3fb950",
}


def _safe(val, fallback="—"):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return fallback
    s = str(val).strip()
    return fallback if s == "" or s == "nan" else s


def render():
    st.title("Pipeline Database")
    st.markdown(
        "<p style='color:#8b949e;margin-top:-12px'>All drug assets across the watchlist · Edit data/pipeline.csv to update</p>",
        unsafe_allow_html=True
    )

    df = load_pipeline()
    if df.empty:
        st.info("No pipeline data found. Add entries to data/pipeline.csv.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Assets", len(df))
    col2.metric("Phase 3 / NDA / Commercial",
                len(df[df["phase"].isin(["Phase 3", "NDA Filed", "Approved", "Commercial"])]))
    col3.metric("Companies", df["ticker"].nunique())
    col4.metric("Indications", df["indication"].nunique())

    st.markdown("---")

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        sel_ticker = st.selectbox("Ticker", ["All"] + sorted(df["ticker"].unique().tolist()))
    with col_f2:
        sel_phase = st.selectbox("Phase", ["All"] + [p for p in PHASE_ORDER if p in df["phase"].unique()])
    with col_f3:
        sel_modality = st.selectbox("Modality", ["All"] + sorted(df["modality"].dropna().unique().tolist()))
    with col_f4:
        sel_partner = st.selectbox("Partner", ["All"] + sorted(df["partner"].dropna().unique().tolist()))

    filtered = df.copy()
    if sel_ticker != "All":
        filtered = filtered[filtered["ticker"] == sel_ticker]
    if sel_phase != "All":
        filtered = filtered[filtered["phase"] == sel_phase]
    if sel_modality != "All":
        filtered = filtered[filtered["modality"] == sel_modality]
    if sel_partner != "All":
        filtered = filtered[filtered["partner"] == sel_partner]

    filtered["phase_order"] = filtered["phase"].apply(
        lambda p: PHASE_ORDER.index(p) if p in PHASE_ORDER else 99
    )
    filtered = filtered.sort_values(["phase_order", "ticker"], ascending=[False, True])

    st.markdown(f"<p style='color:{TEXT_DIM};font-size:13px'>{len(filtered)} assets shown</p>",
                unsafe_allow_html=True)

    for _, row in filtered.iterrows():
        phase = _safe(row.get("phase"), "—")
        phase_color = PHASE_COLORS.get(phase, "#8b949e")
        ticker = _safe(row.get("ticker"), "—")
        asset = _safe(row.get("asset"), "—")
        modality = _safe(row.get("modality"), "—")
        indication = _safe(row.get("indication"), "—")
        partner = _safe(row.get("partner"), "None")
        milestone = _safe(row.get("upcoming_milestone"), "")
        timing = _safe(row.get("estimated_timing"), "")
        notes = _safe(row.get("notes"), "")

        # Card header + grid
        st.markdown(f"""
<div style="background:{PANEL_BG};border:1px solid {BORDER_CLR};border-left:3px solid {phase_color};border-radius:6px;padding:14px 18px;margin-bottom:4px">
  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px">
    <span class='ticker-badge'>{ticker}</span>
    <span style="color:#e6edf3;font-weight:700;font-size:15px">{asset}</span>
    <span style="background:{phase_color}22;border:1px solid {phase_color};color:{phase_color};border-radius:10px;padding:2px 9px;font-size:11px;font-weight:700;margin-left:auto">{phase}</span>
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:8px">
    <div><div style="font-size:11px;color:{TEXT_DIM};text-transform:uppercase;margin-bottom:2px">Modality</div><div style="color:{TEXT_MAIN};font-size:13px">{modality}</div></div>
    <div><div style="font-size:11px;color:{TEXT_DIM};text-transform:uppercase;margin-bottom:2px">Indication</div><div style="color:{TEXT_MAIN};font-size:13px">{indication}</div></div>
    <div><div style="font-size:11px;color:{TEXT_DIM};text-transform:uppercase;margin-bottom:2px">Partner</div><div style="color:{TEXT_MAIN};font-size:13px">{partner}</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Milestone row (separate call)
        if milestone:
            st.markdown(f"""
<div style="background:#0d1117;border:1px solid {BORDER_CLR};border-top:none;border-radius:0 0 6px 6px;padding:8px 18px;margin-top:-4px;margin-bottom:4px">
  <span style="font-size:11px;color:{TEXT_DIM};text-transform:uppercase">Next Milestone: </span>
  <span style="color:#e3b341;font-size:13px">{milestone}</span>
  <span style="color:{TEXT_DIM};font-size:12px"> · {timing}</span>
</div>
""", unsafe_allow_html=True)

        # Notes row (separate call)
        if notes:
            st.markdown(f"""
<div style="background:{PANEL_BG};border:1px solid {BORDER_CLR};border-top:none;border-radius:0 0 6px 6px;padding:6px 18px 12px;margin-top:-4px;margin-bottom:10px">
  <span style="color:{TEXT_DIM};font-size:12px;line-height:1.5">{notes}</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Pipeline by Phase")

    phase_counts = df["phase"].value_counts()
    phase_counts = phase_counts.reindex([p for p in PHASE_ORDER if p in phase_counts.index])

    fig = go.Figure(go.Bar(
        x=phase_counts.index.tolist(),
        y=phase_counts.values.tolist(),
        marker_color=[PHASE_COLORS.get(p, "#8b949e") for p in phase_counts.index],
        hovertemplate="<b>%{x}</b><br>%{y} assets<extra></extra>"
    ))
    layout = chart_layout(height=280, legend=False)
    layout["yaxis"]["title"] = "Assets"
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.caption("Edit data/pipeline.csv to add or update pipeline assets · Not investment advice")
