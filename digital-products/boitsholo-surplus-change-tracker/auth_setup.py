from getpass import getpass
import os
import secrets
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE = Path(__file__).resolve().parent
env_file = BASE / ".env"

if env_file.exists():
    raise SystemExit("STOP: .env already exists. Protect it; do not overwrite it.")

username = "Boitsholo"
password = getpass("Create a private password (minimum 12 characters): ")
if len(password) < 12:
    raise SystemExit("STOP: password must be at least 12 characters.")

confirm = getpass("Enter the password again: ")
if password != confirm:
    raise SystemExit("STOP: passwords did not match. Run setup again.")

content = (
    f"BOITSHOLO_USERNAME={username}\n"
    f"BOITSHOLO_PASSWORD_HASH={generate_password_hash(password)}\n"
    f"BOITSHOLO_SECRET_KEY={secrets.token_urlsafe(48)}\n"
    "BOITSHOLO_COOKIE_SECURE=0\n"
)
with env_file.open("x") as f:
    f.write(content)
os.chmod(env_file, 0o600)
print("PASS: private login settings created.")
print("Username: Boitsholo")
print("Password and secret key were not displayed.")
