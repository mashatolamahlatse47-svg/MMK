PRAGMA foreign_keys = ON;

BEGIN;

CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'ZAR',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'unit',
    selling_price_cents INTEGER NOT NULL DEFAULT 0
        CHECK (selling_price_cents >= 0),
    active INTEGER NOT NULL DEFAULT 1
        CHECK (active IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    UNIQUE (business_id, name)
);

CREATE TABLE IF NOT EXISTS stock_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    batch_reference TEXT NOT NULL,
    quantity_produced INTEGER NOT NULL
        CHECK (quantity_produced > 0),
    production_cost_cents INTEGER NOT NULL DEFAULT 0
        CHECK (production_cost_cents >= 0),
    production_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    UNIQUE (business_id, batch_reference)
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    stock_batch_id INTEGER,
    movement_type TEXT NOT NULL
        CHECK (movement_type IN (
            'PRODUCTION',
            'SALE',
            'ADJUSTMENT',
            'WASTAGE',
            'DAMAGE',
            'RETURN'
        )),
    quantity_delta INTEGER NOT NULL
        CHECK (quantity_delta <> 0),
    reference_type TEXT,
    reference_id INTEGER,
    reason TEXT,
    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    FOREIGN KEY (stock_batch_id) REFERENCES stock_batches(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    notes TEXT,
    active INTEGER NOT NULL DEFAULT 1
        CHECK (active IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    customer_id INTEGER,
    sale_type TEXT NOT NULL
        CHECK (sale_type IN ('CASH','CREDIT')),
    total_amount_cents INTEGER NOT NULL DEFAULT 0
        CHECK (total_amount_cents >= 0),
    sale_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    stock_batch_id INTEGER,
    quantity INTEGER NOT NULL
        CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL
        CHECK (unit_price_cents >= 0),
    line_total_cents INTEGER NOT NULL
        CHECK (line_total_cents >= 0),
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    FOREIGN KEY (stock_batch_id) REFERENCES stock_batches(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS credit_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    sale_id INTEGER NOT NULL UNIQUE,
    amount_owed_cents INTEGER NOT NULL
        CHECK (amount_owed_cents >= 0),
    amount_paid_cents INTEGER NOT NULL DEFAULT 0
        CHECK (amount_paid_cents >= 0),
    due_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    CHECK (amount_paid_cents <= amount_owed_cents)
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    credit_account_id INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL
        CHECK (amount_cents > 0),
    payment_method TEXT NOT NULL DEFAULT 'CASH',
    payment_date TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT,
    FOREIGN KEY (credit_account_id) REFERENCES credit_accounts(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    amount_cents INTEGER NOT NULL
        CHECK (amount_cents >= 0),
    expense_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    details_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_products_business
    ON products(business_id);

CREATE INDEX IF NOT EXISTS idx_stock_movements_product
    ON stock_movements(business_id, product_id);

CREATE INDEX IF NOT EXISTS idx_stock_movements_batch
    ON stock_movements(stock_batch_id);

CREATE INDEX IF NOT EXISTS idx_sales_business_date
    ON sales(business_id, sale_date);

CREATE INDEX IF NOT EXISTS idx_sale_items_sale
    ON sale_items(sale_id);

CREATE INDEX IF NOT EXISTS idx_customers_business
    ON customers(business_id);

CREATE INDEX IF NOT EXISTS idx_credit_customer
    ON credit_accounts(customer_id);

CREATE INDEX IF NOT EXISTS idx_payments_credit
    ON payments(credit_account_id);

CREATE INDEX IF NOT EXISTS idx_expenses_business_date
    ON expenses(business_id, expense_date);

CREATE INDEX IF NOT EXISTS idx_audit_business
    ON audit_events(business_id, created_at);

CREATE VIEW IF NOT EXISTS current_stock AS
SELECT
    business_id,
    product_id,
    COALESCE(SUM(quantity_delta), 0) AS quantity_on_hand
FROM stock_movements
GROUP BY business_id, product_id;

CREATE VIEW IF NOT EXISTS credit_balances AS
SELECT
    ca.id AS credit_account_id,
    ca.business_id,
    ca.customer_id,
    ca.sale_id,
    ca.amount_owed_cents,
    ca.amount_paid_cents,
    (ca.amount_owed_cents - ca.amount_paid_cents) AS balance_cents,
    CASE
        WHEN ca.amount_owed_cents - ca.amount_paid_cents <= 0 THEN 'PAID'
        WHEN ca.amount_paid_cents > 0 THEN 'PARTIALLY_PAID'
        WHEN ca.due_date IS NOT NULL
             AND date(ca.due_date) < date('now') THEN 'OVERDUE'
        ELSE 'OPEN'
    END AS status
FROM credit_accounts ca;

COMMIT;
