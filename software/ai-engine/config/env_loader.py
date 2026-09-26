"""Minimal MMK environment loader.

Loads ~/MMK/.env without requiring an additional dependency.
Never prints secret values.
"""

import os
from pathlib import Path


def load_mmk_env() -> None:
    """Load ~/MMK/.env variables into the current process."""
    env_file = Path.home() / "MMK" / ".env"

    if not env_file.is_file():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key and key.isidentifier() and key not in os.environ:
            os.environ[key] = value
