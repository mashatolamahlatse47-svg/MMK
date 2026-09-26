import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from database import connect, initialize_database
from kpi import get_kpis

initialize_database()

with connect() as db:
    db.execute("DELETE FROM credit_records")
    db.execute("DELETE FROM payments")
    db.execute("DELETE FROM sales")
    db.execute("DELETE FROM customers")
    db.execute("DELETE FROM products")

    product = db.execute(
        "INSERT INTO products (name, cost_price, selling_price, stock_quantity) "
        "VALUES (?, ?, ?, ?)",
        ("Test Product", 20, 35, 10)
    )
    product_id = product.lastrowid

    selling_total = 35 * 2
    cost_total = 20 * 2
    profit = selling_total - cost_total

    sale = db.execute(
        "INSERT INTO sales "
        "(product_id, quantity, selling_total, cost_total, profit, payment_type) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (product_id, 2, selling_total, cost_total, profit, "CREDIT")
    )
    sale_id = sale.lastrowid

    db.execute(
        "UPDATE products SET stock_quantity = stock_quantity - 2 WHERE id = ?",
        (product_id,)
    )

    customer = db.execute(
        "INSERT INTO customers (name) VALUES (?)",
        ("Test Customer",)
    )
    customer_id = customer.lastrowid

    db.execute(
        "INSERT INTO credit_records "
        "(customer_id, sale_id, amount_owed, amount_paid, balance, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (customer_id, sale_id, 70, 0, 70, "OUTSTANDING")
    )

kpis = get_kpis()

expected = {
    "revenue": 70,
    "profit": 30,
    "sales_count": 1,
    "stock": 8,
    "outstanding_credit": 70,
    "expected_money": 70,
}

print("MMK KPI SYSTEM TEST")
print("===================")

passed = True

for key, value in expected.items():
    actual = kpis[key]
    if actual == value:
        print(f"PASS: {key} = {actual}")
    else:
        print(f"FAIL: {key} expected {value}, got {actual}")
        passed = False

if passed:
    print("===================")
    print("KPI TEST: PASS")
else:
    print("===================")
    print("KPI TEST: FAIL")
    raise SystemExit(1)

with connect() as db:
    db.execute("DELETE FROM credit_records")
    db.execute("DELETE FROM sales")
    db.execute("DELETE FROM customers")
    db.execute("DELETE FROM products")
