"""Anonimiza columnas sensibles del Excel crudo.

Reemplaza nombres de plantas, proveedores, items, etc.
con codigos genericos (PLANT-A, SUPPLIER-001, ITEM-00001).
Mantiene consistencia entre hojas (mismo item = mismo codigo).
"""

import pandas as pd
from src.extract import FILE_PATH

ANON_OUTPUT = "data/inventory_anon.xlsx"

# Columnas a anonimizar por hoja
INV_COLUMNS = {
    "Operation Name": "OP",
    "Plant Code": "PLCODE",
    "Plant Name": "PLANT",
    "Store Room": "ROOM",
    "Item Number": "ITEM",
    "Item Description": "ITEM-DESC",
    "Manufacturer Code": "MFG-CODE",
    "Manufacturer Name": "MFG",
    "Manufacturer Part": "MFG-PART",
}

ORD_COLUMNS = {
    "Plant Code": "PLCODE",
    "Item Number": "ITEM",
    "Item Description": "ITEM-DESC",
    "PO Number": "PO",
    "Supplier Code": "SUP-CODE",
    "Supplier Name": "SUPPLIER",
    "Vendor PO": "VPO",
}


def _build_mapping(series, prefix):
    """Crea diccionario de valores unicos a codigos genericos.

    Args:
        series: Serie de pandas con valores a anonimizar.
        prefix: Prefijo para los codigos (ej: "ITEM" -> "ITEM-00001").

    Returns:
        Dict {valor_original: codigo_generico}.
    """
    unique_vals = series.dropna().unique()
    pad = len(str(len(unique_vals)))
    return {val: f"{prefix}-{str(i+1).zfill(pad)}" for i, val in enumerate(unique_vals)}


def anonymize(inv, orders):
    """Anonimiza columnas sensibles en ambos DataFrames.

    Usa mapeos compartidos para Item Number e Item Description
    para mantener consistencia entre hojas.

    Args:
        inv: DataFrame de inventario.
        orders: DataFrame de ordenes abiertas.

    Returns:
        Tupla (inv_anon, orders_anon).
    """
    inv = inv.copy()
    orders = orders.copy()

    # Mapeos compartidos (Item Number, Item Description)
    shared_cols = {
        "Plant Code": "PLCODE",
        "Item Number": "ITEM",
        "Item Description": "ITEM-DESC",
    }
    shared_mappings = {}
    for col, prefix in shared_cols.items():
        combined = pd.concat([inv[col], orders[col]]).dropna().unique()
        pad = len(str(len(combined)))
        shared_mappings[col] = {
            val: f"{prefix}-{str(i+1).zfill(pad)}" for i, val in enumerate(combined)
        }

    # Anonimizar inventario
    for col, prefix in INV_COLUMNS.items():
        if col not in inv.columns:
            continue
        if col in shared_mappings:
            mapping = shared_mappings[col]
        else:
            mapping = _build_mapping(inv[col], prefix)
        inv[col] = inv[col].map(mapping)

    # Anonimizar ordenes
    for col, prefix in ORD_COLUMNS.items():
        if col not in orders.columns:
            continue
        if col in shared_mappings:
            mapping = shared_mappings[col]
        else:
            mapping = _build_mapping(orders[col], prefix)
        orders[col] = orders[col].map(mapping)

    return inv, orders


def export_anon(inv, orders, output_path=ANON_OUTPUT):
    """Guarda Excel anonimizado con las 2 hojas originales.

    Args:
        inv: DataFrame de inventario anonimizado.
        orders: DataFrame de ordenes anonimizado.
        output_path: Ruta del archivo de salida.

    Returns:
        Ruta del archivo exportado.
    """
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        inv.to_excel(writer, sheet_name="Inventory by Storeroom", index=False)
        orders.to_excel(writer, sheet_name="OPEN ORDER", index=False)
    return output_path


if __name__ == "__main__":
    sheets = pd.read_excel(
        FILE_PATH,
        sheet_name=["Inventory by Storeroom", "OPEN ORDER"],
    )
    inv = sheets["Inventory by Storeroom"]
    orders = sheets["OPEN ORDER"]

    inv_anon, orders_anon = anonymize(inv, orders)
    path = export_anon(inv_anon, orders_anon)

    print(f"Inventory: {inv_anon.shape}")
    print(f"Orders:    {orders_anon.shape}")
    print(f"Exported:  {path}")
