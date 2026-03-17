"""Carga datos para el dashboard.

Intenta SQL Server primero. Si no esta disponible, lee del Excel
anonimizado y ejecuta clean + enrich en memoria (modo demo).
"""

import pandas as pd

_DEMO_MODE = None


def _is_db_available() -> bool:
    """Verifica si SQL Server esta disponible."""
    global _DEMO_MODE
    if _DEMO_MODE is not None:
        return not _DEMO_MODE
    try:
        from src.etl.database import get_engine
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(pd.io.sql.text("SELECT 1"))
        _DEMO_MODE = False
        return True
    except Exception:
        _DEMO_MODE = True
        return False


def _load_from_db(query: str) -> pd.DataFrame:
    """Lee de SQL Server."""
    from src.etl.database import get_engine
    engine = get_engine()
    return pd.read_sql(query, engine)


def _load_from_excel() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lee del Excel anonimizado y ejecuta clean + enrich."""
    from src.etl import (
        read_data,
        drop_sparse_rows,
        drop_junk_columns,
        standardize_dates,
        enrich,
        enrich_orders,
    )
    from src.etl.database import normalize_columns, build_summary

    path = "data/inventory_anon.xlsx"
    inv, orders = read_data(path)

    date_cols_inv = ["Item Creation Date", "Last Used", "Last Recieved", "Last Modified"]
    date_cols_orders = ["Issue Date", "Required Date ", "Last Modified"]

    inv = drop_sparse_rows(inv)
    inv = drop_junk_columns(inv)
    orders = drop_sparse_rows(orders)
    orders = drop_junk_columns(orders)
    inv = standardize_dates(inv, date_cols_inv)
    orders = standardize_dates(orders, date_cols_orders)
    inv = enrich(inv)
    orders = enrich_orders(orders)

    inv = normalize_columns(inv)
    orders = normalize_columns(orders)
    summary = build_summary(inv, orders)

    return inv, orders, summary


_cache = {}


def _get_demo_data():
    """Cachea datos del Excel para no re-procesar en cada llamada."""
    if "inv" not in _cache:
        inv, orders, summary = _load_from_excel()
        _cache["inv"] = inv
        _cache["orders"] = orders
        _cache["summary"] = summary
    return _cache["inv"], _cache["orders"], _cache["summary"]


def is_demo_mode() -> bool:
    """Retorna True si estamos en modo demo (sin DB)."""
    _is_db_available()
    return _DEMO_MODE


def load_inventory() -> pd.DataFrame:
    """Lee la tabla inventory."""
    if _is_db_available():
        return _load_from_db("SELECT * FROM inventory")
    inv, _, _ = _get_demo_data()
    return inv


def load_orders() -> pd.DataFrame:
    """Lee la tabla orders."""
    if _is_db_available():
        return _load_from_db("SELECT * FROM orders")
    _, orders, _ = _get_demo_data()
    return orders


def load_summary() -> dict:
    """Lee los KPIs del summary y retorna un dict."""
    if _is_db_available():
        from src.etl.database import get_engine
        engine = get_engine()
        df = pd.read_sql("SELECT * FROM summary", engine)
        return df.iloc[0].to_dict()
    _, _, summary = _get_demo_data()
    return summary.iloc[0].to_dict()
