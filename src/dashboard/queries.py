import pandas as pd
from src.etl.database import get_engine


def load_inventory() -> pd.DataFrame:
    """Lee la tabla inventory completa de SQL Server"""
    engine = get_engine()
    return pd.read_sql("SELECT * FROM inventory", engine)


def load_orders() -> pd.DataFrame:
    """Lee la tabla orders completa de SQL Server"""
    engine = get_engine()
    return pd.read_sql("SELECT * FROM orders", engine)


def load_summary() -> dict:
    """Lee los KPIs del summary y retorna un dict"""
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM summary", engine)
    return df.iloc[0].to_dict()
