"""Logica de alertas y severidad para inventario."""

from src.dashboard.queries import load_inventory

SEVERITY_THRESHOLDS = [
    (5, "low"),
    (15, "medium"),
    (25, "high"),
]
DEFAULT_SEVERITY = "critical"


def get_severity(dead_stock_pct: float) -> str:
    """Devuelve severidad basada en % de dead stock sobre valor total."""
    for threshold, level in SEVERITY_THRESHOLDS:
        if dead_stock_pct < threshold:
            return level
    return DEFAULT_SEVERITY


def build_alerts() -> dict:
    """Construye response de alertas con severidad."""
    inv = load_inventory()
    total_value = int(inv["inventory_value"].sum())

    dead = inv[inv["dead_stock"] == 1]
    dead_value = int(dead["inventory_value"].sum())
    if total_value > 0:
        dead_pct = round(dead_value / total_value * 100, 1)
    else:
        dead_pct = 0

    over = inv[inv["overstock"] == 1]
    risk = inv[inv["reorder_risk"] == 1]
    abc_a = inv[inv["abc"] == "A"]

    return {
        "severity": get_severity(dead_pct),
        "dead_stock_pct": dead_pct,
        "total_inventory_value": total_value,
        "dead_stock": {
            "count": len(dead),
            "total_value": dead_value,
        },
        "overstock": {
            "count": len(over),
            "total_value": int(over["inventory_value"].sum()),
        },
        "reorder_risk": {
            "count": len(risk),
            "total_value": int(risk["inventory_value"].sum()),
        },
        "abc": {
            "count": len(abc_a),
            "total_value": int(abc_a["inventory_value"].sum()),
        },
    }
