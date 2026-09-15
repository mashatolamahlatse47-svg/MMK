import sqlite3
from database import DB_PATH


def get_sales_report():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            sales.id,
            products.name,
            sales.quantity,
            sales.selling_price,
            sales.total_amount,
            sales.profit,
            sales.created_at
        FROM sales
        JOIN products
            ON sales.product_id = products.id
        ORDER BY sales.id DESC
    """)

    sales = cursor.fetchall()
    connection.close()

    return sales


def get_sales_totals():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COALESCE(SUM(quantity), 0),
            COALESCE(SUM(total_amount), 0),
            COALESCE(SUM(profit), 0)
        FROM sales
    """)

    totals = cursor.fetchone()
    connection.close()

    return {
        "quantity_sold": totals[0],
        "revenue": totals[1],
        "profit": totals[2]
    }


if __name__ == "__main__":
    print("MMK SALES REPORT")
    print("=================")

    sales = get_sales_report()

    if not sales:
        print("No sales recorded.")
    else:
        print("\nSALES HISTORY")
        print("-------------")

        for sale in sales:
            print(
                f"Sale ID: {sale[0]} | "
                f"Product: {sale[1]} | "
                f"Qty: {sale[2]} | "
                f"Revenue: R{sale[4]:.2f} | "
                f"Profit: R{sale[5]:.2f} | "
                f"Date: {sale[6]}"
            )

    totals = get_sales_totals()

    print("\nTOTALS")
    print("------")
    print(f"Quantity sold: {totals['quantity_sold']}")
    print(f"Revenue:      R{totals['revenue']:.2f}")
    print(f"Profit:       R{totals['profit']:.2f}")
