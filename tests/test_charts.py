import pandas as pd
import plotly.graph_objects as go
from src.dashboard.charts import (
    chart_abc_value,
    chart_value_by_status,
    chart_treemap_top_items,
    chart_orders_aging,
)


def make_inventory(n=10):
    """Crea DataFrame de inventario sintetico para tests."""
    return pd.DataFrame({
        "abc": ["A"] * 3 + ["B"] * 3 + ["C"] * 4,
        "inventory_value": [1000] * n,
        "dead_stock": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        "overstock": [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        "item_description": [f"Item {i}" for i in range(n)],
        "store_room": ["SR1"] * n,
    })


def make_orders():
    """Crea DataFrame de ordenes sintetico para tests."""
    return pd.DataFrame({
        "age_days": [30, 120, 200, 400, 500],
        "open_value": [100, 200, 300, 400, 500],
        "redundant_order": [0, 1, 0, 1, 1],
    })


def test_chart_abc_value_returns_figure():
    inv = make_inventory()
    fig = chart_abc_value(inv)
    assert isinstance(fig, go.Figure)


def test_chart_abc_value_has_3_bars():
    inv = make_inventory()
    fig = chart_abc_value(inv)
    assert len(fig.data) == 3


def test_chart_value_by_status_returns_figure():
    inv = make_inventory()
    fig = chart_value_by_status(inv)
    assert isinstance(fig, go.Figure)


def test_chart_value_by_status_is_donut():
    inv = make_inventory()
    fig = chart_value_by_status(inv)
    trace = fig.data[0]
    assert trace.hole == 0.45


def test_chart_treemap_returns_figure():
    inv = make_inventory()
    fig = chart_treemap_top_items(inv, top_n=5)
    assert isinstance(fig, go.Figure)


def test_chart_treemap_respects_top_n():
    inv = make_inventory()
    fig = chart_treemap_top_items(inv, top_n=5)
    assert len(fig.data[0].labels) == 5


def test_chart_orders_aging_returns_figure():
    orders = make_orders()
    fig = chart_orders_aging(orders)
    assert isinstance(fig, go.Figure)


def test_chart_orders_aging_has_two_traces():
    """Debe tener 2 traces: Redundante y Valida."""
    orders = make_orders()
    fig = chart_orders_aging(orders)
    assert len(fig.data) == 2
