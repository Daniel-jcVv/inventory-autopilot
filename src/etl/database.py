import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

load_dotenv()


def get_engine():
    """Crea conexion a SQL Server en Docker.

    Lee la contraseña de la variable de entorno SA_PASSWORD.

    Returns:
        Engine de SQLAlchemy conectado a SQL Server.
    """
    password = os.environ["SA_PASSWORD"]
    return create_engine(
        f"mssql+pyodbc://sa:{password}@localhost:1433/master"
        "?driver=ODBC+Driver+18+for+SQL+Server"                                          
        "&TrustServerCertificate=yes"  
    )


def normalize_columns(df):
    """Convierte nombres de columnas a minusculas con guion bajo.

    Args:
        df: DataFrame con columnas a normalizar.

    Returns:
        DataFrame con columnas en formato snake_case.
    """
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def build_summary(inv, orders):
    """Calcula KPIs del inventario y ordenes.

    Genera 12 metricas pre-calculadas para el dashboard.

    Args:
        inv: DataFrame de inventario con columnas normalizadas.
        orders: DataFrame de ordenes con columnas normalizadas.

    Returns:
        DataFrame de 1 fila con 12 KPIs.
    """
    summary = {                             
        "total_items": [len(inv)],      
        "total_value": [round(inv["inventory_value"].sum(), 0)],                         
        "dead_stock_items": [int(inv["dead_stock"].sum())],                              
        "dead_stock_value": [round(inv.loc[inv["dead_stock"] == 1, "inventory_value"].sum(), 0)],                                                                              
        "overstock_items": [int(inv["overstock"].sum())],                                
        "overstock_value": [round(inv.loc[inv["overstock"] == 1, "inventory_value"].sum(), 0)],                                                                              
        "reorder_risk_items": [int(inv["reorder_risk"].sum())],                          
        "reorder_risk_value": [round(inv.loc[inv["reorder_risk"] == 1, "inventory_value"].sum(), 0)],                                 
        "total_orders": [len(orders)],                                                   
        "redundant_orders": [int(orders["redundant_order"].sum())],
        "redundant_value": [round(orders.loc[orders["redundant_order"] == 1, "open_value"].sum(), 0)],                                                                              
        "orders_over_1yr": [int((orders["age_days"] > 365).sum())],                      
    }                                                                                    
    return pd.DataFrame(summary)


def save_to_db(inv, orders, engine):
    """Guarda inventory, orders y summary en SQL Server.

    Normaliza columnas, calcula summary y guarda las 3 tablas.

    Args:
        inv: DataFrame de inventario crudo.
        orders: DataFrame de ordenes crudo.
        engine: Engine de SQLAlchemy.

    Returns:
        Diccionario con filas guardadas por tabla.
    """
    inv = normalize_columns(inv)
    orders = normalize_columns(orders)
    summary = build_summary(inv, orders)

    inv.to_sql("inventory", engine, if_exists="replace", index=False)
    orders.to_sql("orders", engine, if_exists="replace", index=False)
    summary.to_sql("summary", engine, if_exists="replace", index=False)

    return {"inventory": len(inv), "orders": len(orders), "summary": 1}


def verify_integrity(inv, orders, engine):
    """Compara filas en SQL Server vs DataFrames originales.

    Lanza ValueError si algun conteo no coincide.

    Args:
        inv: DataFrame de inventario original.
        orders: DataFrame de ordenes original.
        engine: Engine de SQLAlchemy.

    Returns:
        Diccionario con conteos esperados por tabla.
    """
    expected = {"inventory": len(inv), "orders": len(orders), "summary": 1}
    with engine.connect() as conn:
        for table, count in expected.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            db_count = result.scalar()
            if db_count != count:
                raise ValueError(
                    f"Tabla '{table}': esperado {count}, encontrado {db_count}"
                )
    return expected