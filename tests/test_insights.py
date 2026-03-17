import pandas as pd
from src.dashboard.insights import (
    insight_capital_at_risk,
    insight_value_by_storeroom,
    insight_top_items,
    insight_orders_aging,
    insight_status_by_storeroom,
)


def make_inventory(n=20):
    """Crea DataFrame de inventario sintetico."""
    return pd.DataFrame({
        "item_number": [f"ITM-{i:04d}" for i in range(n)],
        "item_description": [f"Item {i}" for i in range(n)],
        "store_room": ["ROOM-1"] * 10 + ["ROOM-2"] * 10,
        "inventory_value": [1000 * (i + 1) for i in range(n)],
        "dead_stock": [1] * 5 + [0] * 15,
        "overstock": [0] * 5 + [1] * 3 + [0] * 12,
    })


def make_orders():
    """Crea DataFrame de ordenes sintetico."""
    return pd.DataFrame({
        "item_number": [f"ITM-{i:04d}" for i in range(8)],
        "age_days": [30, 120, 200, 400, 500, 60, 90, 180],
        "open_value": [100, 200, 300, 400, 500, 150, 250, 350],
        "redundant_order": [0, 1, 0, 1, 1, 0, 0, 1],
    })


# --- Capital at Risk ---

def test_capital_at_risk_returns_diagnosis_and_action():
    summary = {
        "dead_stock_value": 5600000,
        "overstock_value": 1900000,
        "redundant_value": 2500000,
        "total_value": 9100000,
    }
    result = insight_capital_at_risk(summary)
    assert "diagnosis" in result
    assert "action" in result


def test_capital_at_risk_identifies_worst_category():
    summary = {
        "dead_stock_value": 100,
        "overstock_value": 200,
        "redundant_value": 5000,
        "total_value": 10000,
    }
    result = insight_capital_at_risk(summary)
    assert "Redundant" in result["diagnosis"]


def test_capital_at_risk_action_matches_category():
    summary = {
        "dead_stock_value": 9000,
        "overstock_value": 100,
        "redundant_value": 100,
        "total_value": 10000,
    }
    result = insight_capital_at_risk(summary)
    assert "disposal" in result["action"].lower() or "movement" in result["action"].lower()


# --- Value by Storeroom ---

def test_value_by_storeroom_returns_keys():
    inv = make_inventory()
    result = insight_value_by_storeroom(inv)
    assert "diagnosis" in result
    assert "action" in result


def test_value_by_storeroom_identifies_top_room():
    inv = make_inventory()
    result = insight_value_by_storeroom(inv)
    assert "ROOM-2" in result["diagnosis"]


def test_value_by_storeroom_empty_df():
    inv = pd.DataFrame(columns=["store_room", "inventory_value", "dead_stock"])
    result = insight_value_by_storeroom(inv)
    assert "No data" in result["diagnosis"]


# --- Top Items ---

def test_top_items_returns_keys():
    inv = make_inventory()
    result = insight_top_items(inv)
    assert "diagnosis" in result
    assert "action" in result


def test_top_items_counts_flagged():
    inv = make_inventory()
    result = insight_top_items(inv)
    assert "flagged" in result["diagnosis"]


# --- Orders Aging ---

def test_orders_aging_returns_keys():
    orders = make_orders()
    result = insight_orders_aging(orders)
    assert "diagnosis" in result
    assert "action" in result


def test_orders_aging_detects_old_orders():
    orders = make_orders()
    result = insight_orders_aging(orders)
    assert "older than 1 year" in result["diagnosis"]


def test_orders_aging_empty_df():
    orders = pd.DataFrame(columns=["age_days", "open_value", "redundant_order"])
    result = insight_orders_aging(orders)
    assert "No orders" in result["diagnosis"]


# --- Status by Storeroom ---

def test_status_by_storeroom_returns_keys():
    inv = make_inventory()
    result = insight_status_by_storeroom(inv)
    assert "diagnosis" in result
    assert "action" in result


def test_status_by_storeroom_identifies_worst_room():
    inv = make_inventory()
    result = insight_status_by_storeroom(inv)
    assert "ROOM-1" in result["diagnosis"] or "ROOM-2" in result["diagnosis"]
