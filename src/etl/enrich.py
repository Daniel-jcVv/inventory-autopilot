import pandas as pd
import numpy as np


def flag_dead_stock(df):
    """Marca items con stock pero sin uso como dead stock.

    Criterio: Balance On Hand > 0 y Average Daily Usage == 0.

    Args:
        df: DataFrame de inventario con columnas BOH y ADU.

    Returns:
        DataFrame con columna 'Dead Stock' (1/0).
    """
    condition = (df["Balance On Hand"] > 0) & (df["Average Daily Usage"] == 0)
    df["Dead Stock"] = condition.astype(int)
    return df


def flag_overstock(df):
    """Marca items con stock mayor a 12 meses de uso promedio.

    Criterio: BOH > Avg12Mon Usage * 12 y uso > 0.
    Items con uso == 0 son dead stock, no overstock.

    Args:
        df: DataFrame de inventario.

    Returns:
        DataFrame con columna 'Overstock' (1/0).
    """
    has_usage = df["Avg12Mon Usage"] > 0
    excess = df["Balance On Hand"] > (df["Avg12Mon Usage"] * 12)
    df["Overstock"] = (has_usage & excess).astype(int)
    return df


def abc_classification(df: pd.DataFrame) -> pd.DataFrame:
    """Clasifica items por valor acumulado (Pareto 80/20).

    Umbrales: A <= 80%, B <= 95%, C > 95%.

    Returns:
        DataFrame con columna 'ABC' (A/B/C).
    """
    sorted_inv = df.sort_values("Inventory Value", ascending=False)
    sorted_inv["Cumulative Value"] = sorted_inv["Inventory Value"].cumsum()
    total_value = sorted_inv["Inventory Value"].sum()
    sorted_inv["Cumulative pct"] = sorted_inv["Cumulative Value"] / total_value

    # ABC Clasification
    sorted_inv["ABC"] = "C"
    # sobreescribe con B los que acumulan hasta 95%
    sorted_inv.loc[sorted_inv["Cumulative pct"] <= 0.95, "ABC"] = "B"
    sorted_inv.loc[sorted_inv["Cumulative pct"] <= 0.80, "ABC"] = "A"
    # copia la columan ABC del df sorted_inv de regreso al df inv
    df["ABC"] = sorted_inv["ABC"]
    return df


def days_of_supply(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula dias de stock restante por item.

    Formula: BOH / Average Daily Usage. Items sin consumo = inf.

    Returns:
      DataFrame con columna 'DOS'.
    """
    df["DOS"] = np.where(
        df["Average Daily Usage"] > 0,
        df["Balance On Hand"] / df["Average Daily Usage"],
        np.inf # si no que consume, el stock nunca se termina
    )
    return df


def reorder_risk(df: pd.DataFrame) -> pd.DataFrame:
    """Marca items activos con menos de 30 dias de stock.

    Criterio: ADU > 0 y BOH < ADU * 30.

    Returns:
        DataFrame con columna 'Reorder Risk' (1/0).
    """
    active = df["Average Daily Usage"] > 0
    low_stock = df["Balance On Hand"] < (df["Average Daily Usage"] * 30)
    df["Reorder Risk"] = (active & low_stock).astype(int)
    return df


def enrich_orders(df):
    """Agrega columnas de analisis a Open Orders.

    Columnas nuevas:
        - Open Value: Open Qty * Price.
        - Redundant Order: 1 si BOH >= Open Qty.
        - Age Days: dias desde emision hasta la orden mas reciente.

    Args:
        df: DataFrame de ordenes abiertas.

    Returns:
        DataFrame enriquecido.
    """
    df["Open Value"] = df["Open Qty"] * df["Price"]
    df["Redundant Order"] = (df["BOH"] >= df["Open Qty"]).astype(int)

    df["Issue Date"] = pd.to_datetime(df["Issue Date"], errors="coerce")
    last_date = df["Issue Date"].max()
    df["Age Days"] = (last_date - df["Issue Date"]).dt.days

    return df


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica todas las transformaciones de enrichment al inventario."""
    # flags df inventory
    flag_dead_stock(df)
    flag_overstock(df)
    abc_classification(df)
    days_of_supply(df)
    reorder_risk(df)
    return df