import sqlite3
import shutil

dedicated_path = "reddit_data/2025-05-11_16-48-23/dedicated.db"
generic_path = "reddit_data/2025-05-11_16-48-23/generic.db"
raw_path = "reddit_data/2025-05-11_16-48-23/raw.db"

shutil.copyfile(dedicated_path, raw_path)

conn = sqlite3.connect(raw_path)
cursor = conn.cursor()

cursor.execute(f"ATTACH DATABASE '{generic_path}' AS generic")

cursor.execute("SELECT name FROM generic.sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    cursor.execute(f"INSERT INTO {table} SELECT * FROM generic.{table}")

conn.commit()

cursor.execute("DETACH DATABASE generic")
conn.commit()
conn.close()