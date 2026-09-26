import sqlite3
from pathlib import Path
from datetime import datetime


ENGINE_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ENGINE_ROOT / "database" / "mmk_small_business_engine.db"
SCHEMA_PATH = ENGINE_ROOT / "database" / "schema.sql"


class SmallBusinessEngine:
    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize_database(self):
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Database schema not found: {SCHEMA_PATH}")

        schema = SCHEMA_PATH.read_text(encoding="utf-8")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executescript(schema)

    def _audit(self, conn, business_id, action, entity_type, entity_id=None, details=None):
        import json

        conn.execute(
            """
            INSERT INTO audit_events
                (business_id, action, entity_type, entity_id, details_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                business_id,
                action,
                entity_type,
                entity_id,
                json.dumps(details or {}, sort_keys=True),
            ),
        )

    def create_business(self, name, currency="ZAR"):
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO businesses (name, currency)
                VALUES (?, ?)
                """,
                (name, currency),
            )
            business_id = cur.lastrowid
            self._audit(
                conn, business_id, "CREATE", "BUSINESS", business_id,
                {"name": name, "currency": currency},
            )
            return business_id

    def create_product(self, business_id, name, unit="unit",
                       selling_price_cents=0):
        with self.connect() as conn:
            if selling_price_cents < 0:
                raise ValueError("Selling price cannot be negative.")

            cur = conn.execute(
                """
                INSERT INTO products
                    (business_id, name, unit, selling_price_cents)
                VALUES (?, ?, ?, ?)
                """,
                (business_id, name, unit, selling_price_cents),
            )
            product_id = cur.lastrowid
            self._audit(
                conn, business_id, "CREATE", "PRODUCT", product_id,
                {"name": name, "unit": unit},
            )
            return product_id

    def create_stock_batch(
        self,
        business_id,
        product_id,
        batch_reference,
        quantity_produced,
        production_cost_cents,
        production_date=None,
    ):
        if quantity_produced <= 0:
            raise ValueError("Stock quantity must be greater than zero.")

        if production_cost_cents < 0:
            raise ValueError("Production cost cannot be negative.")

        production_date = production_date or datetime.now().date().isoformat()

        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO stock_batches
                    (
                        business_id,
                        product_id,
                        batch_reference,
                        quantity_produced,
                        production_cost_cents,
                        production_date
                    )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    business_id,
                    product_id,
                    batch_reference,
                    quantity_produced,
                    production_cost_cents,
                    production_date,
                ),
            )

            batch_id = cur.lastrowid

            conn.execute(
                """
                INSERT INTO stock_movements
                    (
                        business_id,
                        product_id,
                        stock_batch_id,
                        movement_type,
                        quantity_delta,
                        reference_type,
                        reference_id,
                        reason
                    )
                VALUES (?, ?, ?, 'PRODUCTION', ?, 'STOCK_BATCH', ?, ?)
                """,
                (
                    business_id,
                    product_id,
                    batch_id,
                    quantity_produced,
                    batch_id,
                    "Initial production batch",
                ),
            )

            self._audit(
                conn, business_id, "CREATE", "STOCK_BATCH", batch_id,
                {
                    "product_id": product_id,
                    "batch_reference": batch_reference,
                    "quantity_produced": quantity_produced,
                    "production_cost_cents": production_cost_cents,
                },
            )

            return batch_id

    def get_stock(self, business_id, product_id):
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(quantity_delta), 0) AS quantity_on_hand
                FROM stock_movements
                WHERE business_id = ?
                  AND product_id = ?
                """,
                (business_id, product_id),
            ).fetchone()

            return row["quantity_on_hand"]

    def create_customer(self, business_id, name, phone=None, notes=None):
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO customers
                    (business_id, name, phone, notes)
                VALUES (?, ?, ?, ?)
                """,
                (business_id, name, phone, notes),
            )
            customer_id = cur.lastrowid
            self._audit(
                conn, business_id, "CREATE", "CUSTOMER", customer_id,
                {"name": name},
            )
            return customer_id

    def sell(
        self,
        business_id,
        product_id,
        quantity,
        unit_price_cents,
        sale_type="CASH",
        customer_id=None,
        stock_batch_id=None,
        due_date=None,
    ):
        if quantity <= 0:
            raise ValueError("Sale quantity must be greater than zero.")

        if unit_price_cents < 0:
            raise ValueError("Selling price cannot be negative.")

        sale_type = sale_type.upper()

        if sale_type not in ("CASH", "CREDIT"):
            raise ValueError("Sale type must be CASH or CREDIT.")

        if sale_type == "CREDIT" and customer_id is None:
            raise ValueError("Credit sales require a customer.")

        available = self.get_stock(business_id, product_id)

        if quantity > available:
            raise ValueError(
                f"Insufficient stock. Available: {available}, requested: {quantity}."
            )

        with self.connect() as conn:
            if stock_batch_id is None:
                batch = conn.execute(
                    """
                    SELECT id
                    FROM stock_batches
                    WHERE business_id = ?
                      AND product_id = ?
                    ORDER BY production_date ASC, id ASC
                    LIMIT 1
                    """,
                    (business_id, product_id),
                ).fetchone()

                if batch is None:
                    raise ValueError("No stock batch exists for this product.")

                stock_batch_id = batch["id"]

            batch = conn.execute(
                """
                SELECT
                    sb.id,
                    sb.product_id,
                    sb.quantity_produced,
                    COALESCE(SUM(sm.quantity_delta), 0) AS batch_stock
                FROM stock_batches sb
                LEFT JOIN stock_movements sm
                    ON sm.stock_batch_id = sb.id
                WHERE sb.id = ?
                  AND sb.business_id = ?
                  AND sb.product_id = ?
                GROUP BY sb.id
                """,
                (stock_batch_id, business_id, product_id),
            ).fetchone()

            if batch is None:
                raise ValueError("Stock batch not found for this business/product.")

            if quantity > batch["batch_stock"]:
                raise ValueError(
                    f"Insufficient batch stock. Available: {batch['batch_stock']}, "
                    f"requested: {quantity}."
                )

        total_cents = quantity * unit_price_cents
        sale_date = datetime.now().date().isoformat()

        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO sales
                    (
                        business_id,
                        customer_id,
                        sale_type,
                        total_amount_cents,
                        sale_date
                    )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    business_id,
                    customer_id,
                    sale_type,
                    total_cents,
                    sale_date,
                ),
            )

            sale_id = cur.lastrowid

            conn.execute(
                """
                INSERT INTO sale_items
                    (
                        sale_id,
                        product_id,
                        stock_batch_id,
                        quantity,
                        unit_price_cents,
                        line_total_cents
                    )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    sale_id,
                    product_id,
                    stock_batch_id,
                    quantity,
                    unit_price_cents,
                    total_cents,
                ),
            )

            conn.execute(
                """
                INSERT INTO stock_movements
                    (
                        business_id,
                        product_id,
                        stock_batch_id,
                        movement_type,
                        quantity_delta,
                        reference_type,
                        reference_id,
                        reason
                    )
                VALUES (?, ?, ?, 'SALE', ?, 'SALE', ?, ?)
                """,
                (
                    business_id,
                    product_id,
                    stock_batch_id,
                    -quantity,
                    sale_id,
                    f"{sale_type} sale",
                ),
            )

            if sale_type == "CREDIT":
                conn.execute(
                    """
                    INSERT INTO credit_accounts
                        (
                            business_id,
                            customer_id,
                            sale_id,
                            amount_owed_cents,
                            amount_paid_cents,
                            due_date
                        )
                    VALUES (?, ?, ?, ?, 0, ?)
                    """,
                    (
                        business_id,
                        customer_id,
                        sale_id,
                        total_cents,
                        due_date,
                    ),
                )

            self._audit(
                conn, business_id, "CREATE", "SALE", sale_id,
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "sale_type": sale_type,
                    "total_amount_cents": total_cents,
                    "stock_batch_id": stock_batch_id,
                    "customer_id": customer_id,
                },
            )

            return sale_id

    def record_payment(
        self,
        business_id,
        customer_id,
        credit_account_id,
        amount_cents,
        payment_method="CASH",
        notes=None,
    ):
        if amount_cents <= 0:
            raise ValueError("Payment must be greater than zero.")

        with self.connect() as conn:
            account = conn.execute(
                """
                SELECT
                    amount_owed_cents,
                    amount_paid_cents
                FROM credit_accounts
                WHERE id = ?
                  AND business_id = ?
                  AND customer_id = ?
                """,
                (
                    credit_account_id,
                    business_id,
                    customer_id,
                ),
            ).fetchone()

            if account is None:
                raise ValueError("Credit account not found.")

            balance = (
                account["amount_owed_cents"]
                - account["amount_paid_cents"]
            )

            if amount_cents > balance:
                raise ValueError(
                    f"Payment exceeds outstanding balance of {balance} cents."
                )

            conn.execute(
                """
                INSERT INTO payments
                    (
                        business_id,
                        customer_id,
                        credit_account_id,
                        amount_cents,
                        payment_method,
                        payment_date,
                        notes
                    )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    business_id,
                    customer_id,
                    credit_account_id,
                    amount_cents,
                    payment_method,
                    datetime.now().date().isoformat(),
                    notes,
                ),
            )

            conn.execute(
                """
                UPDATE credit_accounts
                SET amount_paid_cents = amount_paid_cents + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (amount_cents, credit_account_id),
            )

            self._audit(
                conn, business_id, "CREATE", "PAYMENT", credit_account_id,
                {
                    "customer_id": customer_id,
                    "amount_cents": amount_cents,
                    "payment_method": payment_method,
                },
            )

    def record_expense(
        self,
        business_id,
        category,
        amount_cents,
        description=None,
        expense_date=None,
    ):
        if not category or not str(category).strip():
            raise ValueError("Expense category is required.")

        if amount_cents < 0:
            raise ValueError("Expense amount cannot be negative.")

        expense_date = expense_date or datetime.now().date().isoformat()

        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO expenses
                    (business_id, category, description, amount_cents, expense_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    business_id,
                    category.strip(),
                    description,
                    amount_cents,
                    expense_date,
                ),
            )

            expense_id = cur.lastrowid

            self._audit(
                conn, business_id, "CREATE", "EXPENSE", expense_id,
                {
                    "category": category.strip(),
                    "amount_cents": amount_cents,
                },
            )

            return expense_id

    def get_customer_balance(self, business_id, customer_id):
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(
                    SUM(amount_owed_cents - amount_paid_cents),
                    0
                ) AS balance
                FROM credit_accounts
                WHERE business_id = ?
                  AND customer_id = ?
                """,
                (business_id, customer_id),
            ).fetchone()

            return row["balance"]

    def get_sales_total(self, business_id):
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(total_amount_cents), 0) AS total
                FROM sales
                WHERE business_id = ?
                """,
                (business_id,),
            ).fetchone()

            return row["total"]

    def get_cash_sales_total(self, business_id):
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(total_amount_cents), 0) AS total
                FROM sales
                WHERE business_id = ?
                  AND sale_type = 'CASH'
                """,
                (business_id,),
            ).fetchone()

            return row["total"]

    def get_credit_sales_total(self, business_id):
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(total_amount_cents), 0) AS total
                FROM sales
                WHERE business_id = ?
                  AND sale_type = 'CREDIT'
                """,
                (business_id,),
            ).fetchone()

            return row["total"]

    def get_expenses_total(self, business_id):
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(amount_cents), 0) AS total
                FROM expenses
                WHERE business_id = ?
                """,
                (business_id,),
            ).fetchone()

            return row["total"]

    @staticmethod
    def money(cents):
        return f"R{cents / 100:.2f}"
