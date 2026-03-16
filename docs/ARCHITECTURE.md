# Architecture

## Overview

Inventory Autopilot is an end-to-end inventory health pipeline that processes raw ERP Excel exports into actionable alerts. The system follows a layered architecture separating data processing, storage, presentation, and automation.

```
+-------------------+
|   Data Source      |   Excel export from ERP (2 sheets: Inventory + Open Orders)
+--------+----------+
         |
         v
+--------+----------+
|   ETL Pipeline     |   extract.py --> clean.py --> enrich.py --> export.py
|   (main.py)        |   Orchestrates the full pipeline
+--------+----------+
         |
         v
+--------+----------+
|   SQL Server       |   3 tables: inventory, orders, summary
|   (Docker)         |   Persistent volume, accessed via SQLAlchemy + pyodbc
+--------+----------+
         |
    +----+----+
    |         |
    v         v
+---+---+ +---+------+
| API   | | Dashboard |
| (Fast | | (Stream  |
|  API) | |  lit)    |
+---+---+ +---+------+
    |         |
    v         v
+---+---+ +---+------+
| n8n   | | AI Chat  |
| alerts| | (Groq)   |
+-------+ +----------+
```

## Design Decisions

### SQL Server over SQLite

SQLite was used during development for simplicity. Production uses SQL Server because:

- Mirrors real enterprise environments (the source data comes from an ERP system backed by SQL Server)
- Supports concurrent access from the dashboard, API, and n8n simultaneously
- Docker makes it easy to run locally with `docker compose up -d`

### Service Layer for Alerts (src/alerts.py)

Alert logic lives in `src/alerts.py`, not in `api.py`. This separation means:

- Business rules (severity thresholds) are independent of the HTTP layer
- The same logic can be reused by the dashboard, CLI, or any future consumer
- Thresholds are easy to adjust without touching API code

### Severity Thresholds

Dead stock severity is based on industry benchmarks for inventory health:

| Level | Dead Stock % | Severity |
|-------|-------------|----------|
| Healthy | < 5% | low |
| Warning | 5-15% | medium |
| Critical | 15-25% | high |
| Not competitive | > 25% | critical |

Source: industry standards where companies with >25-30% dead stock are considered not competitive.

### n8n over Airflow/Cron

n8n was chosen for workflow automation because:

- Visual workflow builder makes the automation logic transparent
- Built-in nodes for Gmail, Slack, HTTP Request (no custom code needed)
- Self-hosted via Docker (runs alongside SQL Server in the same docker-compose)
- Low resource footprint compared to Airflow

### Groq over OpenAI

The AI chat feature uses Groq (Llama 3.3 70B) instead of OpenAI because:

- Free tier is generous enough for a portfolio project
- Fast inference (Groq's LPU architecture)
- No vendor lock-in to proprietary models

## Data Flow

### ETL Pipeline (main.py)

```
1. Extract  -->  Read 2 sheets from Excel (pandas + openpyxl)
2. Clean    -->  Drop sparse rows/cols, fix dates, normalize columns
3. Enrich   -->  Add flags: dead_stock, overstock, ABC, DOS, reorder_risk
4. Database -->  Write 3 tables to SQL Server (inventory, orders, summary)
5. Export   -->  Formatted Excel with 3 sheets (inventory, orders, summary)
```

### Alert Flow (n8n)

```
1. Schedule Trigger  -->  Fires daily at 8:00 AM (America/Mexico_City)
2. HTTP Request      -->  GET http://host.docker.internal:8001/alerts
3. If                -->  severity != "low"
4. Gmail + Slack     -->  Send alert with inventory breakdown
```

## File Responsibilities

| File | Layer | Responsibility |
|------|-------|----------------|
| main.py | Orchestration | Runs ETL pipeline end-to-end |
| api.py | Presentation | HTTP endpoints (thin layer, delegates to services) |
| app.py | Presentation | Streamlit dashboard |
| src/extract.py | Data | Read Excel source |
| src/clean.py | Data | Data cleaning and normalization |
| src/enrich.py | Data | Business flags and KPIs |
| src/alerts.py | Service | Alert logic and severity classification |
| src/database.py | Data | SQL Server read/write |
| src/export.py | Data | Formatted Excel output |
| src/dashboard/queries.py | Data | SQL queries for dashboard |
| src/dashboard/charts.py | Presentation | Plotly chart builders |
| src/dashboard/chat.py | Service | Groq AI chat integration |
