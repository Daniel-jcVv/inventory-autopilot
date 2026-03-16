# Inventory Autopilot

Automated inventory health pipeline: raw ERP Excel exports → cleaning → analysis → SQL Server → dashboard → API → alerts.

Built with real (anonymized) warehouse data from a Tier 1 automotive manufacturer. Detects **$5.6M in dead stock** and **$2.5M in redundant orders** across 16,249 inventory items.

## Key Findings

| Metric | Value |
|--------|-------|
| Dead stock items | 3,795 (23.4%) — $5.6M (61.8% of total value) |
| Overstock items | 1,234 — $1.9M |
| Redundant orders | 2,538 (66.6%) — $2.5M |
| Reorder risk items | 1,871 — $390K |
| Orders > 1 year old | 209 |

## Features

- **Dead stock detection** — items with stock but zero usage
- **Overstock alerts** — stock exceeding 12 months of demand
- **Redundant order flagging** — open orders where BOH already covers demand
- **ABC classification** — Pareto analysis (80/15/5) on inventory value
- **Days of Supply (DOS)** — stock runway per item
- **Reorder risk** — items with less than 30 days of stock
- **Enterprise severity alerts** — dead stock % thresholds (low/medium/high/critical)
- **Automated alerts** — n8n workflow: Schedule → FastAPI → Gmail + Slack
- **AI chat** — natural language queries over inventory data (Groq + Llama 3.3 70B)

## Architecture

```
ERP Excel export
    |
    v
  Extract (pandas + openpyxl)
    |
    v
  Clean (drop sparse rows/cols, fix dates, flags)
    |
    v
  Enrich (dead stock, overstock, ABC, DOS, reorder risk)
    |
    v
  SQL Server (SQLAlchemy + Docker)
    |
    v
  Dashboard (Streamlit + Plotly + Groq chat)
    |
    +---> FastAPI (/health, /summary, /alerts with severity)
    |         |
    v         v
  Excel    n8n (Schedule Trigger --> HTTP Request --> If severity != low --> Gmail + Slack)
```

## Project Structure

```
inventory-autopilot/
├── main.py                  # ETL orchestrator
├── app.py                   # Streamlit dashboard
├── api.py                   # FastAPI (3 endpoints)
├── docker-compose.yml       # SQL Server + n8n
├── src/
│   ├── extract.py           # Read Excel (2 sheets)
│   ├── clean.py             # Drop junk rows/cols, flags
│   ├── enrich.py            # ABC, DOS, dead stock, overstock, reorder risk
│   ├── alerts.py            # Severity thresholds + alert logic
│   ├── export.py            # Formatted Excel output (3 sheets)
│   ├── database.py          # SQL Server (3 tables)
│   ├── anonymize.py         # Anonymize sensitive columns
│   └── dashboard/
│       ├── queries.py       # SQL queries
│       ├── charts.py        # Plotly charts
│       └── chat.py          # Groq AI chat
├── workflows/
│   └── inventory_alerts_daily_report.json  # n8n workflow
├── notebooks/
│   ├── 01_eda.ipynb         # Exploratory Data Analysis
│   ├── 02_clean.ipynb       # Data cleaning walkthrough
│   ├── 03_enrich.ipynb      # Enrichment logic
│   ├── 04_analytics.ipynb   # Analytics deep dive
│   └── 05_database.ipynb    # Database operations
├── docs/
│   └── BUSINESS_RULES.md    # Business rules and severity thresholds
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
```

Start SQL Server and n8n:

```bash
docker compose up -d
```

Run the ETL pipeline:

```bash
python main.py
```

Launch the dashboard:

```bash
streamlit run app.py
```

Start the API:

```bash
uvicorn api:app --port 8001
```

## Input Data

Source: `data/inventory_anon.xlsx` (anonymized ERP export)

| Sheet | Rows | Columns |
|-------|------|---------|
| Inventory by Storeroom | 16,249 | 61 |
| OPEN ORDER | 3,813 | 18 |

## Stack

| Tool | Purpose |
|------|---------|
| pandas + openpyxl | ETL and Excel export |
| SQL Server + SQLAlchemy | Database (Docker) |
| Streamlit + Plotly | Dashboard |
| Groq (Llama 3.3 70B) | AI chat (natural language SQL) |
| FastAPI + uvicorn | REST API |
| n8n | Workflow automation (Gmail + Slack alerts) |

## Roadmap

- [x] EDA notebook
- [x] Data cleaning pipeline
- [x] Enrichment (ABC, DOS, reorder risk)
- [x] SQL Server database
- [x] Streamlit dashboard + AI chat
- [x] FastAPI API (3 endpoints)
- [x] n8n automation workflow (Gmail + Slack)
- [x] Enterprise severity alerts (thresholds)
- [ ] Dashboard improvements
- [ ] Deploy (Streamlit Cloud + n8n Cloud)

## License

MIT
