from unittest.mock import patch
from fastapi.testclient import TestClient
import pandas as pd
from api import app

client = TestClient(app)


def make_fake_inventory():
    """DataFrame sintetico que simula load_inventory()."""
    return pd.DataFrame({
        "dead_stock": [1, 1, 0, 0, 0],
        "overstock": [0, 0, 1, 0, 0],
        "reorder_risk": [0, 0, 0, 1, 1],
        "abc": ["A", "B", "A", "C", "A"],
        "inventory_value": [1000, 2000, 3000, 4000, 5000],
    })


def make_fake_summary():
    """Dict sintetico que simula load_summary()."""
    return {"total_items": 100, "total_value": 50000}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("api.load_summary", return_value=make_fake_summary())
def test_summary(mock_summary):
    response = client.get("/summary")
    assert response.status_code == 200
    assert response.json() == {"total_items": 100, "total_value": 50000}


@patch("api.load_inventory", return_value=make_fake_inventory())
def test_alerts_keys(mock_inv):
    response = client.get("/alerts")
    data = response.json()
    assert set(data.keys()) == {"dead_stock", "overstock", "reorder_risk", "abc"}


@patch("api.load_inventory", return_value=make_fake_inventory())
def test_alerts_counts(mock_inv):
    response = client.get("/alerts")
    data = response.json()
    assert data["dead_stock"]["count"] == 2
    assert data["overstock"]["count"] == 1
    assert data["reorder_risk"]["count"] == 2
    assert data["abc"]["count"] == 3
    


@patch("api.load_inventory", return_value=make_fake_inventory())
def test_alerts_values(mock_inv):
    response = client.get("/alerts")
    data = response.json()
    assert data["dead_stock"]["total_value"] == 3000
    assert data["overstock"]["total_value"] == 3000
    assert data["reorder_risk"]["total_value"] == 9000
    assert data["abc"]["total_value"] == 9000
    
