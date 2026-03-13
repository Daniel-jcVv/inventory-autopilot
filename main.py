"""Orquestador ETL: Excel crudo -> limpieza -> enrichment -> SQL Server -> Excel."""

from src.etl import (
    read_data,
    FILE_PATH,
    drop_sparse_rows,
    drop_junk_columns,
    standardize_dates,
    enrich,
    enrich_orders,
    export_clean_excel,
    get_engine,
    save_to_db,
    verify_integrity,
)

DATE_COLUMNS_INV = ["Item Creation Date", "Last Used", "Last Recieved", "Last Modified"]
DATE_COLUMNS_ORDERS = ["Issue Date", "Required Date ", "Last Modified"]


def run():
    """Ejecuta el pipeline completo."""
    # 1. Extract
    inv, orders = read_data(FILE_PATH)
    print(f"Extract: {len(inv)} inventory, {len(orders)} orders")

    # 2. Clean
    inv = drop_sparse_rows(inv)
    inv = drop_junk_columns(inv)
    orders = drop_sparse_rows(orders)
    orders = drop_junk_columns(orders)
    inv = standardize_dates(inv, DATE_COLUMNS_INV)
    orders = standardize_dates(orders, DATE_COLUMNS_ORDERS)
    print(f"Clean: {len(inv)} inventory, {len(orders)} orders")

    # 3. Enrich
    inv = enrich(inv)
    orders = enrich_orders(orders)
    print(f"Enrich: flags and KPIs added")

    # 4. Database
    engine = get_engine()
    counts = save_to_db(inv, orders, engine)
    verify_integrity(inv, orders, engine)
    print(f"Database: {counts}")

    # 5. Export
    path = export_clean_excel(inv, orders)
    print(f"Export: {path}")


if __name__ == "__main__":
    run()
