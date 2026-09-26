import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "kpi.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def connect():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cost_price REAL NOT NULL DEFAULT 0,
            selling_price REAL NOT NULL DEFAULT 0,
            stock_quantity INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            selling_total REAL NOT NULL,
            cost_total REAL NOT NULL,
            profit REAL NOT NULL,
            payment_type TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS credit_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            sale_id INTEGER,
            amount_owed REAL NOT NULL DEFAULT 0,
            amount_paid REAL NOT NULL DEFAULT 0,
            balance REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'OUTSTANDING',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (sale_id) REFERENCES sales(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_record_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (credit_record_id) REFERENCES credit_records(id)
        );
        """)


if __name__ == "__main__":
    initialize_database()
    print(f"MMK KPI DATABASE READY: {DB_PATH}")
