import re
import tempfile
import unittest
from pathlib import Path

from werkzeug.security import generate_password_hash
from app import app, get_db


class MoneyOwedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        app.config.update(
            TESTING=True,
            SECRET_KEY="money-owed-test-secret",
            DATABASE=str(Path(self.temp.name) / "money-owed-test.db"),
            AUTH_USERNAME="Boitsholo-test",
            AUTH_PASSWORD_HASH=generate_password_hash("test-password"),
        )
        self.client = app.test_client()
        response = self.client.get("/login")
        token = re.search(rb'name="csrf" value="([^"]+)"', response.data).group(1).decode()
        self.client.post("/login", data={
            "csrf": token,
            "username": "Boitsholo-test",
            "password": "test-password",
        })
        with app.app_context():
            get_db()

    def tearDown(self):
        self.temp.cleanup()

    def page_token(self):
        response = self.client.get("/money-owed")
        self.assertEqual(response.status_code, 200)
        match = re.search(rb'name="csrf" value="([^"]+)"', response.data)
        self.assertIsNotNone(match)
        return match.group(1).decode()

    def add_record(self, direction, person, amount="125.50"):
        return self.client.post("/money-owed/new", data={
            "csrf": self.page_token(),
            "direction": direction,
            "person": person,
            "reason": "Test balance",
            "amount": amount,
        })

    def test_both_directions_are_saved_in_cents(self):
        self.add_record("BUSINESS_OWES", "Supplier")
        self.add_record("OWES_BUSINESS", "Customer")
        with app.app_context():
            rows = get_db().execute(
                "SELECT direction, amount, status FROM money_owed ORDER BY id"
            ).fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["direction"], "BUSINESS_OWES")
        self.assertEqual(rows[1]["direction"], "OWES_BUSINESS")
        self.assertEqual(rows[0]["amount"], 12550)
        self.assertEqual(rows[0]["status"], "OPEN")

    def test_invalid_csrf_cannot_add_record(self):
        response = self.client.post("/money-owed/new", data={
            "csrf": "invalid",
            "direction": "OWES_BUSINESS",
            "person": "Customer",
            "reason": "Test",
            "amount": "10.00",
        })
        self.assertEqual(response.status_code, 400)
        with app.app_context():
            count = get_db().execute(
                "SELECT COUNT(*) FROM money_owed"
            ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_open_record_can_be_settled(self):
        self.add_record("OWES_BUSINESS", "Customer")
        token = self.page_token()
        with app.app_context():
            debt_id = get_db().execute(
                "SELECT id FROM money_owed"
            ).fetchone()["id"]
        response = self.client.post(
            f"/money-owed/{debt_id}/settle", data={"csrf": token}
        )
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            row = get_db().execute(
                "SELECT status, settled_by FROM money_owed WHERE id=?",
                (debt_id,)
            ).fetchone()
        self.assertEqual(row["status"], "SETTLED")
        self.assertEqual(row["settled_by"], "Boitsholo-test")

    def test_invalid_amount_is_not_saved(self):
        self.add_record("OWES_BUSINESS", "Customer", amount="0")
        with app.app_context():
            count = get_db().execute(
                "SELECT COUNT(*) FROM money_owed"
            ).fetchone()[0]
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
