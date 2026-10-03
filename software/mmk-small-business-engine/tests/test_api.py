import json
import os
import tempfile
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
    TEST_DB = temp_db.name

os.environ["MMK_ENGINE_DB"] = TEST_DB

from api.server import APIHandler, engine

HOST = "127.0.0.1"
PORT = 18090


def get_json(path):
    with urllib.request.urlopen(
        f"http://{HOST}:{PORT}{path}",
        timeout=5,
    ) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


def prepare_test_data():
    business_id = engine.create_business("API Test Business")
    product_id = engine.create_product(
        business_id,
        "Test Product",
        "unit",
        1500,
    )
    engine.create_stock_batch(
        business_id,
        product_id,
        "API-TEST-BATCH-001",
        10,
        5000,
        "2026-10-02",
    )


def main():
    prepare_test_data()

    server = ThreadingHTTPServer((HOST, PORT), APIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        print("=== API TEST ===")

        status, data = get_json("/api/health")
        assert status == 200
        assert data["status"] == "ok"
        print("[OK] Health endpoint")

        status, data = get_json("/api/dashboard")
        assert status == 200
        assert data["business"]["name"] == "API Test Business"
        assert data["stock_units"] == 10
        assert data["revenue_cents"] == 0
        assert data["outstanding_credit_cents"] == 0
        assert data["expenses_cents"] == 0
        assert data["cash_collected_cents"] == 0
        assert data["net_profit_cents"] == 0
        print("[OK] Dashboard endpoint")

        status, data = get_json("/api/stock")
        assert status == 200
        assert data["business"]["name"] == "API Test Business"
        assert len(data["products"]) == 1
        assert data["products"][0]["name"] == "Test Product"
        assert data["products"][0]["quantity_on_hand"] == 10
        print("[OK] Stock endpoint")

        print()
        print("=== API TEST PASSED ===")

    finally:
        server.shutdown()
        server.server_close()

        try:
            Path(TEST_DB).unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    main()
