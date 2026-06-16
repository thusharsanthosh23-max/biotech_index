import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Biotech Watchlist Index",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0d1117; color: #e6edf3; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
    }
    [data-testid="metric-container"] label { color: #8b949e !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: 0.08em; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #58a6ff !important; font-size: 28px !important; font-weight: 700; }
    
    /* Headers */
    h1 { color: #e6edf3 !important; font-weight: 700; letter-spacing: -0.02em; }
    h2, h3 { color: #c9d1d9 !important; }
    
    /* Tables */
    [data-testid="stDataFrame"] { border: 1px solid #30363d; border-radius: 8px; }
    
    /* Ticker badge */
    .ticker-badge {
        display: inline-block;
        background: #1f6feb22;
        border: 1px solid #1f6feb;
        color: #58a6ff;
        border-radius: 4px;
        padding: 2px 8px;
        font-family: monospace;
        font-weight: 700;
        font-size: 13px;
    }
    
    /* Section divider */
    .section-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #8b949e;
        margin-bottom: 4px;
    }
    
    /* Thesis card */
    .thesis-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-left: 3px solid #58a6ff;
        border-radius: 6px;
        padding: 16px 20px;
        margin-top: 8px;
        line-height: 1.6;
        color: #c9d1d9;
    }
    
    /* Performance callout */
    .perf-callout {
        background: #0f291e;
        border: 1px solid #238636;
        border-radius: 8px;
        padding: 12px 16px;
        color: #3fb950;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    xl = pd.ExcelFile("data.xlsx")

    # Summary stats — row 2 is header, rows 3-6 are data
    raw = pd.read_excel(xl, "Backtest", header=None)
    stats_df = raw.iloc[2:7, 0:6].copy()
    stats_df.columns = stats_df.iloc[0]
    stats_df = stats_df[1:].reset_index(drop=True)
    stats_df.columns.name = None

    # Index time series — cols 7-11
    idx_df = raw.iloc[2:, 7:12].copy()
    idx_df.columns = idx_df.iloc[0]
    idx_df = idx_df[1:].dropna(subset=["Month"]).reset_index(drop=True)
    idx_df.columns.name = None
    idx_df["Month"] = pd.to_datetime(idx_df["Month"].astype(str))
    for c in ["Watchlist Index", "XBI Index", "IBB Index", "SPY Index"]:
        idx_df[c] = pd.to_numeric(idx_df[c], errors="coerce")

    # Drawdown — cols 13-17
    dd_df = raw.iloc[2:, 13:18].copy()
    dd_df.columns = dd_df.iloc[0]
    dd_df = dd_df[1:].dropna(subset=["Month"]).reset_index(drop=True)
    dd_df.columns.name = None
    dd_df["Month"] = pd.to_datetime(dd_df["Month"].astype(str))
    for c in ["Watchlist DD", "XBI DD", "IBB DD", "SPY DD"]:
        dd_df[c] = pd.to_numeric(dd_df[c], errors="coerce")

    # Factor data
    factor = pd.read_excel(xl, "Factor_Data")

    # Monthly prices
    prices = pd.read_excel(xl, "Monthly_Prices")
    prices["Month"] = pd.to_datetime(prices["Month"].astype(str))

    return stats_df, idx_df, dd_df, factor, prices

stats_df, idx_df, dd_df, factor, prices = load_data()

WATCHLIST = ["NBTX", "IONS", "CYTK", "GRAL", "CDNA", "CTMX", "GPCR", "IDYA", "NRIX"]

THESES = {
    "NBTX": {
        "name": "Nanobiotix",
        "theme": "Royalty / Platform",
        "thesis": "Nanobiotix is shifting toward a capital-light model, with Johnson & Johnson leading development of JNJ-1900 while Nanobiotix retains milestone and royalty economics. The thesis emphasizes extended runway (through 2029 per management) and upside from broader adoption of its radiotherapy-enhancer platform, balanced against clinical trial risk and dilution/capital-structure risk."
    },
    "IONS": {
        "name": "Ionis Pharmaceuticals",
        "theme": "RNA Therapeutics",
        "thesis": "Ionis is transitioning from a platform-validated RNA therapeutics developer into a high-margin commercial biotech with accelerating revenue and expanding royalty streams. The strong early launches of TRYNGOLZA and DAWNZERA — its first wholly owned drugs — are establishing recurring, higher-margin revenue and major late-stage catalysts ahead."
    },
    "CYTK": {
        "name": "Cytokinetics",
        "theme": "Cardiovascular",
        "thesis": "Cytokinetics is emerging as a leading cardiovascular biotech with a successful first commercial product (Myqorzo in oHCM) and a potentially transformative expansion opportunity in non-obstructive HCM. The pivotal Phase 3 ACACIA-HCM trial (topline data expected 2Q26) and $1.1B+ cash runway make this a compelling SMid-cap CV name."
    },
    "GRAL": {
        "name": "GRAIL",
        "theme": "Diagnostics / MCED",
        "thesis": "GRAIL is scaling adoption of its Galleri multi-cancer early detection test, with Q1 revenue up 28% and test volume up 50%. Expanding clinical evidence, payer engagement, and employer-channel penetration could broaden reimbursement. Key risks: high gross losses, regulatory uncertainty, and competing screening technologies."
    },
    "CDNA": {
        "name": "CareDx",
        "theme": "Transplant Diagnostics",
        "thesis": "CareDx is a leading precision-diagnostics company in transplant surveillance, posting 39% YoY revenue growth in Q1 2026 and raising full-year guidance. The Naveris acquisition adds viral-mediated cancer surveillance, leveraging existing lab and commercial infrastructure. Reimbursement remains the key swing factor."
    },
    "CTMX": {
        "name": "CytomX Therapeutics",
        "theme": "Oncology ADC",
        "thesis": "Varseta-M showed a 32% ORR in heavily pretreated metastatic CRC — meaningful for a late-line population. As the only EpCAM-directed ADC in clinical development, it has first-mover advantage. H2 2026 data is the make-or-break catalyst. Cash of ~$347M extends runway into at least H2 2028. High-grade diarrhea remains the key toxicity risk."
    },
    "GPCR": {
        "name": "Structure Therapeutics",
        "theme": "Obesity / GLP-1",
        "thesis": "Phase 2 ACCESS II showed up to 16.3% body weight loss at 44 weeks for aleniglipron, an oral GLP-1. The FDA gave positive end-of-Phase 2 feedback; Phase 3 initiates Q3 2026. $1.5B in cash provides runway through end of 2028. The key risk is DILI (liver injury) — the ghost of Pfizer's danuglipron — and commercial differentiation against Novo and Lilly."
    },
    "IDYA": {
        "name": "IDEAYA Biosciences",
        "theme": "Precision Oncology",
        "thesis": "Darovasertib + crizotinib reduced disease progression risk by 58% in first-line HLA*A2-negative metastatic uveal melanoma — a cancer with no FDA-approved treatments. The RTOR NDA submission process was initiated in May 2026, targeting filing completion in H2 2026. Cash of ~$973M with runway into 2030."
    },
    "NRIX": {
        "name": "Nurix Therapeutics",
        "theme": "BTK Degrader / Immunology",
        "thesis": "Bexobrutideg achieved 83% ORR and 22.1-month mPFS in r/r CLL — outperforming JAYPIRCA (65% ORR, 14-month mPFS) by eliminating both kinase and scaffolding BTK functions. The Roche deal (June 2026) provides $700M upfront with up to $2.3B in milestones, resolving near-term cash concerns and bringing Roche's commercial infrastructure to bear."
    }
}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧬 Biotech Index")
    st.markdown("<div class='section-label'>Navigation</div>", unsafe_allow_html=True)
    page = st.radio("", ["📊 Dashboard", "🏢 Holdings", "📋 Methodology"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<div class='section-label'>Backtest Period</div>", unsafe_allow_html=True)
    st.markdown("Jun 2024 – Jun 2026")
    st.markdown("<div class='section-label' style='margin-top:12px'>Universe</div>", unsafe_allow_html=True)
    st.markdown("9 stocks · Equal weight · Monthly rebalanced")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("Biotech Watchlist Index")
    st.markdown("<p style='color:#8b949e;margin-top:-12px'>Equal-weight 9-stock watchlist · Backtested June 2024 – June 2026</p>", unsafe_allow_html=True)

    st.markdown("<div class='perf-callout'>📈 Watchlist returned +128.7% over the period vs. XBI +44.9% · IBB +26.1% · SPY +41.1%</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Return", "128.7%", "+84pp vs XBI")
    col2.metric("CAGR", "51.2%", "+31pp vs XBI")
    col3.metric("Sharpe Ratio", "1.01", "vs SPY 1.21")
    col4.metric("Max Drawdown", "-33.7%", "vs XBI -21.8%")

    st.markdown("---")

    # ── Cumulative performance chart
    st.subheader("Cumulative Performance (Base 100)")

    colors = {
        "Watchlist Index": "#58a6ff",
        "XBI Index": "#f78166",
        "IBB Index": "#d2a8ff",
        "SPY Index": "#7ee787"
    }
    labels = {
        "Watchlist Index": "Watchlist",
        "XBI Index": "XBI",
        "IBB Index": "IBB",
        "SPY Index": "SPY"
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

    fig.update_layout(
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="#8b949e"),
        legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)", font_color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d", tickfont_color="#8b949e", showline=False),
        yaxis=dict(gridcolor="#21262d", tickfont_color="#8b949e", ticksuffix=""),
        margin=dict(l=0, r=0, t=30, b=0),
        height=380,
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Drawdown chart
    st.subheader("Drawdown from Peak")
    fig2 = go.Figure()
    dd_colors = {
        "Watchlist DD": "#58a6ff",
        "XBI DD": "#f78166",
        "IBB DD": "#d2a8ff",
        "SPY DD": "#7ee787"
    }
    dd_labels = {"Watchlist DD": "Watchlist", "XBI DD": "XBI", "IBB DD": "IBB", "SPY DD": "SPY"}
    for col, color in dd_colors.items():
        fig2.add_trace(go.Scatter(
            x=dd_df["Month"],
            y=dd_df[col] * 100,
            name=dd_labels[col],
            fill="tozeroy",
            fillcolor=color.replace(")", ",0.08)").replace("rgb", "rgba") if "rgb" in color else color + "15",
            line=dict(color=color, width=1.5),
            hovertemplate=f"<b>{dd_labels[col]}</b><br>%{{x|%b %Y}}<br>DD: %{{y:.1f}}%<extra></extra>"
        ))
    fig2.update_layout(
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="#8b949e"),
        legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)", font_color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d", tickfont_color="#8b949e"),
        yaxis=dict(gridcolor="#21262d", tickfont_color="#8b949e", ticksuffix="%"),
        margin=dict(l=0, r=0, t=30, b=0),
        height=260,
        hovermode="x unified"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Stats table
    st.subheader("Summary Statistics")
    display_stats = stats_df.copy()
    display_stats["Total Return"] = (display_stats["Total Return"].astype(float) * 100).map("{:.1f}%".format)
    display_stats["CAGR"] = (display_stats["CAGR"].astype(float) * 100).map("{:.1f}%".format)
    display_stats["Volatility"] = (display_stats["Volatility"].astype(float) * 100).map("{:.1f}%".format)
    display_stats["Sharpe (4% rf)"] = display_stats["Sharpe (4% rf)"].astype(float).map("{:.2f}".format)
    display_stats["Max Drawdown"] = (display_stats["Max Drawdown"].astype(float) * 100).map("{:.1f}%".format)
    st.dataframe(display_stats, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOLDINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏢 Holdings":
    st.title("Holdings")
    st.markdown("<p style='color:#8b949e;margin-top:-12px'>9-stock equal-weight watchlist</p>", unsafe_allow_html=True)

    # Holdings table
    holdings = factor[factor["Ticker"].isin(WATCHLIST)].copy()
    holdings["Market Cap"] = holdings["Market Cap"].apply(
        lambda x: f"${x/1e9:.1f}B" if pd.notna(x) and x >= 1e9 else (f"${x/1e6:.0f}M" if pd.notna(x) else "—")
    )
    holdings["Current Price"] = holdings["Current Price"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    holdings["P/E"] = holdings["P/E"].apply(lambda x: f"{x:.1f}x" if pd.notna(x) else "—")
    holdings["52W Range"] = holdings.apply(
        lambda r: f"${r['52W Low']:.2f} – ${r['52W High']:.2f}" if pd.notna(r['52W Low']) else "—", axis=1
    )

    st.dataframe(
        holdings[["Ticker", "Company / ETF", "Current Price", "Market Cap", "P/E", "52W Range"]].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("Individual Stock Price History")

    ticker = st.selectbox("Select ticker", WATCHLIST, format_func=lambda t: f"{t} — {THESES[t]['name']}")

    # Price chart for selected ticker
    price_data = prices[["Month", ticker]].dropna()
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=price_data["Month"],
        y=price_data[ticker],
        fill="tozeroy",
        fillcolor="rgba(88,166,255,0.08)",
        line=dict(color="#58a6ff", width=2),
        hovertemplate=f"<b>{ticker}</b><br>%{{x|%b %Y}}<br>${{y:.2f}}<extra></extra>"
    ))
    fig3.update_layout(
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="#8b949e"),
        xaxis=dict(gridcolor="#21262d", tickfont_color="#8b949e"),
        yaxis=dict(gridcolor="#21262d", tickfont_color="#8b949e", tickprefix="$"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=260
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Thesis card
    t = THESES[ticker]
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px'>
        <span class='ticker-badge'>{ticker}</span>
        <span style='color:#8b949e;font-size:13px'>{t['theme']}</span>
    </div>
    <div class='thesis-card'>{t['thesis']}</div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Methodology":
    st.title("Methodology")
    st.markdown("<p style='color:#8b949e;margin-top:-12px'>How the index is constructed and backtested</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Construction")
        st.markdown("""
        **Universe**  
        9 biotech stocks selected based on qualitative thesis strength across cardiovascular, oncology, RNA therapeutics, diagnostics, and obesity categories.

        **Weighting**  
        Equal-weight basket, rebalanced monthly using month-end adjusted prices.

        **Benchmarks**  
        XBI (SPDR S&P Biotech ETF), IBB (iShares Biotechnology ETF), SPY (S&P 500).

        **Backtest Period**  
        June 2024 – June 2026. Start date chosen because GRAL history begins June 2024, allowing a complete current-watchlist sample.
        """)

    with col2:
        st.subheader("Risk & Limitations")
        st.markdown("""
        **Risk-free rate**  
        4.0% annual, used for Sharpe ratio calculation.

        **Key Limitation**  
        This is a *realized-watchlist price backtest*, not a point-in-time factor backtest. It tests what happened to these stocks — it does not prove that the scoring factors predicted returns in advance.

        **Missing data**  
        CDNA May 2026 price was unavailable; the basket return averages available constituents when at least 8 of 9 returns are present.

        **Recommended next step**  
        Point-in-time quarterly scoring across a wider biotech universe with historical factor data (Option B).
        """)

    st.markdown("---")
    st.subheader("Data Sources")
    sources = pd.read_excel("data.xlsx", sheet_name="Sources")
    st.dataframe(sources[["Source", "Type", "Used For"]], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Scoring Factors (Planned)")
    st.markdown("""
    The next phase of this project will assign quantitative scores across these factor categories:

    | Factor | Description |
    |---|---|
    | **Analyst** | Consensus rating, price target upside |
    | **Quality** | Gross margin, R&D efficiency |
    | **Growth** | Revenue growth, pipeline stage progression |
    | **Balance Sheet** | Cash runway, debt levels |
    | **Valuation** | EV/Revenue, P/S vs peers |
    | **Capital Allocation** | Dilution history, buybacks |
    | **Pipeline** | Phase, indication size, probability of success |
    | **Platform** | Modality breadth, licensing potential |
    | **Dilution** | Share count growth, offering history |
    """)

    st.markdown("---")
    st.caption("Research / educational model only · Not investment advice · Built with Streamlit")
