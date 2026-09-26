from flask import Flask, jsonify, request
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "mmk_preorder.db"

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db()

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        price REAL NOT NULL CHECK(price >= 0),
        active INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        customer_reference TEXT,
        collection_time TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'NEW',
        total REAL NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        menu_item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK(quantity > 0),
        unit_price REAL NOT NULL CHECK(unit_price >= 0),
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(menu_item_id) REFERENCES menu_items(id)
    );
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM menu_items"
    ).fetchone()[0]

    if count == 0:
        menu = [
            ("Food", "Kota", 0),
            ("Food", "Vetkoek", 0),
            ("Food", "Chips", 0),
            ("Food", "Chicken", 0),
            ("Food", "Pap & Meat", 0),
            ("Drinks", "Drinks", 0),
            ("Cold Drinks", "Cold Drinks", 0),
            ("Beers", "Beer", 0),
            ("Platters", "Platters", 0),
        ]

        conn.executemany(
            """
            INSERT INTO menu_items (category, name, price)
            VALUES (?, ?, ?)
            """,
            menu,
        )

    conn.commit()
    conn.close()

@app.get("/api/health")
def health():
    return jsonify({
        "system": "MMK Pre-Order System",
        "version": "0.1.0",
        "status": "OK"
    })

@app.get("/api/menu")
def menu():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT id, category, name, price
        FROM menu_items
        WHERE active = 1
        ORDER BY category, name
        """
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

@app.get("/api/orders")
def orders():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT id, customer_name, customer_reference,
               collection_time, status, total, created_at
        FROM orders
        ORDER BY id DESC
        """
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5050, debug=False)
