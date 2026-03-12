import pandas as pd

FILE_PATH = "data/inventory_anon.xlsx"


def read_data(file_path):
    """Lee las hojas Inventory y Open Orders del Excel crudo.

    Args:
        file_path: Ruta al archivo Excel.

    Returns:
        Tupla (df_inventory, df_orders).
    """
    sheets = pd.read_excel(
        file_path,
        sheet_name=["Inventory by Storeroom", "OPEN ORDER"],
    )
    return sheets["Inventory by Storeroom"], sheets["OPEN ORDER"]
