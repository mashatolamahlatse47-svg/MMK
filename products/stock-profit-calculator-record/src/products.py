import sqlite3
from database import DB_PATH


def add_product(name, cost_price, selling_price, quantity=0, low_stock_level=5):
    if not name.strip():
        raise ValueError("Product name cannot be empty.")

    if cost_price < 0:
        raise ValueError("Cost price cannot be negative.")

    if selling_price < 0:
        raise ValueError("Selling price cannot be negative.")

    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    if low_stock_level < 0:
        raise ValueError("Low stock level cannot be negative.")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products
        (name, cost_price, selling_price, quantity, low_stock_level)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name.strip(),
        cost_price,
        selling_price,
        quantity,
        low_stock_level
    ))

    product_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return product_id


def get_product(product_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, cost_price, selling_price,
               quantity, low_stock_level
        FROM products
        WHERE id = ?
    """, (product_id,))

    product = cursor.fetchone()
    connection.close()

    return product


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

    print("\nREGISTERED PRODUCTS:")

    products = get_products()

    if not products:
        print("No products registered.")
    else:
        for product in products:
            print(
                f"ID: {product[0]} | "
                f"{product[1]} | "
                f"Cost: R{product[2]:.2f} | "
                f"Selling: R{product[3]:.2f} | "
                f"Stock: {product[4]} | "
                f"Low level: {product[5]}"
            )

    print("\nLOW STOCK:")

    low_stock = get_low_stock_products()

    if not low_stock:
        print("No low-stock products.")
    else:
        for product in low_stock:
            print(
                f"ID: {product[0]} | "
                f"{product[1]} | "
                f"Stock: {product[2]} | "
                f"Warning level: {product[3]}"
            )
