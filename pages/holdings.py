"""
pages/holdings.py
Holdings — watchlist table, individual price history, and thesis summary.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import (
    load_excel_data, load_theses, WATCHLIST, TICKER_COLORS, chart_layout,
    TEXT_DIM, TEXT_MAIN, BORDER_CLR, PANEL_BG
)


def render():
    st.title("Holdings")
    st.markdown(
        "<p style='color:#8b949e;margin-top:-12px'>9-stock equal-weight watchlist</p>",
        unsafe_allow_html=True
    )

    _, _, _, factor, prices = load_excel_data()
    theses = load_theses()

    if factor is None:
        st.error("Could not load factor data.")
        return

    # ── Holdings table ────────────────────────────────────────────────────
    holdings = factor[factor["Ticker"].isin(WATCHLIST)].copy()
    holdings["Market Cap"] = holdings["Market Cap"].apply(
        lambda x: f"${x/1e9:.1f}B" if pd.notna(x) and x >= 1e9 else (f"${x/1e6:.0f}M" if pd.notna(x) else "—")
    )
    holdings["Current Price"] = holdings["Current Price"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    holdings["P/E"]           = holdings["P/E"].apply(lambda x: f"{x:.1f}x" if pd.notna(x) else "—")
    holdings["52W Range"]     = holdings.apply(
        lambda r: f"${r['52W Low']:.2f} – ${r['52W High']:.2f}" if pd.notna(r['52W Low']) else "—", axis=1
    )
    holdings["Theme"] = holdings["Ticker"].map(
        {t: d.get("theme", "") for t, d in theses.items()}
    )

    st.dataframe(
        holdings[["Ticker", "Company / ETF", "Theme", "Current Price", "Market Cap", "P/E", "52W Range"]].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ── Individual price chart + thesis ───────────────────────────────────
    st.subheader("Individual Stock Price History")

    ticker = st.selectbox(
        "Select ticker",
        WATCHLIST,
        format_func=lambda t: f"{t} — {theses.get(t, {}).get('name', t)}"
    )

    color = TICKER_COLORS.get(ticker, "#58a6ff")
    hex_c = color.lstrip("#")
    r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)

    if ticker in prices.columns:
        price_data = prices[["Month", ticker]].dropna()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=price_data["Month"],
            y=price_data[ticker],
            fill="tozeroy",
            fillcolor=f"rgba({r},{g},{b},0.08)",
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{ticker}</b><br>%{{x|%b %Y}}<br>${{y:.2f}}<extra></extra>"
        ))
        layout = chart_layout(height=260, legend=False)
        layout["yaxis"]["tickprefix"] = "$"
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No price data found for {ticker}.")

    # Thesis card
    t = theses.get(ticker, {})
    if t:
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px'>
            <span class='ticker-badge' style='border-color:{color};color:{color}'>{ticker}</span>
            <span style='color:{TEXT_DIM};font-size:13px'>{t.get('theme','')}</span>
        </div>
        <div class='thesis-card' style='border-left-color:{color}'>{t.get('thesis','')}</div>
        """, unsafe_allow_html=True)
    else:
        st.info("No thesis data found. Add this ticker to data/theses.json.")
