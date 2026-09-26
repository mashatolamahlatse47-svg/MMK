import sys
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.engine import SmallBusinessEngine
from core.profit import ProfitEngine


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "profit-test.db"

        engine = SmallBusinessEngine(db_path)
        profit = ProfitEngine(engine)

        business_id = engine.create_business("Profit Test Business")

        product_id = engine.create_product(
            business_id,
            "Vetkoek",
            "each",
            1500,
        )

        batch_id = engine.create_stock_batch(
            business_id,
            product_id,
            "BATCH-PROFIT-001",
            20,
            12000,
        )

        customer_id = engine.create_customer(
            business_id,
            "Credit Customer",
        )

        engine.sell(
            business_id,
            product_id,
            5,
            1500,
            "CASH",
            stock_batch_id=batch_id,
        )

        credit_sale = engine.sell(
            business_id,
            product_id,
            3,
            1500,
            "CREDIT",
            customer_id=customer_id,
            stock_batch_id=batch_id,
        )

        with engine.connect() as conn:
            account = conn.execute(
                """
                SELECT id
                FROM credit_accounts
                WHERE sale_id = ?
                """,
                (credit_sale,),
            ).fetchone()

            conn.execute(
                """
                INSERT INTO expenses
                    (
                        business_id,
                        category,
                        description,
                        amount_cents,
                        expense_date
                    )
                VALUES (?, ?, ?, ?, date('now'))
                """,
                (
                    business_id,
                    "Packaging",
                    "Test packaging expense",
                    1000,
                ),
            )

        engine.record_payment(
            business_id,
            customer_id,
            account["id"],
            2000,
        )

        summary = profit.batch_summary(
            business_id,
            batch_id,
        )

        business = profit.business_summary(
            business_id,
        )

        assert summary["quantity_produced"] == 20
        assert summary["quantity_sold"] == 8
        assert summary["quantity_remaining"] == 12

        assert summary["revenue_cents"] == 12000
        assert summary["cost_of_goods_sold_cents"] == 4800
        assert summary["gross_profit_cents"] == 7200

        assert business["revenue_cents"] == 12000
        assert business["cash_collected_cents"] == 9500
        assert business["credit_outstanding_cents"] == 2500
        assert business["expenses_cents"] == 1000

        print("\n=== PROFIT ENGINE TEST ===")
        print("[OK] Production quantity")
        print("[OK] Units sold")
        print("[OK] Units remaining")
        print("[OK] Sales revenue")
        print("[OK] Cost of goods sold")
        print("[OK] Gross profit")
        print("[OK] Cash collected")
        print("[OK] Outstanding credit")
        print("[OK] Expenses")
        print("[OK] Profit does not confuse revenue with cash")
        print("\n=== PROFIT ENGINE TEST PASSED ===")
        print("\nExpected batch result:")
        print("  Produced:        20 units")
        print("  Sold:             8 units")
        print("  Remaining:       12 units")
        print("  Revenue:         R120.00")
        print("  Production COGS: R48.00")
        print("  Gross profit:    R72.00")
        print("  Cash collected:  R95.00")
        print("  Still owed:      R25.00")
        print("  Expense:         R10.00")


if __name__ == "__main__":
    main()
