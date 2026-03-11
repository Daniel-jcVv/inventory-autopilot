import pandas as pd


def drop_sparse_rows(df):
    """Elimina filas con mas de 50 columnas nulas.

    Args:
        df: DataFrame con posibles filas basura del Excel.

    Returns:
        DataFrame sin filas sparse.
    """
    null_per_row = df.isnull().sum(axis=1)
    sparse = null_per_row[null_per_row > 50]
    return df.drop(sparse.index)


def drop_junk_columns(df):
    """Elimina columnas 100%% nulas y Unnamed: 61.

    Args:
        df: DataFrame con posibles columnas basura.

    Returns:
        DataFrame sin columnas junk.
    """
    null_pct = df.isnull().sum() / df.shape[0]
    junk = null_pct[null_pct == 1.0].index.tolist()
    if "Unnamed: 61" in df.columns:
        junk.append("Unnamed: 61")
    return df.drop(columns=junk)


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


def standardize_dates(df, date_columns):
    """Convierte columnas de texto a datetime.

    Valores invalidos quedan como NaT en vez de lanzar error.

    Args:
        df: DataFrame a modificar.
        date_columns: Lista de nombres de columnas a convertir.

    Returns:
        DataFrame con columnas convertidas a datetime.
    """
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df
