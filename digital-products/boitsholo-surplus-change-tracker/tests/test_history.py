import re
import tempfile
import unittest
from pathlib import Path

from app import app, get_db
from werkzeug.security import generate_password_hash


class HistoryClearTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        app.config.update(
            TESTING=True,
            SECRET_KEY="test-only-secret",
            DATABASE=str(Path(self.temp.name) / "test.db"),
            AUTH_USERNAME="Boitsholo-test",
            AUTH_PASSWORD_HASH=generate_password_hash("test-password"),
        )
        self.client = app.test_client()
        self.sign_in()
        with app.app_context():
            db = get_db()
            cur = db.execute(
                """INSERT INTO transactions
                (customer, location, served_by, approver, amount_paid, total,
                 change_owed, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("Example", "Test", "Tester", "", 1500, 1000, 500,
                 "PENDING", "2026-01-01T10:00:00+02:00"),
            )
            db.execute(
                """INSERT INTO items
                (transaction_id, item_name, quantity, unit_price, line_total)
                VALUES (?, ?, ?, ?, ?)""",
                (cur.lastrowid, "Example item", 1, 1000, 1000),
            )
            db.commit()

    def sign_in(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        match = re.search(rb'name="csrf" value="([^"]+)"', response.data)
        self.assertIsNotNone(match, "Login page must contain a CSRF token.")
        response = self.client.post("/login", data={
            "csrf": match.group(1).decode(),
            "username": "Boitsholo-test",
            "password": "test-password",
        })
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        self.temp.cleanup()

    def csrf_from_history(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        match = re.search(rb'name="csrf" value="([^"]+)"', response.data)
        self.assertIsNotNone(match, "History page must contain a CSRF token.")
        return match.group(1).decode()

    def counts(self):
        with app.app_context():
            db = get_db()
            return (
                db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0],
                db.execute("SELECT COUNT(*) FROM items").fetchone()[0],
            )

    def test_invalid_csrf_does_not_clear_history(self):
        response = self.client.post("/history/clear", data={"csrf": "invalid"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.counts(), (1, 1))

    def test_valid_csrf_clears_transactions_and_items(self):
        token = self.csrf_from_history()
        response = self.client.post(
            "/history/clear", data={"csrf": token}, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.counts(), (0, 0))
        self.assertIn(b"No transactions recorded yet.", response.data)


if __name__ == "__main__":
    unittest.main()
