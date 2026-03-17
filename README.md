# Inventory Autopilot

A Tier 1 automotive manufacturer had **$5.6M in dead stock sitting in warehouses** — items purchased but never used. On top of that, **$2.5M in redundant purchase orders** were still open for items already overstocked. Nobody knew because the data was buried across 16,249 rows in ERP Excel exports.

**Inventory Autopilot** is an end-to-end pipeline that turns messy ERP exports into actionable insights — automatically flagging dead stock, overstock, and redundant orders so finance teams can act before capital is wasted.

**[Click here to explore the live dashboard](https://inventory-autopilot-3mlc5ryu4wsxppx26jvbqe.streamlit.app/)**

![Dashboard](docs/dashboard/Peek%202026-03-16%2017-51.gif)

## Key Findings

| Metric | Value |
|--------|-------|
| Dead stock | 3,795 items (23.4%) — **$5.6M** (61.8% of total value) |
| Overstock | 1,234 items — **$1.9M** |
| Redundant orders | 2,538 (66.6%) — **$2.5M** |
| Orders > 1 year old | 209 |

## Features

- **ETL pipeline** — Extract, clean, enrich, and load to SQL Server in one command
- **Smart dashboard** — KPIs, 5 interactive charts, and AI-generated insights per chart
- **AI chat** — Ask questions in natural language, get answers from your data (Groq + Llama 3.3 70B)
- **REST API** — 3 endpoints: health, summary, alerts with enterprise severity levels
- **Automated alerts** — n8n workflow triggers daily: checks severity → sends Gmail + Slack notifications

![Dashboard with AI Chat](docs/dashboard/dashboard_chat_ai.png)

## Automated Alerts

An n8n workflow runs daily: calls the API, evaluates severity, and sends alerts to Gmail and Slack when dead stock exceeds thresholds.

![n8n Workflow](docs/dashboard/workflow_n8n_report_automation.png)

![Email Alert](docs/dashboard/email_automation.png)

## Documentation

- [Setup Guide](docs/SETUP.md) — Installation, configuration, and quick start
- [API Reference](docs/API_REFERENCE.md) — Endpoints, parameters, and responses
- [Architecture & Stack](docs/ARCHITECTURE.md) — System design, data flow, and technology stack
- [Business Rules](docs/BUSINESS_RULES.md) — Detection logic and severity thresholds

## License

MIT
