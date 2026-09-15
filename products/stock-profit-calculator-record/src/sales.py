import sqlite3
from database import DB_PATH


def record_sale(product_id, quantity):
    if quantity <= 0:
        raise ValueError("Sale quantity must be greater than zero.")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, cost_price, selling_price, quantity
        FROM products
        WHERE id = ?
    """, (product_id,))

    product = cursor.fetchone()

    if product is None:
        connection.close()
        raise ValueError("Product not found.")

    name, cost_price, selling_price, current_stock = product

    if quantity > current_stock:
        connection.close()
        raise ValueError(
            f"Not enough stock. Available stock: {current_stock}"
        )

    total_amount = quantity * selling_price
    profit = quantity * (selling_price - cost_price)
    new_stock = current_stock - quantity

    cursor.execute("""
        UPDATE products
        SET quantity = ?
        WHERE id = ?
    """, (new_stock, product_id))

    cursor.execute("""
        INSERT INTO sales
        (product_id, quantity, selling_price, total_amount, profit)
        VALUES (?, ?, ?, ?, ?)
    """, (
        product_id,
        quantity,
        selling_price,
        total_amount,
        profit
    ))

    connection.commit()
    connection.close()

    return {
        "product_id": product_id,
        "product_name": name,
        "quantity_sold": quantity,
        "selling_price": selling_price,
        "total_amount": total_amount,
        "profit": profit,
        "remaining_stock": new_stock
    }


if __name__ == "__main__":
    print("MMK SALES MODULE")
    print("-----------------")
    print("Sales module loaded successfully.")
    print("No sale was recorded.")
