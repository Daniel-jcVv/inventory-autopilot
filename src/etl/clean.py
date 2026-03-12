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
