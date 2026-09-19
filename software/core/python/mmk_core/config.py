"""MMK Core configuration loader."""

import json
from pathlib import Path


CONFIG_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "mmk.json"
)


def load_config():
    """Load the central MMK configuration."""
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)
