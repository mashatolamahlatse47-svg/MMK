from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
CONFIG_FILE = ROOT / "config" / "product.json"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def mmk_info():
    config = load_config()

    return {
        "brand": config["brand"],
        "company": config["company"],
        "version": config["version"],
        "environment": config["environment"],
    }


if __name__ == "__main__":
    print(mmk_info())
