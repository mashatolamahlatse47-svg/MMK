import sys
import tempfile
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_ROOT / "core"))

from engine import SmallBusinessEngine


print("=== SECURITY + AUDIT TEST ===")

with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / "security_test.db"
    engine = SmallBusinessEngine(db)

    business_id = engine.create_business("Security Test Business")
    product_id = engine.create_product(
        business_id,
        "Vetkoek",
        selling_price_cents=1500
    )

    batch_id = engine.create_stock_batch(
        business_id,
        product_id,
        "SEC-001",
        5,
        3000
    )

    customer_id = engine.create_customer(
        business_id,
        "Test Customer"
    )

    # 1. Valid sale
    engine.sell(
        business_id,
        product_id,
        2,
        1500,
        "CASH",
        stock_batch_id=batch_id
    )
    print("[OK] Valid sale accepted")

    # 2. Prevent overselling selected batch
    try:
        engine.sell(
            business_id,
            product_id,
            4,
            1500,
            "CASH",
            stock_batch_id=batch_id
        )
        raise AssertionError("Overselling was allowed")
    except ValueError:
        print("[OK] Overselling rejected")

    # 3. Credit sale requires customer
    try:
        engine.sell(
            business_id,
            product_id,
            1,
            1500,
            "CREDIT",
            stock_batch_id=batch_id
        )
        raise AssertionError("Credit sale without customer was allowed")
    except ValueError:
        print("[OK] Credit sale without customer rejected")

    # 4. Valid credit sale
    sale_id = engine.sell(
        business_id,
        product_id,
        1,
        1500,
        "CREDIT",
        customer_id=customer_id,
        stock_batch_id=batch_id
    )
    print("[OK] Valid credit sale accepted")

    # 5. Payment cannot exceed debt
    credit_id = None
    with engine.connect() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM credit_accounts
            WHERE sale_id = ?
            """,
            (sale_id,)
        ).fetchone()
        credit_id = row["id"]

    try:
        engine.record_payment(
            business_id,
            customer_id,
            credit_id,
            2000
        )
        raise AssertionError("Overpayment was allowed")
    except ValueError:
        print("[OK] Overpayment rejected")

    # 6. Invalid expense rejected
    try:
        engine.record_expense(
            business_id,
            "Ingredients",
            -100
        )
        raise AssertionError("Negative expense was allowed")
    except ValueError:
        print("[OK] Negative expense rejected")

    # 7. Audit events exist
    with engine.connect() as conn:
        audit_count = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM audit_events
            WHERE business_id = ?
            """,
            (business_id,)
        ).fetchone()["count"]

    if audit_count < 6:
        raise AssertionError(
            f"Expected audit events, found only {audit_count}"
        )

    print("[OK] Audit events recorded")

print()
print("=== SECURITY + AUDIT TEST PASSED ===")
