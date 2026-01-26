import sqlite3
from tabulate import tabulate

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all table names
tables = cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
).fetchall()

print("=" * 80)
print("DATABASE TABLES AND DATA")
print("=" * 80)

for table in tables:
    table_name = table[0]
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name.upper()}")
    print(f"{'='*80}")
    
    # Get table schema
    schema = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    columns = [col[1] for col in schema]
    
    # Get table data
    rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
    
    if rows:
        data = [list(row) for row in rows]
        print(tabulate(data, headers=columns, tablefmt="grid"))
        print(f"Total records: {len(rows)}")
    else:
        print(f"Table is empty")

conn.close()
print("\n" + "=" * 80)