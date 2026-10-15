import re
import tempfile
import unittest
from pathlib import Path

from werkzeug.security import generate_password_hash
import app as app_module
from app import app, get_db


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        app_module._LOGIN_FAILURES.clear()
        self.temp = tempfile.TemporaryDirectory()
        app.config.update(
            TESTING=True,
            SECRET_KEY="auth-test-only-secret",
            DATABASE=str(Path(self.temp.name) / "auth-test.db"),
            AUTH_USERNAME="Boitsholo-test",
            AUTH_PASSWORD_HASH=generate_password_hash("test-password"),
        )
        self.client = app.test_client()
        with app.app_context():
            get_db()

    def tearDown(self):
        self.temp.cleanup()

    def login_token(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        match = re.search(rb'name="csrf" value="([^"]+)"', response.data)
        self.assertIsNotNone(match, "Login form must contain a CSRF token.")
        return match.group(1).decode()

    def test_protected_page_redirects_without_login(self):
        response = self.client.get("/new")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_wrong_password_is_rejected(self):
        response = self.client.post("/login", data={
            "csrf": self.login_token(),
            "username": "Boitsholo-test",
            "password": "wrong-password",
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])
        page = self.client.get("/new")
        self.assertEqual(page.status_code, 302)

    def test_correct_login_allows_protected_page(self):
        response = self.client.post("/login", data={
            "csrf": self.login_token(),
            "username": "Boitsholo-test",
            "password": "test-password",
        })
        self.assertEqual(response.status_code, 302)
        page = self.client.get("/new")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Sign out", page.data)

    def test_logout_removes_access(self):
        self.client.post("/login", data={
            "csrf": self.login_token(),
            "username": "Boitsholo-test",
            "password": "test-password",
        })
        page = self.client.get("/new")
        match = re.search(rb'name="csrf" value="([^"]+)"', page.data)
        self.assertIsNotNone(match)
        response = self.client.post("/logout", data={
            "csrf": match.group(1).decode(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])
        self.assertEqual(self.client.get("/new").status_code, 302)

    def test_repeated_failed_logins_are_limited(self):
        for _ in range(app_module.LOGIN_MAX_FAILURES):
            response = self.client.post("/login", data={
                "csrf": self.login_token(),
                "username": "Boitsholo-test",
                "password": "wrong-password",
            })
            self.assertEqual(response.status_code, 302)

        response = self.client.post("/login", data={
            "csrf": self.login_token(),
            "username": "Boitsholo-test",
            "password": "test-password",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get("/new").status_code, 302)

    def test_login_rejects_invalid_csrf(self):
        response = self.client.post("/login", data={
            "csrf": "invalid",
            "username": "Boitsholo-test",
            "password": "test-password",
        })
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
