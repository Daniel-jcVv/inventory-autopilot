import pandas as pd
import plotly.graph_objects as go
from src.dashboard.charts import (
    chart_capital_at_risk,
    chart_value_by_storeroom,
    chart_top_items,
    chart_orders_aging,
    chart_status_by_storeroom,
)


def make_inventory(n=20):
    """Crea DataFrame de inventario sintetico para tests."""
    return pd.DataFrame({
        "item_number": [f"ITM-{i:04d}" for i in range(n)],
        "item_description": [f"Item {i}" for i in range(n)],
        "store_room": ["ROOM-1"] * 10 + ["ROOM-2"] * 10,
        "inventory_value": [1000 * (i + 1) for i in range(n)],
        "dead_stock": [1] * 5 + [0] * 15,
        "overstock": [0] * 5 + [1] * 3 + [0] * 12,
        "balance_on_hand": [10] * n,
        "reorder_risk": [1] * 4 + [0] * 16,
    })


def make_summary():
    """Crea dict de summary sintetico."""
    return {
        "dead_stock_value": 15000,
        "overstock_value": 18000,
        "redundant_value": 5000,
        "total_value": 210000,
    }


def make_orders():
    """Crea DataFrame de ordenes sintetico."""
    return pd.DataFrame({
        "item_number": [f"ITM-{i:04d}" for i in range(8)],
        "age_days": [30, 120, 200, 400, 500, 60, 90, 180],
        "open_value": [100, 200, 300, 400, 500, 150, 250, 350],
        "redundant_order": [0, 1, 0, 1, 1, 0, 0, 1],
    })


# --- Capital at Risk ---

def test_capital_at_risk_returns_figure():
    inv = make_inventory()
    fig = chart_capital_at_risk(inv, make_summary())
    assert isinstance(fig, go.Figure)


def test_capital_at_risk_has_3_bars():
    inv = make_inventory()
    fig = chart_capital_at_risk(inv, make_summary())
    assert len(fig.data[0].y) == 3


# --- Value by Storeroom ---

def test_value_by_storeroom_returns_figure():
    inv = make_inventory()
    fig = chart_value_by_storeroom(inv)
    assert isinstance(fig, go.Figure)


def test_value_by_storeroom_respects_top_n():
    inv = make_inventory()
    fig = chart_value_by_storeroom(inv, top_n=1)
    assert len(fig.data[0].y) == 1


# --- Top Items ---

def test_top_items_returns_figure():
    inv = make_inventory()
    fig = chart_top_items(inv)
    assert isinstance(fig, go.Figure)


def test_top_items_respects_top_n():
    inv = make_inventory()
    fig = chart_top_items(inv, top_n=5)
    assert len(fig.data[0].y) == 5


# --- Orders Aging ---

def test_orders_aging_returns_figure():
    orders = make_orders()
    fig = chart_orders_aging(orders)
    assert isinstance(fig, go.Figure)


def test_orders_aging_has_two_traces():
    orders = make_orders()
    fig = chart_orders_aging(orders)
    assert len(fig.data) == 2


# --- Status by Storeroom ---

def test_status_by_storeroom_returns_figure():
    inv = make_inventory()
    fig = chart_status_by_storeroom(inv)
    assert isinstance(fig, go.Figure)


def test_status_by_storeroom_has_status_traces():
    inv = make_inventory()
    fig = chart_status_by_storeroom(inv)
    trace_names = {t.name for t in fig.data}
    assert "Dead Stock" in trace_names or "Normal" in trace_names
