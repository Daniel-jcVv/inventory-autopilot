# Inventory Autopilot

Automated inventory health pipeline: raw ERP Excel exports → cleaning → analysis → database → dashboard → alerts.

Built with real (anonymized) warehouse data from a Tier 1 automotive manufacturer. Detects **$5.6M in dead stock** and **$2.5M in redundant orders** across 16,249 inventory items.

## Key Findings

| Metric | Value |
|--------|-------|
| Dead stock items | 3,795 (23.4%) — $5.6M |
| Overstock items | 1,234 — $1.9M |
| Redundant orders | 2,538 (66.6%) — $2.5M |
| Orders > 1 year old | 209 |

## Features

- **Dead stock detection** — items with stock but zero usage
- **Overstock alerts** — stock exceeding 12 months of demand
- **Redundant order flagging** — open orders where BOH already covers demand
- **ABC classification** — Pareto analysis (80/15/5) on inventory value
- **Days of Supply (DOS)** — stock runway per item
- **Reorder risk** — items with less than 30 days of stock
- **Demand forecasting** — Prophet/ARIMA on synthetic consumption data
- **Automated alerts** — n8n triggers pipeline on new ERP export, sends email/Slack

## Architecture

```
ERP Excel export
    │
    ▼
  Extract (pandas + openpyxl)
    │
    ▼
  Clean (drop sparse rows/cols, fix dates)
    │
    ▼
  Enrich (dead stock, overstock, ABC, DOS flags)
    │
    ▼
  SQLite (SQLAlchemy)
    │
    ▼
  Dashboard (Streamlit + Plotly + Groq chat)
    │
    ▼
  n8n (automated triggers + Slack/email alerts)
```

## Project Structure

```
inventory-autopilot/
├── main.py                  # ETL orchestrator
├── src/
│   ├── extract.py           # Read Excel (2 sheets)
│   ├── clean.py             # Drop junk rows/cols, flags
│   ├── export.py            # Formatted Excel output (3 sheets)
│   └── anonymize.py         # Anonymize sensitive columns
├── notebooks/
│   ├── 01_eda.ipynb         # Exploratory Data Analysis
│   └── 02_clean.ipynb       # Data cleaning walkthrough
├── docs/
│   └── BUSINESS_RULES.md    # Business rules and tier roadmap
├── data/
│   └── inventory_anon.xlsx  # Anonymized dataset
└── requirements.txt
```

## Quick Start

```bash
git clone https://github.com/Daniel-jcVv/inventory-autopilot.git
cd inventory-autopilot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Input Data

Source: `data/inventory_anon.xlsx` (anonymized ERP export)

| Sheet | Rows | Columns |
|-------|------|---------|
| Inventory by Storeroom | 16,249 | 59 |
| OPEN ORDER | 3,813 | 15 |

## Stack

| Tool | Purpose |
|------|---------|
| pandas + openpyxl | ETL and Excel export |
| SQLite + SQLAlchemy | Database |
| Streamlit + Plotly | Dashboard |
| Groq (Llama 3.3 70B) | AI chat (natural language SQL) |
| FastAPI | REST API |
| n8n | Workflow automation |
| scikit-learn | k-means clustering |
| Prophet | Demand forecasting |

## Roadmap

- [x] EDA notebook
- [x] Data cleaning pipeline
- [ ] Enrichment (ABC, DOS, reorder risk)
- [ ] SQLite database
- [ ] Streamlit dashboard
- [ ] FastAPI endpoint
- [ ] n8n automation workflow
- [ ] ML: demand forecasting + clustering

## License

MIT
