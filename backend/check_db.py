import sqlite3

conn = sqlite3.connect('amis.db')
cursor = conn.cursor()

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('=== DATABASE ANALYSIS ===\n')
print(f'Total Tables: {len(tables)}\n')

for table in tables:
    table_name = table[0]
    count = cursor.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
    print(f'{table_name}: {count} records')

conn.close()
