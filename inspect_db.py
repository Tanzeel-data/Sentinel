import sqlite3

DB_PATH = "data/system_telemetry.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""").fetchall()

print("\nTABLES:")
for table in tables:
    print(f" - {table[0]}")

for table in tables:
    table_name = table[0]

    print(f"\n{table_name} COLUMNS:")

    columns = cursor.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    for column in columns:
        print(f"   {column}")

conn.close()