# 🧬 Biotech Intelligence Dashboard

A biotech equity research and portfolio strategy dashboard built with Streamlit. Tracks a 9-stock equal-weight watchlist against XBI, IBB, and SPY benchmarks with full factor scoring, catalyst tracking, pipeline mapping, and company deep dives.

---

## Features

| Page | Description |
|---|---|
| 📊 Dashboard | KPI metrics, cumulative performance chart, drawdown, stats table |
| 📈 Index Performance | Full benchmark comparison with monthly return heatmap |
| 🏢 Holdings | Watchlist table, individual price history, thesis summary |
| 📅 Catalyst Calendar | Filterable binary event tracker with bull/bear impact |
| 🔬 Company Deep Dive | Full thesis, bull/bear case, risks, score radar per ticker |
| 🧪 Pipeline | Drug asset database filtered by phase, modality, indication |
| ⭐ Score Breakdown | Factor scores, radar charts, heatmap across all companies |
| 📋 Methodology | Index construction, data sources, scoring definitions |

---

## Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/thusharsanthosh23-max/biotech_index.git
cd biotech_index

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app will open at http://localhost:8501

---

## Data File Structure

All data files live in the `/data` folder. Edit these to update content without touching code.

### `data/data.xlsx`
Main Excel file with backtest results, monthly prices, and factor data.
Sheets: `Backtest`, `Monthly_Prices`, `Monthly_Returns`, `Factor_Data`, `Sources`

### `data/catalysts.csv`
Catalyst calendar. Columns:
```
ticker, company, catalyst, catalyst_type, expected_timing, quarter,
importance (1-5), bull_impact, bear_risk, source
```
`catalyst_type` options: `clinical`, `regulatory`, `earnings`, `partnership`, `commercial`

### `data/theses.json`
Company thesis content. One entry per ticker:
```json
{
  "TICK": {
    "name": "Company Name",
    "theme": "Sector / Modality",
    "why_in_index": "...",
    "thesis": "...",
    "bull_case": "...",
    "bear_case": "...",
    "key_risks": "...",
    "recent_developments": "..."
  }
}
```

### `data/pipeline.csv`
Drug asset database. Columns:
```
ticker, company, asset, modality, indication, phase, partner,
upcoming_milestone, estimated_timing, notes
```
`phase` options: `Preclinical`, `Phase 1`, `Phase 1/2`, `Phase 2`, `Phase 2b`, `Phase 3`, `NDA Filed`, `Approved`, `Commercial`

### `data/scores.csv`
Factor scores (0–100 each, dilution_penalty is negative). Columns:
```
ticker, company, analyst, quality, growth, balance_sheet, valuation,
capital_allocation, pipeline, platform, dilution_penalty, notes
```

---

## Watchlist

| Ticker | Company | Theme |
|---|---|---|
| NBTX | Nanobiotix | Royalty / Platform |
| IONS | Ionis Pharmaceuticals | RNA Therapeutics |
| CYTK | Cytokinetics | Cardiovascular |
| GRAL | GRAIL | Diagnostics / MCED |
| CDNA | CareDx | Transplant Diagnostics |
| CTMX | CytomX Therapeutics | Oncology ADC |
| GPCR | Structure Therapeutics | Obesity / GLP-1 |
| IDYA | IDEAYA Biosciences | Precision Oncology |
| NRIX | Nurix Therapeutics | BTK Degrader / Immunology |

**Benchmarks:** XBI · IBB · SPY  
**Backtest period:** June 2024 – June 2026  
**Construction:** Equal-weight, monthly rebalanced  

---

## Project Structure

```
biotech-index/
├── app.py                    # Entry point — page router
├── requirements.txt
├── README.md
├── utils/
│   ├── __init__.py
│   └── helpers.py            # CSS, chart theme, shared data loaders
├── pages/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── index_performance.py
│   ├── holdings.py
│   ├── catalyst_calendar.py
│   ├── company_thesis.py
│   ├── pipeline.py
│   ├── scores.py
│   └── methodology.py
└── data/
    ├── data.xlsx
    ├── catalysts.csv
    ├── theses.json
    ├── pipeline.csv
    └── scores.csv
```

---

## Future Improvements

- [ ] Automated price data refresh via yfinance or Financial Modeling Prep API
- [ ] Point-in-time factor scoring across a wider 50–200 stock biotech universe
- [ ] Portfolio construction page with equal / score-weighted / market-cap options
- [ ] Monthly research report PDF export
- [ ] Email/Slack alert when a catalyst date is within 30 days
- [ ] Peer comparison across therapeutic area cohorts

---

*Research / educational model only · Not investment advice*
