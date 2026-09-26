import sys
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.engine import SmallBusinessEngine


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        engine = SmallBusinessEngine(db_path)

        business_id = engine.create_business("Test Vetkoek Business")
        product_id = engine.create_product(
            business_id,
            "Vetkoek",
            "each",
            1500,
        )

        batch_id = engine.create_stock_batch(
            business_id,
            product_id,
            "BATCH-001",
            20,
            12000,
        )

        assert batch_id > 0
        assert engine.get_stock(business_id, product_id) == 20

        cash_sale = engine.sell(
            business_id,
            product_id,
            5,
            1500,
            "CASH",
            stock_batch_id=batch_id,
        )

        assert cash_sale > 0
        assert engine.get_stock(business_id, product_id) == 15
        assert engine.get_cash_sales_total(business_id) == 7500

        customer_id = engine.create_customer(
            business_id,
            "Test Customer",
            "0000000000",
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

        assert credit_sale > 0
        assert engine.get_stock(business_id, product_id) == 12
        assert engine.get_credit_sales_total(business_id) == 4500
        assert engine.get_customer_balance(
            business_id,
            customer_id,
        ) == 4500

        with engine.connect() as conn:
            account = conn.execute(
                """
                SELECT id
                FROM credit_accounts
                WHERE sale_id = ?
                """,
                (credit_sale,),
            ).fetchone()

        credit_account_id = account["id"]

        engine.record_payment(
            business_id,
            customer_id,
            credit_account_id,
            2000,
            "CASH",
        )

        assert engine.get_customer_balance(
            business_id,
            customer_id,
        ) == 2500

        print("\n=== ENGINE LOGIC TEST ===")
        print("[OK] Business creation")
        print("[OK] Product creation")
        print("[OK] Stock batch creation")
        print("[OK] Stock movement recorded")
        print("[OK] Cash sale")
        print("[OK] Credit sale")
        print("[OK] Customer debt")
        print("[OK] Partial debt payment")
        print("[OK] Stock decreases correctly")
        print("[OK] Sales remain separate from debt and cash")
        print("\n=== ENGINE LOGIC TEST PASSED ===")


if __name__ == "__main__":
    main()
