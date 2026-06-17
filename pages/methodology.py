"""
pages/methodology.py
Methodology — index construction, data sources, scoring factor definitions.
"""

import streamlit as st
import pandas as pd
from utils.helpers import TEXT_DIM


def render():
    st.title("Methodology")
    st.markdown(
        "<p style='color:#8b949e;margin-top:-12px'>How the index is constructed, backtested, and scored</p>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Construction")
        st.markdown("""
        **Universe**  
        9 biotech stocks selected based on qualitative thesis strength across cardiovascular, oncology,
        RNA therapeutics, diagnostics, and obesity categories.

        **Weighting**  
        Equal-weight basket, rebalanced monthly using month-end adjusted prices.

        **Benchmarks**  
        XBI (SPDR S&P Biotech ETF), IBB (iShares Biotechnology ETF), SPY (S&P 500).

        **Backtest Period**  
        June 2024 – June 2026. Start date chosen because GRAL history begins June 2024,
        allowing a complete current-watchlist sample.
        """)

    with col2:
        st.subheader("Risk & Limitations")
        st.markdown("""
        **Risk-free rate**  
        4.0% annual, used for Sharpe ratio calculation.

        **Key Limitation**  
        This is a *realized-watchlist price backtest*, not a point-in-time factor backtest.
        It tests what happened to these stocks — it does not prove that the scoring factors
        predicted returns in advance.

        **Missing data**  
        CDNA May 2026 price was unavailable; the basket return averages available constituents
        when at least 8 of 9 returns are present.

        **Recommended next step**  
        Point-in-time quarterly scoring across a wider biotech universe with historical factor data.
        """)

    st.markdown("---")
    st.subheader("Data Sources")
    try:
        sources = pd.read_excel("data/data.xlsx", sheet_name="Sources")
        st.dataframe(sources[["Source", "Type", "Used For"]], use_container_width=True, hide_index=True)
    except Exception:
        st.markdown("""
        | Source | Type | Used For |
        |---|---|---|
        | Yahoo Finance | Market data | Monthly prices, market cap |
        | Financial Modeling Prep | Fundamentals | EPS, P/E, 52W range |
        | SEC EDGAR | Filings | Cash, share count, dilution |
        | Analyst consensus | Research | Price targets, ratings |
        | Company IR sites | Primary | Pipeline data, catalyst timing |
        """)

    st.markdown("---")
    st.subheader("Scoring Factors")
    st.markdown("""
    Each company is scored 0–100 across 8 factors. A dilution penalty (0 to –20) is subtracted from the average.

    | Factor | Weight | Description |
    |---|---|---|
    | **Analyst** | Equal | Consensus rating, price target upside vs current price |
    | **Quality** | Equal | Gross margin, R&D spend efficiency, operating leverage |
    | **Growth** | Equal | Revenue growth rate, pipeline stage progression |
    | **Balance Sheet** | Equal | Cash runway in years, debt levels, burn rate |
    | **Valuation** | Equal | EV/Revenue, P/S vs sector peers |
    | **Capital Allocation** | Equal | Historical dilution, buybacks, partnership economics |
    | **Pipeline** | Equal | Phase advancement, indication size, probability of success |
    | **Platform** | Equal | Modality breadth, licensing potential, defensibility |
    | **Dilution Penalty** | — | Share count growth over trailing 2 years (negative, 0 to –20) |
    """)

    st.markdown("---")
    st.subheader("File Structure")
    st.code("""
biotech-index/
├── app.py                    # Entry point — page router
├── requirements.txt          # Python dependencies
├── README.md
├── utils/
│   ├── __init__.py
│   └── helpers.py            # CSS, chart theme, data loaders
├── pages/
│   ├── dashboard.py          # KPI metrics and performance charts
│   ├── index_performance.py  # Full benchmark comparison
│   ├── holdings.py           # Holdings table and price history
│   ├── catalyst_calendar.py  # Upcoming binary events
│   ├── company_thesis.py     # Deep dive per ticker
│   ├── pipeline.py           # Drug asset database
│   ├── scores.py             # Factor score charts
│   └── methodology.py        # This page
└── data/
    ├── data.xlsx             # Backtest, prices, factor data (from Excel)
    ├── catalysts.csv         # Edit this to update catalyst calendar
    ├── theses.json           # Edit this to update company theses
    ├── pipeline.csv          # Edit this to update pipeline database
    └── scores.csv            # Edit this to update factor scores
    """, language="")

    st.markdown("---")
    st.caption("Research / educational model only · Not investment advice · Built with Streamlit")
