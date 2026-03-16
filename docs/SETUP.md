# Setup Guide

## Prerequisites

- Python 3.12+
- Docker and Docker Compose
- ODBC Driver 18 for SQL Server

### Install ODBC Driver (Ubuntu/Debian)

```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
sudo add-apt-repository "$(curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list)"
sudo apt update
sudo apt install -y msodbcsql18
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Daniel-jcVv/inventory-autopilot.git
cd inventory-autopilot
```

2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
SA_PASSWORD="YourStrongPassword123!"
GROQ_API_KEY=your_groq_api_key
```

- `SA_PASSWORD` — SQL Server admin password (used by docker-compose)
- `GROQ_API_KEY` — required for the AI chat feature in the dashboard (get one at [console.groq.com](https://console.groq.com))

## Start Services

Start SQL Server and n8n:

```bash
docker compose up -d
```

This starts two containers:

| Service | Port | Description |
|---------|------|-------------|
| SQL Server | 1433 | Database (persistent volume) |
| n8n | 5679 | Workflow automation |

Verify they are running:

```bash
docker ps
```

## Load Data

Run the ETL pipeline to extract, clean, enrich, and load data into SQL Server:

```bash
python main.py
```

Expected output:

```
Extract: 20047 inventory, 3813 orders
Clean: 16249 inventory, 3813 orders
Enrich: flags and KPIs added
Database: {'inventory': 16249, 'orders': 3813, 'summary': 1}
Export: output/inventory_clean.xlsx
```

## Run Components

### Dashboard

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

### API

```bash
uvicorn api:app --port 8001
```

Available at `http://localhost:8001`. See [API_REFERENCE.md](API_REFERENCE.md) for endpoints.

### n8n Workflow

1. Open `http://localhost:5679`
2. Import `workflows/inventory_alerts_daily_report.json` (or it may already be loaded)
3. Configure Gmail and Slack credentials in n8n
4. Activate the workflow

## Stop Services

```bash
docker compose down
```

Data persists in Docker volumes (`sqlserver_data`, `n8n_data`). To remove all data:

```bash
docker compose down -v
```
