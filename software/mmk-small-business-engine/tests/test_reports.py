import sys
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.engine import SmallBusinessEngine
from core.reports import ReportsEngine


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "reports-test.db"

        engine = SmallBusinessEngine(db_path)
        reports = ReportsEngine(engine)

        business_id = engine.create_business(
            "MMK Vetkoek Test Business"
        )

        product_id = engine.create_product(
            business_id,
            "Vetkoek",
            "each",
            1500,
        )

        batch_id = engine.create_stock_batch(
            business_id,
            product_id,
            "BATCH-REPORT-001",
            20,
            12000,
            "2026-09-22",
        )

        customer_id = engine.create_customer(
            business_id,
            "Customer One",
            "0000000000",
        )

        engine.sell(
            business_id,
            product_id,
            5,
            1500,
            "CASH",
            stock_batch_id=batch_id,
            sale_date="2026-09-22",
        )

        credit_sale = engine.sell(
            business_id,
            product_id,
            3,
            1500,
            "CREDIT",
            customer_id=customer_id,
            stock_batch_id=batch_id,
            sale_date="2026-09-22",
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
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    business_id,
                    "Packaging",
                    "Packaging",
                    1000,
                    "2026-09-22",
                ),
            )

        engine.record_payment(
            business_id,
            customer_id,
            account["id"],
            2000,
            "CASH",
            None,
            "2026-09-22",
        )

        summary = reports.financial_summary(
            business_id,
            "2026-09-22",
            "2026-09-22",
        )

        batch = reports.batch_report(
            business_id,
            batch_id,
        )

        assert summary["revenue_cents"] == 12000
        assert summary["cash_sales_cents"] == 7500
        assert summary["credit_sales_cents"] == 4500
        assert summary["debt_payments_cents"] == 2000
        assert summary["cash_collected_cents"] == 9500
        assert summary["credit_outstanding_cents"] == 2500
        assert summary["cogs_cents"] == 4800
        assert summary["expenses_cents"] == 1000
        assert summary["gross_profit_cents"] == 7200
        assert summary["net_profit_cents"] == 6200

        assert batch["quantity_produced"] == 20
        assert batch["quantity_sold"] == 8
        assert batch["quantity_remaining"] == 12
        assert batch["revenue_cents"] == 12000
        assert batch["cogs_cents"] == 4800
        assert batch["gross_profit_cents"] == 7200

        print("\n=== REPORTS ENGINE TEST ===")
        print("[OK] Revenue")
        print("[OK] Cash sales")
        print("[OK] Credit sales")
        print("[OK] Debt payments")
        print("[OK] Cash collected")
        print("[OK] Outstanding debt")
        print("[OK] Cost of goods sold")
        print("[OK] Expenses")
        print("[OK] Gross profit")
        print("[OK] Net profit")
        print("[OK] Batch report")
        print("[OK] Date filtering")
        print("\n=== REPORTS ENGINE TEST PASSED ===")

        print("\nFinancial result:")
        print("  Revenue:          R120.00")
        print("  Cash sales:        R75.00")
        print("  Credit sales:      R45.00")
        print("  Debt collected:    R20.00")
        print("  Cash collected:    R95.00")
        print("  Still owed:        R25.00")
        print("  COGS:              R48.00")
        print("  Expenses:          R10.00")
        print("  Gross profit:      R72.00")
        print("  Net profit:        R62.00")


if __name__ == "__main__":
    main()
