import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys

ENGINE_ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ENGINE_ROOT / "core"
WEBSITE_PATH = ENGINE_ROOT / "website"

sys.path.insert(0, str(ENGINE_ROOT))

from core.engine import SmallBusinessEngine
from core.reports import ReportsEngine


DB_PATH = os.environ.get("MMK_ENGINE_DB")
engine = SmallBusinessEngine(DB_PATH) if DB_PATH else SmallBusinessEngine()
reports = ReportsEngine(engine)


class APIHandler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            self.send_json(200, {
                "status": "ok",
                "service": "MMK Small Business Engine"
            })
            return

        if self.path == "/":
            self.send_json(200, {
                "message": "MMK Small Business Engine API"
            })
            return

        if self.path == "/api/stock":
            with engine.connect() as conn:
                business = conn.execute(
                    """
                    SELECT id, name, currency
                    FROM businesses
                    ORDER BY id
                    LIMIT 1
                    """
                ).fetchone()

                if business is None:
                    self.send_json(200, {
                        "business": None,
                        "products": []
                    })
                    return

                products = conn.execute(
                    """
                    SELECT
                        p.id,
                        p.name,
                        p.unit,
                        p.selling_price_cents,
                        COALESCE(cs.quantity_on_hand, 0) AS quantity_on_hand
                    FROM products p
                    LEFT JOIN current_stock cs
                        ON cs.business_id = p.business_id
                        AND cs.product_id = p.id
                    WHERE p.business_id = ?
                    ORDER BY p.id
                    """,
                    (business["id"],)
                ).fetchall()

            self.send_json(200, {
                "business": {
                    "id": business["id"],
                    "name": business["name"],
                    "currency": business["currency"]
                },
                "products": [
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "unit": row["unit"],
                        "selling_price_cents": row["selling_price_cents"],
                        "quantity_on_hand": row["quantity_on_hand"]
                    }
                    for row in products
                ]
            })
            return

        if self.path == "/api/dashboard":
            with engine.connect() as conn:
                business = conn.execute(
                    """
                    SELECT id, name, currency
                    FROM businesses
                    ORDER BY id
                    LIMIT 1
                    """
                ).fetchone()

                if business is None:
                    self.send_json(200, {
                        "business": None,
                        "stock_units": 0,
                        "revenue_cents": 0,
                        "outstanding_credit_cents": 0,
                        "expenses_cents": 0
                    })
                    return

                business_id = business["id"]

                stock = conn.execute(
                    """
                    SELECT COALESCE(SUM(quantity_delta), 0) AS total
                    FROM stock_movements
                    WHERE business_id = ?
                    """,
                    (business_id,)
                ).fetchone()["total"]

                summary = reports.financial_summary(business_id)

                revenue = summary["revenue_cents"]
                credit = summary["credit_outstanding_cents"]
                expenses = summary["expenses_cents"]
                cash_collected = summary["cash_collected_cents"]
                net_profit = summary["net_profit_cents"]

            self.send_json(200, {
                "business": {
                    "id": business["id"],
                    "name": business["name"],
                    "currency": business["currency"]
                },
                "stock_units": stock,
                "revenue_cents": revenue,
                "cash_collected_cents": cash_collected,
                "outstanding_credit_cents": credit,
                "expenses_cents": expenses,
                "net_profit_cents": net_profit
            })
            return

        self.send_json(404, {
            "error": "Route not found"
        })


if __name__ == "__main__":
    server = ThreadingHTTPServer(
        ("127.0.0.1", 8090),
        APIHandler
    )

    print("MMK Small Business Engine API")
    print("Running on http://127.0.0.1:8090")
    print("Health check: http://127.0.0.1:8090/api/health")

    server.serve_forever()
