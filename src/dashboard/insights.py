"""Genera mensajes inteligentes para cada grafico del dashboard.

Cada funcion analiza los datos filtrados y retorna un dict con:
- diagnosis: que esta pasando (el hallazgo clave)
- action: que deberia hacer el usuario (recomendacion accionable)
"""

import pandas as pd


def _fmt(value: float) -> str:
    """Formatea valor a formato compacto: $1.2M, $54K, $800."""
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def _pct(part: float, total: float) -> str:
    if total == 0:
        return "0%"
    return f"{part / total * 100:.1f}%"


def insight_capital_at_risk(summary: dict) -> dict:
    """Insight para el grafico Capital at Risk.

    Identifica cual categoria de riesgo domina y genera
    una recomendacion especifica basada en los montos.
    """
    categories = {
        "Dead Stock": summary["dead_stock_value"],
        "Overstock": summary.get("overstock_value", 0),
        "Redundant Orders": summary["redundant_value"],
    }
    total = summary["total_value"]
    worst = max(categories, key=categories.get)
    worst_value = categories[worst]

    diagnosis = (
        f"{worst} is the largest risk: "
        f"{_fmt(worst_value)} ({_pct(worst_value, total)} of total value)."
    )

    actions = {
        "Dead Stock": (
            "Review items with no movement for disposal, "
            "liquidation, or transfer to other facilities."
        ),
        "Overstock": (
            "Adjust reorder points and safety stock levels "
            "to prevent excess purchasing."
        ),
        "Redundant Orders": (
            "Cancel or consolidate duplicate open orders "
            "with procurement team."
        ),
    }
    return {"diagnosis": diagnosis, "action": actions[worst]}


def insight_value_by_storeroom(inv: pd.DataFrame) -> dict:
    """Insight para Value by Storeroom."""
    by_room = inv.groupby("store_room")["inventory_value"].sum()
    if by_room.empty:
        return {"diagnosis": "No data available.", "action": ""}

    top_room = by_room.idxmax()
    top_value = by_room.max()
    total = by_room.sum()
    top_pct = top_value / total * 100

    dead_in_top = inv[
        (inv["store_room"] == top_room) & (inv["dead_stock"] == 1)
    ]["inventory_value"].sum()
    dead_pct = dead_in_top / top_value * 100 if top_value > 0 else 0

    diagnosis = (
        f"{top_room} concentrates {_pct(top_value, total)} "
        f"of total inventory value ({_fmt(top_value)})."
    )
    if dead_pct > 30:
        action = (
            f"Audit {top_room} — {dead_pct:.0f}% of its value "
            f"({_fmt(dead_in_top)}) is dead stock."
        )
    elif top_pct > 40:
        action = (
            f"High concentration risk. Consider redistributing "
            f"stock across storerooms."
        )
    else:
        action = "Value distribution is balanced across storerooms."

    return {"diagnosis": diagnosis, "action": action}


def insight_top_items(inv: pd.DataFrame, top_n: int = 10) -> dict:
    """Insight para Top 10 Items by Value."""
    top = inv.nlargest(top_n, "inventory_value")
    total_top_value = top["inventory_value"].sum()
    total_inv = inv["inventory_value"].sum()

    dead_count = (top["dead_stock"] == 1).sum()
    over_count = (top["overstock"] == 1).sum()
    risky = dead_count + over_count

    diagnosis = (
        f"Top {top_n} items hold {_pct(total_top_value, total_inv)} "
        f"of filtered value ({_fmt(total_top_value)}). "
        f"{risky} of {top_n} are flagged (dead stock or overstock)."
    )
    if risky >= 5:
        action = (
            "Most high-value items are at risk. Prioritize review "
            "of these items for disposal or renegotiation."
        )
    elif risky >= 2:
        action = (
            f"Review the {risky} flagged items — they represent "
            f"significant trapped capital."
        )
    else:
        action = "High-value items are mostly healthy."

    return {"diagnosis": diagnosis, "action": action}


def insight_orders_aging(orders: pd.DataFrame) -> dict:
    """Insight para Orders Aging."""
    if orders.empty:
        return {"diagnosis": "No orders data available.", "action": ""}

    old = orders[orders["age_days"] > 365]
    old_count = len(old)
    old_value = old["open_value"].sum()
    total_value = orders["open_value"].sum()

    redundant = orders[orders["redundant_order"] == 1]
    redundant_value = redundant["open_value"].sum()

    diagnosis = (
        f"{old_count} orders older than 1 year "
        f"({_fmt(old_value)}, {_pct(old_value, total_value)} of total). "
        f"Redundant orders: {_fmt(redundant_value)}."
    )
    if old_count > 100:
        action = (
            "Critical backlog. Escalate aged orders for cancellation "
            "or supplier renegotiation."
        )
    elif old_count > 20:
        action = (
            "Review aged orders with procurement — many may no longer "
            "be needed."
        )
    else:
        action = "Order aging is under control."

    return {"diagnosis": diagnosis, "action": action}


def insight_status_by_storeroom(inv: pd.DataFrame) -> dict:
    """Insight para Status Breakdown by Storeroom."""
    inv = inv.copy()
    inv["is_dead"] = inv["dead_stock"] == 1

    by_room = inv.groupby("store_room").agg(
        total_value=("inventory_value", "sum"),
        dead_value=("inventory_value", lambda x: x[inv.loc[x.index, "is_dead"]].sum()),
    )
    by_room["dead_pct"] = (by_room["dead_value"] / by_room["total_value"] * 100).round(1)

    worst = by_room["dead_pct"].idxmax()
    worst_pct = by_room.loc[worst, "dead_pct"]
    worst_value = by_room.loc[worst, "dead_value"]

    diagnosis = (
        f"{worst} has the highest dead stock ratio: "
        f"{worst_pct:.0f}% ({_fmt(worst_value)})."
    )
    if worst_pct > 50:
        action = (
            f"Over half of {worst}'s value is dead stock. "
            f"Conduct physical audit and initiate disposal process."
        )
    elif worst_pct > 30:
        action = (
            f"{worst} needs attention — review slow-moving items "
            f"for potential write-off."
        )
    else:
        action = "Dead stock ratios are manageable across storerooms."

    return {"diagnosis": diagnosis, "action": action}
