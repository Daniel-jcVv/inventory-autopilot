from fastapi import FastAPI
from src.dashboard.queries import load_summary
from src.alerts import build_alerts

app = FastAPI(title="Inventory Report API")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/summary")
def summary():
    return load_summary()


@app.get("/alerts")
def alerts():
    return build_alerts()

