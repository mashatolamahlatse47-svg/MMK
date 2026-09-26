from database import connect


def get_kpis():
    with connect() as db:
        revenue = db.execute(
            "SELECT COALESCE(SUM(selling_total), 0) FROM sales"
        ).fetchone()[0]

        profit = db.execute(
            "SELECT COALESCE(SUM(profit), 0) FROM sales"
        ).fetchone()[0]

        sales_count = db.execute(
            "SELECT COUNT(*) FROM sales"
        ).fetchone()[0]

        stock = db.execute(
            "SELECT COALESCE(SUM(stock_quantity), 0) FROM products"
        ).fetchone()[0]

        credit = db.execute(
            "SELECT COALESCE(SUM(balance), 0) "
            "FROM credit_records "
            "WHERE status = 'OUTSTANDING'"
        ).fetchone()[0]

        return {
            "revenue": revenue,
            "profit": profit,
            "sales_count": sales_count,
            "stock": stock,
            "outstanding_credit": credit,
            "expected_money": credit,
        }


if __name__ == "__main__":
    print("MMK KPI ENGINE CHECK")
    print("====================")

    for name, value in get_kpis().items():
        print(f"{name}: {value}")
