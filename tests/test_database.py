from sqlalchemy import text
from src.etl.database import get_engine, normalize_columns, build_summary, save_to_db, verify_integrity
import pandas as pd


def test_connection():
    """Verifica que python conecta a SQL Sever"""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_normalize_columns():
    """Verifica que los nombres se limpian correctamente"""
    df = pd.DataFrame({"Balance On Hand": [1], " Price ": [2]})
    result = normalize_columns(df)
    assert list(result.columns) == ["balance_on_hand", "price"]


def test_build_summary():
    """Verifica que build_summary genera los 12 kpis"""
    inv = pd.DataFrame({
        "inventory_value": [100, 200, 300],
        "dead_stock": [1, 0, 0],
        "overstock": [0, 1, 0],
        "reorder_risk": [0, 0, 1],
    })
    orders = pd.DataFrame({
        "open_value": [50, 60],
        "redundant_order": [1, 0],
        "age_days": [400, 100],
    })
    result = build_summary(inv=inv, orders=orders)
    assert result.shape == (1, 12)
    assert result["total_items"][0] == 3
    assert result["dead_stock_value"][0] == 100
    assert result["orders_over_1yr"][0] == 1


def test_save_to_db():
    """Verifica que las 3 tablas se crean en SQL Server."""
    inv = pd.DataFrame({
        "Balance On Hand": [10, 20],
        "Inventory Value": [100, 200],
        "Average Daily Usage": [0, 1],
        "Avg12Mon Usage": [0, 5],
        "Dead Stock": [1, 0],
        "Overstock": [0, 0],
        "Reorder Risk": [0, 1],
    })
    orders = pd.DataFrame({
        "Open Value": [50],
        "Redundant Order": [1],
        "Age Days": [400],
    })
    engine = get_engine()
    result = save_to_db(inv, orders, engine)

    assert result["inventory"] == 2
    assert result["orders"] == 1
    assert result["summary"] == 1

    with engine.connect() as conn:
        tables = conn.execute(text(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_TYPE='BASE TABLE'"
        ))
        table_names = [row[0] for row in tables]
        assert "inventory" in table_names
        assert "orders" in table_names
        assert "summary" in table_names


def test_verify_integrity():                                                             
    """Verifica que los conteos en SQL Server coinciden con pandas."""
    inv = pd.DataFrame({                                                                 
        "Balance On Hand": [10],        
        "Inventory Value": [100],           
        "Average Daily Usage": [0],                                                      
        "Avg12Mon Usage": [0],          
        "Dead Stock": [1],                                                               
        "Overstock": [0],                                                                
        "Reorder Risk": [0],                                                             
    })                                                                                   
    orders = pd.DataFrame({             
        "Open Value": [50],                                                              
        "Redundant Order": [1],                                                          
        "Age Days": [400],
    })                                                                                   
    engine = get_engine()             
    save_to_db(inv, orders, engine)
    result = verify_integrity(inv, orders, engine)                                       
                                            
    assert result["inventory"] == 1                                                     
    assert result["orders"] == 1       
    assert result["summary"] == 1


