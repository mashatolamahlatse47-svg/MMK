import sqlite3
from database import DB_PATH


def add_product(name, cost_price, selling_price, quantity=0, low_stock_level=5):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products
        (name, cost_price, selling_price, quantity, low_stock_level)
        VALUES (?, ?, ?, ?, ?)
    """, (name, cost_price, selling_price, quantity, low_stock_level))

    product_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return product_id


def get_products():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, cost_price, selling_price,
               quantity, low_stock_level
        FROM products
        ORDER BY id
    """)

    products = cursor.fetchall()
    connection.close()

    return products


def get_low_stock_products():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, quantity, low_stock_level
        FROM products
        WHERE quantity <= low_stock_level
        ORDER BY quantity ASC
    """)

    products = cursor.fetchall()
    connection.close()

    return products


if __name__ == "__main__":
    print("MMK PRODUCT MANAGEMENT")
    print("----------------------")

    product_id = add_product(
        name="Test Product",
        cost_price=20,
        selling_price=35,
        quantity=10,
        low_stock_level=5
    )

    print(f"Product added successfully. ID: {product_id}")

    print("\nPRODUCTS:")
    for product in get_products():
        print(product)

    print("\nLOW STOCK:")
    for product in get_low_stock_products():
        print(product)
