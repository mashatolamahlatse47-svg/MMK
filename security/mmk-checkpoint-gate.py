#!/usr/bin/env python3

import getpass
import hashlib
import json
import os
import secrets
import sys
from pathlib import Path

BASE_DIR = Path.home() / "MMK"
SECURITY_DIR = BASE_DIR / "private" / "checkpoint-security"
CREDENTIAL_FILE = SECURITY_DIR / "credentials.json"

PBKDF2_ITERATIONS = 600_000


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS
    ).hex()


def setup_password():
    SECURITY_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(SECURITY_DIR, 0o700)

    print("================================")
    print("MMK CHECKPOINT SECURITY SETUP")
    print("================================")
    print()
    print("Create your MMK master checkpoint password.")
    print("Do NOT share this password with anyone.")
    print()

    password = getpass.getpass("Create password: ")

    if len(password) < 12:
        print("ERROR: Password must contain at least 12 characters.")
        return 1

    confirmation = getpass.getpass("Confirm password: ")

    if password != confirmation:
        print("ERROR: Passwords do not match.")
        return 1

    salt = secrets.token_bytes(32)
    password_hash = hash_password(password, salt)

    data = {
        "algorithm": "PBKDF2-HMAC-SHA256",
        "iterations": PBKDF2_ITERATIONS,
        "salt": salt.hex(),
        "password_hash": password_hash
    }

    CREDENTIAL_FILE.write_text(json.dumps(data, indent=2))
    os.chmod(CREDENTIAL_FILE, 0o600)

    print()
    print("================================")
    print("MMK CHECKPOINT PASSWORD CREATED")
    print("================================")
    print("Password is stored as a cryptographic hash.")
    print("Plain-text password is NOT stored.")
    print()
    print("CHECKPOINT SECURITY: READY")
    return 0


def verify_password():
    if not CREDENTIAL_FILE.exists():
        print("ERROR: MMK checkpoint password has not been configured.")
        print()
        print("Run:")
        print("  ./security/mmk-checkpoint-gate.sh --setup")
        return False

    try:
        data = json.loads(CREDENTIAL_FILE.read_text())

        salt = bytes.fromhex(data["salt"])
        stored_hash = data["password_hash"]
        iterations = int(data["iterations"])

        password = getpass.getpass("MMK checkpoint password: ")

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations
        ).hex()

        return secrets.compare_digest(calculated_hash, stored_hash)

    except Exception:
        print("ERROR: Checkpoint security configuration could not be read.")
        return False


def unlock_checkpoint(checkpoint):
    print("================================")
    print("MMK CHECKPOINT SECURITY")
    print("================================")
    print(f"Checkpoint: {checkpoint}")
    print()

    if not verify_password():
        print()
        print("================================")
        print("ACCESS DENIED")
        print("================================")
        print("Checkpoint remains LOCKED.")
        return 1

    print()
    print("================================")
    print("ACCESS GRANTED")
    print("================================")
    print(f"Checkpoint unlocked: {checkpoint}")
    print("Proceed with authorized MMK work.")
    return 0


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--setup":
        return setup_password()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./security/mmk-checkpoint-gate.sh --setup")
        print("  ./security/mmk-checkpoint-gate.sh \"O.B. 8.12 Security Hardening\"")
        return 1

    checkpoint = " ".join(sys.argv[1:]).strip()

    if not checkpoint:
        print("ERROR: Checkpoint name cannot be empty.")
        return 1

    return unlock_checkpoint(checkpoint)


if __name__ == "__main__":
    sys.exit(main())
