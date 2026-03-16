from fastapi import FastAPI
from src.dashboard.queries import load_summary, load_inventory

app = FastAPI(title="Inventory Report API")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/summary")
def summary():
    return load_summary()


@app.get("/alerts")
def alerts():
    inv = load_inventory()
    result = {}
    filter_dead_stock = inv[inv["dead_stock"] == 1]
    result["dead_stock"] = {
        "count": len(filter_dead_stock),
        "total_value": int(filter_dead_stock["inventory_value"].sum())
    }
    filter_overstock = inv[inv["overstock"] == 1]
    result["overstock"] = {
        "count": len(filter_overstock),
        "total_value": int(filter_overstock["inventory_value"].sum())
    }
    filter_re_risk = inv[inv["reorder_risk"] == 1]
    result["reorder_risk"] = {
        "count": len(filter_re_risk),
        "total_value": int(filter_re_risk["inventory_value"].sum())
    }
    filter_abc_a = inv[inv["abc"] == "A"]
    result["abc"] = {
        "count": len(filter_abc_a),
        "total_value": int(filter_abc_a["inventory_value"].sum())
    }
    return result

