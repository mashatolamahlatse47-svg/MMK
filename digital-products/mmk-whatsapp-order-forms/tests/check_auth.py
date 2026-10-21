import os
import tempfile
import unittest
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server.auth_app as auth


def test_dbopen():
    """Use the app's managed database context."""
    return auth.dbopen()


class AuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.original_db = auth.DB
        auth.DB = Path(cls.temp.name) / "test.db"
        with test_dbopen() as d:
            d.executescript("""
            CREATE TABLE shops(
                id INTEGER PRIMARY KEY, name TEXT NOT NULL,
                whatsapp TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE users(
                id INTEGER PRIMARY KEY,
                shop_id INTEGER NOT NULL REFERENCES shops(id),
                email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE products(
                id INTEGER PRIMARY KEY,
                shop_id INTEGER NOT NULL REFERENCES shops(id),
                name TEXT NOT NULL, price_cents INTEGER NOT NULL CHECK(price_cents>=0),
                active INTEGER NOT NULL DEFAULT 1);
            CREATE TABLE orders(
                id INTEGER PRIMARY KEY,
                shop_id INTEGER NOT NULL REFERENCES shops(id),
                customer_name TEXT NOT NULL, items_json TEXT NOT NULL,
                total_cents INTEGER NOT NULL CHECK(total_cents>=0),
                status TEXT NOT NULL DEFAULT 'NEW',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            """)

    @classmethod
    def tearDownClass(cls):
        auth.DB = cls.original_db
        cls.temp.cleanup()

    def setUp(self):
        with test_dbopen() as d:
            d.execute("DELETE FROM orders")
            d.execute("DELETE FROM products")
            d.execute("DELETE FROM users")
            d.execute("DELETE FROM shops")
        self.client = auth.app.test_client()

    def csrf(self):
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as s:
            return s["csrf"]

    def register(self, shop, email):
        token = self.csrf()
        return self.client.post("/register", data={
            "csrf": token, "shop": shop, "email": email,
            "password": "MMK-Test-Password-123!"
        })

    def test_registration_and_dashboard(self):
        response = self.register("Test Shop A", "a@example.com")
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Shop A", response.data)

    def test_duplicate_email_does_not_leave_shop(self):
        self.register("Test Shop A", "a@example.com")
        with test_dbopen() as before:
            shops_before = before.execute("SELECT COUNT(*) FROM shops").fetchone()[0]
        response = self.register("Should Roll Back", "a@example.com")
        self.assertEqual(response.status_code, 409)
        with test_dbopen() as d:
            shops_after = d.execute("SELECT COUNT(*) FROM shops").fetchone()[0]
        self.assertEqual(shops_after, shops_before)

    def test_post_without_csrf_rejected(self):
        response = self.client.post("/logout")
        self.assertEqual(response.status_code, 400)

    def test_dashboard_requires_login(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_logout_blocks_dashboard(self):
        response = self.register("Logout Test Shop", "logout@example.com")
        self.assertEqual(response.status_code, 302)

        token = self.csrf()
        response = self.client.post("/logout", data={"csrf": token})
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")



    def test_products_requires_login(self):
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_add_product_and_reject_invalid_price(self):
        self.register("Product Shop", "products@example.com")
        token = self.csrf()
        response = self.client.post("/products", data={
            "csrf": token, "name": "Test Coffee", "price": "12.50"
        })
        self.assertEqual(response.status_code, 302)
        with test_dbopen() as d:
            row = d.execute("SELECT name, price_cents FROM products").fetchone()
        self.assertEqual(row["name"], "Test Coffee")
        self.assertEqual(row["price_cents"], 1250)
        response = self.client.get("/products")
        self.assertIn(b"Test Coffee", response.data)
        self.assertIn(b"R12.50", response.data)

        token = self.csrf()
        response = self.client.post("/products", data={
            "csrf": token, "name": "Bad Price", "price": "-1"
        })
        self.assertEqual(response.status_code, 400)
        with test_dbopen() as d:
            count = d.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        self.assertEqual(count, 1)

    def test_toggle_product_active_state(self):
        self.register("Toggle Shop", "toggle@example.com")
        token = self.csrf()
        self.client.post("/products", data={
            "csrf": token, "name": "Toggle Coffee", "price": "5.00"
        })
        with test_dbopen() as d:
            pid = d.execute("SELECT id FROM products").fetchone()["id"]

        for expected in (0, 1):
            token = self.csrf()
            response = self.client.post(
                f"/products/{pid}/toggle", data={"csrf": token}
            )
            self.assertEqual(response.status_code, 302)
            with test_dbopen() as d:
                active = d.execute(
                    "SELECT active FROM products WHERE id=?", (pid,)
                ).fetchone()["active"]
            self.assertEqual(active, expected)

    def test_shop_isolation(self):
        self.register("Shop One", "one@example.com")
        token = self.csrf()
        self.client.post("/products", data={
            "csrf": token, "name": "Private Product One", "price": "9.00"
        })
        with test_dbopen() as d:
            pid = d.execute("SELECT id FROM products").fetchone()["id"]

        other = auth.app.test_client()
        other.get("/register")
        with other.session_transaction() as s:
            token = s["csrf"]
        response = other.post("/register", data={
            "csrf": token, "shop": "Shop Two", "email": "two@example.com",
            "password": "MMK-Test-Password-456!"
        })
        self.assertEqual(response.status_code, 302)
        response = other.get("/products")
        self.assertNotIn(b"Private Product One", response.data)
        with other.session_transaction() as s:
            token = s["csrf"]
        response = other.post(
            f"/products/{pid}/toggle", data={"csrf": token}
        )
        self.assertEqual(response.status_code, 404)
        with test_dbopen() as d:
            active = d.execute(
                "SELECT active FROM products WHERE id=?", (pid,)
            ).fetchone()["active"]
        self.assertEqual(active, 1)


    def test_settings_requires_login(self):
        response = self.client.get("/settings")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_settings_saves_whatsapp(self):
        self.register("MMK Settings Test", "settings@example.test")
        token = self.csrf()
        response = self.client.post("/settings", data={
            "csrf": token, "whatsapp": "0821234567"
        })
        self.assertEqual(response.status_code, 302)
        with test_dbopen() as d:
            row = d.execute(
                "SELECT whatsapp FROM shops WHERE name=?",
                ("MMK Settings Test",)
            ).fetchone()
        self.assertEqual(row["whatsapp"], "0821234567")

    def test_customer_checkout_saves_order_and_whatsapp_link(self):
        self.register("MMK Checkout Test", "checkout@example.test")
        with test_dbopen() as d:
            shop = d.execute(
                "SELECT id FROM shops WHERE name=?", ("MMK Checkout Test",)
            ).fetchone()
            shop_id = shop["id"]
            d.execute("UPDATE shops SET whatsapp=? WHERE id=?",
                      ("0821234567", shop_id))
            cur = d.execute(
                "INSERT INTO products(shop_id,name,price_cents,active) "
                "VALUES(?,?,?,1)", (shop_id, "Test Coffee", 1250)
            )
            product_id = cur.lastrowid

        response = self.client.get(f"/shop/{shop_id}")
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as session:
            token = session["csrf"]

        response = self.client.post(f"/shop/{shop_id}", data={
            "csrf": token, "customer_name": "Test Customer",
            f"qty_{product_id}": "2"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Continue to WhatsApp", response.data)
        self.assertIn(b"wa.me/27821234567?text=", response.data)
        self.assertIn(b"Total: R25.00", response.data)

        with test_dbopen() as d:
            order = d.execute(
                "SELECT * FROM orders WHERE shop_id=?", (shop_id,)
            ).fetchone()
        self.assertIsNotNone(order)
        self.assertEqual(order["customer_name"], "Test Customer")
        self.assertEqual(order["total_cents"], 2500)
        self.assertEqual(order["status"], "NEW")

    def test_customer_checkout_rejects_empty_order(self):
        self.register("MMK Empty Test", "empty@example.test")
        with test_dbopen() as d:
            shop = d.execute(
                "SELECT id FROM shops WHERE name=?", ("MMK Empty Test",)
            ).fetchone()
            shop_id = shop["id"]
            cur = d.execute(
                "INSERT INTO products(shop_id,name,price_cents,active) "
                "VALUES(?,?,?,1)", (shop_id, "Test Item", 500)
            )
            product_id = cur.lastrowid

        self.client.get(f"/shop/{shop_id}")
        with self.client.session_transaction() as session:
            token = session["csrf"]
        response = self.client.post(f"/shop/{shop_id}", data={
            "csrf": token, "customer_name": "Test Customer",
            f"qty_{product_id}": "0"
        })
        self.assertEqual(response.status_code, 400)
        with test_dbopen() as d:
            count = d.execute(
                "SELECT COUNT(*) FROM orders WHERE shop_id=?", (shop_id,)
            ).fetchone()[0]
        self.assertEqual(count, 0)


    def test_owner_can_update_own_order_status(self):
        self.register("MMK Status Test", "status@example.test")
        with test_dbopen() as d:
            shop = d.execute(
                "SELECT id FROM shops WHERE name=?", ("MMK Status Test",)
            ).fetchone()
            cur = d.execute(
                "INSERT INTO orders(shop_id,customer_name,items_json,total_cents) "
                "VALUES(?,?,?,?)", (shop["id"], "Fake Customer", "[]", 500)
            )
            order_id = cur.lastrowid
        token = self.csrf()
        response = self.client.post(f"/orders/{order_id}/status", data={
            "csrf": token, "status": "CONFIRMED"
        })
        self.assertEqual(response.status_code, 302)
        with test_dbopen() as d:
            row = d.execute(
                "SELECT status FROM orders WHERE id=?", (order_id,)
            ).fetchone()
        self.assertEqual(row["status"], "CONFIRMED")

    def test_owner_cannot_update_another_shops_order(self):
        self.register("MMK Owner One", "ownerone@example.test")
        with test_dbopen() as d:
            cur = d.execute("INSERT INTO shops(name) VALUES(?)", ("MMK Owner Two",))
            other_shop_id = cur.lastrowid
            cur = d.execute(
                "INSERT INTO orders(shop_id,customer_name,items_json,total_cents) "
                "VALUES(?,?,?,?)", (other_shop_id, "Fake Customer", "[]", 500)
            )
            order_id = cur.lastrowid
        response = self.client.post(f"/orders/{order_id}/status", data={
            "csrf": self.csrf(), "status": "COMPLETED"
        })
        self.assertEqual(response.status_code, 404)
        with test_dbopen() as d:
            row = d.execute(
                "SELECT status FROM orders WHERE id=?", (order_id,)
            ).fetchone()
        self.assertEqual(row["status"], "NEW")

    def test_order_status_rejects_invalid_value(self):
        self.register("MMK Invalid Status", "invalidstatus@example.test")
        with test_dbopen() as d:
            shop = d.execute(
                "SELECT id FROM shops WHERE name=?", ("MMK Invalid Status",)
            ).fetchone()
            cur = d.execute(
                "INSERT INTO orders(shop_id,customer_name,items_json,total_cents) "
                "VALUES(?,?,?,?)", (shop["id"], "Fake Customer", "[]", 500)
            )
            order_id = cur.lastrowid
        response = self.client.post(f"/orders/{order_id}/status", data={
            "csrf": self.csrf(), "status": "PAID"
        })
        self.assertEqual(response.status_code, 400)


    def test_owner_receipt_shows_order_details(self):
        self.register("MMK Receipt Shop", "receipt@example.test")
        with test_dbopen() as d:
            shop = d.execute(
                "SELECT id FROM shops WHERE name=?", ("MMK Receipt Shop",)
            ).fetchone()
            cur = d.execute(
                "INSERT INTO orders(shop_id,customer_name,items_json,total_cents) "
                "VALUES(?,?,?,?)",
                (shop["id"], "Test Customer",
                 '[{"name":"Coffee","quantity":2,"unit_price_cents":1250,'
                 '"line_total_cents":2500}]', 2500)
            )
            order_id = cur.lastrowid
        response = self.client.get(f"/orders/{order_id}/receipt")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ORDER RECEIPT", response.data)
        self.assertIn(b"Test Customer", response.data)
        self.assertIn(b"Coffee", response.data)
        self.assertIn(b"R25.00", response.data)
        self.assertIn(b"window.print()", response.data)

    def test_owner_cannot_view_another_shops_receipt(self):
        self.register("MMK Receipt Owner", "receiptowner@example.test")
        with test_dbopen() as d:
            cur = d.execute("INSERT INTO shops(name) VALUES(?)",
                            ("Other Receipt Shop",))
            other_shop = cur.lastrowid
            cur = d.execute(
                "INSERT INTO orders(shop_id,customer_name,items_json,total_cents) "
                "VALUES(?,?,?,?)",
                (other_shop, "Private Customer", "[]", 0)
            )
            order_id = cur.lastrowid
        response = self.client.get(f"/orders/{order_id}/receipt")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)
