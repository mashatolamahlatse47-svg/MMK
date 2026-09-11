import sqlite3
from database import DB_PATH


def get_stock(product_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT quantity FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()
    connection.close()

    if product is None:
        raise ValueError("Product not found.")

    return product[0]


def add_stock(product_id, quantity):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT quantity FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        connection.close()
        raise ValueError("Product not found.")

    new_quantity = product[0] + quantity

    cursor.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (new_quantity, product_id)
    )

    cursor.execute("""
        INSERT INTO stock_records
        (product_id, quantity, action)
        VALUES (?, ?, ?)
    """, (product_id, quantity, "STOCK_IN"))

    connection.commit()
    connection.close()

    return new_quantity


def remove_stock(product_id, quantity):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT quantity FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        connection.close()
        raise ValueError("Product not found.")

    if product[0] < quantity:
        connection.close()
        raise ValueError("Not enough stock.")

    new_quantity = product[0] - quantity

    cursor.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (new_quantity, product_id)
    )

    cursor.execute("""
        INSERT INTO stock_records
        (product_id, quantity, action)
        VALUES (?, ?, ?)
    """, (product_id, quantity, "STOCK_OUT"))

    connection.commit()
    connection.close()

    return new_quantity


if __name__ == "__main__":
    print("MMK STOCK MANAGEMENT")
    print("--------------------")

    current_stock = get_stock(1)

    print(f"Product ID: 1")
    print(f"Current stock: {current_stock}")

    print("\nStock functions are ready.")
    print("No stock was changed by this test.")
