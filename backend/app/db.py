import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "fitness.db"

print("BASE_DIR =", BASE_DIR)
print("DB_PATH =", DB_PATH)
print("DB exists? =", DB_PATH.exists())

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn