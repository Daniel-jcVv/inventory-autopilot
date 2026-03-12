from src.etl.extract import read_data, FILE_PATH
from src.etl.clean import drop_sparse_rows, drop_junk_columns, standardize_dates
from src.etl.enrich import enrich, enrich_orders
from src.etl.export import export_clean_excel



if __name__ == "__main__":
    inv, orders = read_data(FILE_PATH)

    # Limpieza
    inv = drop_sparse_rows(inv)
    inv = drop_junk_columns(inv)
    orders = drop_sparse_rows(orders)
    orders = drop_junk_columns(orders)

    # Fechas
    inv = standardize_dates(
        inv, ["Item Creation Date", "Last Used", "Last Recieved", "Last Modified"]
    )
    orders = standardize_dates(
        orders, ["Issue Date", "Required Date ", "Last Modified"]
    )

    # Enriquecimiento
    inv = flag_dead_stock(inv)
    inv = flag_overstock(inv)
    orders = enrich_orders(orders)

    # Export
    path = export_clean_excel(inv, orders)

    print(f"Inventory: {inv.shape}")
    print(f"Orders:    {orders.shape}")
    print(f"Dead stock:       {inv['Dead Stock'].sum()}")
    print(f"Overstock:        {inv['Overstock'].sum()}")
    print(f"Redundant orders: {orders['Redundant Order'].sum()}")
    print(f"Exported: {path}")
