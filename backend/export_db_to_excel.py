"""
Export all AMIS database tables to an Excel file.
Each table is written to its own sheet.
Output: amis_database_export.xlsx  (saved next to this script)
"""

import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "amis.db")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "amis_database_export.xlsx")


def get_all_tables(conn: sqlite3.Connection) -> list[str]:
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    )
    return [row[0] for row in cursor.fetchall()]


def export_to_excel():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    tables = get_all_tables(conn)
    print(f"Found {len(tables)} tables: {tables}\n")

    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        for table in tables:
            try:
                df = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
                # Sheet names are limited to 31 characters in Excel
                sheet_name = table[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"  ✔  {table:40s}  ({len(df)} rows, {len(df.columns)} columns)")
            except Exception as e:
                print(f"  ✘  {table}: {e}")

    conn.close()
    print(f"\nExport complete → {OUTPUT_PATH}")


if __name__ == "__main__":
    export_to_excel()
