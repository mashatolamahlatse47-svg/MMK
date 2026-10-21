from flask import Flask, request, redirect, session, url_for, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
import sqlite3, secrets, hmac, re, os
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "instance" / "mmk_orders.db"
KEY = ROOT / "instance" / "session.key"
KEY.parent.mkdir(parents=True, exist_ok=True)
if not KEY.exists():
    KEY.write_text(secrets.token_hex(32))
    KEY.chmod(0o600)

app = Flask(__name__)
production = os.environ.get("MMK_ENV", "").lower() == "production"

if production:
    production_key = os.environ.get("MMK_SECRET_KEY", "")
    if len(production_key) < 32:
        raise RuntimeError("Production requires MMK_SECRET_KEY of at least 32 characters.")
    if os.environ.get("MMK_HTTPS", "").lower() != "true":
        raise RuntimeError("Production requires MMK_HTTPS=true.")
    app.secret_key = production_key
else:
    app.secret_key = KEY.read_text().strip()

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=production or os.environ.get("MMK_HTTPS", "").lower() == "true",
)

from contextlib import contextmanager

@contextmanager
def dbopen():
    d = sqlite3.connect(DB)
    d.row_factory = sqlite3.Row
    d.execute("PRAGMA foreign_keys=ON")
    try:
        yield d
        d.commit()
    except Exception:
        d.rollback()
        raise
    finally:
        d.close()

with dbopen() as d:
    d.executescript("""
    CREATE TABLE IF NOT EXISTS shops(
      id INTEGER PRIMARY KEY, name TEXT NOT NULL,
      whatsapp TEXT NOT NULL DEFAULT '',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY,
      shop_id INTEGER NOT NULL REFERENCES shops(id),
      email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS products(
      id INTEGER PRIMARY KEY,
      shop_id INTEGER NOT NULL REFERENCES shops(id),
      name TEXT NOT NULL, price_cents INTEGER NOT NULL CHECK(price_cents>=0),
      active INTEGER NOT NULL DEFAULT 1);
    CREATE TABLE IF NOT EXISTS orders(
      id INTEGER PRIMARY KEY,
      shop_id INTEGER NOT NULL REFERENCES shops(id),
      customer_name TEXT NOT NULL, items_json TEXT NOT NULL,
      total_cents INTEGER NOT NULL CHECK(total_cents>=0),
      status TEXT NOT NULL DEFAULT 'NEW',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    """)

def token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]

@app.before_request
def verify_post():
    if request.method == "POST":
        expected = session.get("csrf", "")
        supplied = request.form.get("csrf", "")
        if not expected or not hmac.compare_digest(expected, supplied):
            return "Security token invalid. Reload and try again.", 400

def page(body, **data):
    return render_template_string("""
    <!doctype html><html><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>MMK Orders</title><style>
    *{box-sizing:border-box}
    body{font:18px/1.6 system-ui,sans-serif;max-width:900px;margin:16px auto;padding:16px;background:#eef2ee;color:#17251d}
    main{background:white;padding:28px;border-radius:18px;box-shadow:0 4px 18px #17251d12}
    h2{font-size:clamp(26px,5vw,36px);line-height:1.2;margin:8px 0 24px}
    h3{font-size:28px;line-height:1.25}
    p{margin:16px 0}
    a{font-weight:650;overflow-wrap:anywhere}
    input,button{width:100%;padding:16px;margin:9px 0;font:inherit;border-radius:10px}
    input{border:2px solid #cbd5cc}
    button{min-height:56px;background:#155e45;color:white;border:0;font-weight:750}
    button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #d6a83b;outline-offset:3px}
    @media(max-width:600px){body{font-size:18px;margin:0;padding:10px}main{padding:20px;border-radius:14px}h3{font-size:26px}}
    </style><main><h2>MMK WhatsApp Order Forms</h2>
    """ + body + """
    <p><small>Local prototype only. Do not enter real customer data.</small></p>
    </main></html>
    """, csrf=token(), **data)

@app.get("/")
def home():
    return redirect(url_for("dashboard") if session.get("user_id") else url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = """
    <h3>Create business account</h3><form method="post">
    <input type="hidden" name="csrf" value="{{csrf}}">
    <label>Business name</label><input name="shop" maxlength="80" required>
    <label>Email</label><input name="email" type="email" maxlength="254" required>
    <label>Password (12+ characters)</label><input name="password" type="password" minlength="12" required>
    <button>Create account</button></form><a href="/login">Log in</a>"""
    if request.method == "GET":
        return page(form)
    shop = request.form.get("shop", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if not shop or len(shop) > 80 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return page(form), 400
    if len(password) < 12 or len(password) > 256:
        return page(form), 400
    try:
        with dbopen() as d:
            with d:
                cur = d.execute("INSERT INTO shops(name) VALUES(?)", (shop,))
                sid = cur.lastrowid
                cur = d.execute("INSERT INTO users(shop_id,email,password_hash) VALUES(?,?,?)",
                                (sid, email, generate_password_hash(password)))
                uid = cur.lastrowid
    except sqlite3.IntegrityError:
        return page(form + "<p>Email already registered.</p>"), 409
    session.clear()
    session.update(user_id=uid, shop_id=sid, csrf=secrets.token_urlsafe(32))
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = """
    <h3>Owner login</h3><form method="post">
    <input type="hidden" name="csrf" value="{{csrf}}">
    <label>Email</label><input name="email" type="email" required>
    <label>Password</label><input name="password" type="password" required>
    <button>Log in</button></form><a href="/register">Create account</a>"""
    if request.method == "GET":
        return page(form)
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    with dbopen() as d:
        user = d.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        return page(form + "<p>Login failed.</p>"), 401
    session.clear()
    session.update(user_id=user["id"], shop_id=user["shop_id"], csrf=secrets.token_urlsafe(32))
    return redirect(url_for("dashboard"))

@app.get("/dashboard")
def dashboard():
    if not session.get("user_id") or not session.get("shop_id"):
        return redirect(url_for("login"))
    with dbopen() as d:
        shop = d.execute("SELECT id,name FROM shops WHERE id=?",
                         (session["shop_id"],)).fetchone()
        if not shop:
            session.clear()
            return redirect(url_for("login"))
        count = d.execute("SELECT COUNT(*) FROM orders WHERE shop_id=?",
                          (shop["id"],)).fetchone()[0]
        products = d.execute("SELECT COUNT(*) FROM products WHERE shop_id=?",
                             (shop["id"],)).fetchone()[0]
    return page("""<h3>Owner dashboard</h3><p>Business: {{shop['name']}}</p>
    <p>Shop ID: {{shop['id']}}</p><p>Products: {{products}} · Orders: {{count}}</p>
    <p><a href="/products">Manage products</a></p><p><a href="/settings">Shop settings / WhatsApp</a></p><p><a href="/orders">Customer orders</a></p><p>Customer order page: <a href="/shop/{{shop["id"]}}">Open order page</a></p>
    <form method="post" action="/logout"><input type="hidden" name="csrf" value="{{csrf}}">
    <button>Log out</button></form>""", shop=shop, products=products, count=count)


@app.route("/products", methods=["GET", "POST"])
def products_page():
    if not session.get("user_id") or not session.get("shop_id"):
        return redirect(url_for("login"))
    form = """
    <h3>Manage products</h3>
    <form method="post">
    <input type="hidden" name="csrf" value="{{csrf}}">
    <label>Product name</label><input name="name" maxlength="100" required>
    <label>Price in rand (e.g. 12.50)</label>
    <input name="price" inputmode="decimal" maxlength="12" required>
    <button>Add product</button></form>
    <p><a href="/dashboard">Back to dashboard</a></p>
    """
    error = ""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price_text = request.form.get("price", "").strip()
        if not name or len(name) > 100 or not re.fullmatch(r"(?:0|[1-9]\d{0,7})(?:\.\d{1,2})?", price_text):
            error = "<p>Enter a product name and a valid non-negative price (up to 2 decimals).</p>"
            response_status = 400
        else:
            whole, dot, fraction = price_text.partition(".")
            cents = int(whole) * 100 + int((fraction + "00")[:2])
            with dbopen() as d:
                d.execute(
                    "INSERT INTO products(shop_id,name,price_cents,active) VALUES(?,?,?,1)",
                    (session["shop_id"], name, cents)
                )
            return redirect(url_for("products_page"))
    else:
        response_status = 200

    with dbopen() as d:
        rows = d.execute(
            "SELECT id,name,price_cents,active FROM products WHERE shop_id=? ORDER BY id DESC",
            (session["shop_id"],)
        ).fetchall()
    listing = "<h3>Your products</h3>"
    if not rows:
        listing += "<p>No products yet.</p>"
    for item in rows:
        price = f"{item['price_cents'] // 100}.{item['price_cents'] % 100:02d}"
        status = "Active" if item["active"] else "Inactive"
        listing += (
            f"<p>{__import__('html').escape(item['name'])} — R{price} — {status}</p>"
            f'<form method="post" action="/products/{item["id"]}/toggle">'
            '<input type="hidden" name="csrf" value="{{csrf}}">'
            f'<button>{"Deactivate" if item["active"] else "Activate"}</button></form>'
        )
    return page(form + error + listing), response_status


@app.post("/products/<int:product_id>/toggle")
def toggle_product(product_id):
    if not session.get("user_id") or not session.get("shop_id"):
        return redirect(url_for("login"))
    with dbopen() as d:
        d.execute(
            "UPDATE products SET active=CASE active WHEN 1 THEN 0 ELSE 1 END "
            "WHERE id=? AND shop_id=?",
            (product_id, session["shop_id"])
        )
        changed = d.execute("SELECT changes()").fetchone()[0]
    if not changed:
        return "Product not found.", 404
    return redirect(url_for("products_page"))


@app.route("/shop/<int:shop_id>", methods=["GET", "POST"])
def customer_order(shop_id):
    with dbopen() as d:
        shop = d.execute(
            "SELECT id,name,whatsapp FROM shops WHERE id=?", (shop_id,)
        ).fetchone()
        products = d.execute(
            "SELECT id,name,price_cents FROM products "
            "WHERE shop_id=? AND active=1 ORDER BY name",
            (shop_id,)
        ).fetchall()
    if not shop:
        return "Shop not found.", 404

    if request.method == "GET":
        if not products:
            return page("<p>This shop has no available products.</p>")
        fields = ""
        for product in products:
            price = f"{product['price_cents']//100}.{product['price_cents']%100:02d}"
            fields += (
                f"<label>{__import__('html').escape(product['name'])} — R{price}</label>"
                f'<input type="number" min="0" max="99" value="0" '
                f'name="qty_{product["id"]}">'
            )
        body = (
            f"<h3>Order from {__import__('html').escape(shop['name'])}</h3>"
            '<form method="post"><input type="hidden" name="csrf" value="{{csrf}}">'
            '<label>Your name</label><input name="customer_name" maxlength="100" required>'
            + fields + '<button>Prepare WhatsApp order</button></form>'
        )
        return page(body)

    customer = request.form.get("customer_name", "").strip()
    if not customer or len(customer) > 100:
        return page("<p>Please enter a valid name.</p>"), 400

    items, total = [], 0
    for product in products:
        raw = request.form.get(f"qty_{product['id']}", "0").strip()
        if not re.fullmatch(r"\d{1,2}", raw):
            return page("<p>Invalid quantity. Please try again.</p>"), 400
        qty = int(raw)
        if qty:
            line_total = qty * product["price_cents"]
            total += line_total
            items.append({
                "product_id": product["id"], "name": product["name"],
                "quantity": qty, "unit_price_cents": product["price_cents"],
                "line_total_cents": line_total
            })
    if not items or total <= 0:
        return page("<p>Please choose at least one product.</p>"), 400

    import json
    with dbopen() as d:
        cur = d.execute(
            "INSERT INTO orders(shop_id,customer_name,items_json,total_cents,status) "
            "VALUES(?,?,?,?, 'NEW')",
            (shop_id, customer, json.dumps(items, ensure_ascii=False), total)
        )
        order_id = cur.lastrowid

    lines = [
        f"Order #{order_id} — {shop['name']}",
        f"Customer: {customer}"
    ]
    for item in items:
        lines.append(
            f"{item['quantity']} x {item['name']} "
            f"@ R{item['unit_price_cents']/100:.2f} "
            f"= R{item['line_total_cents']/100:.2f}"
        )
    lines.append(f"TOTAL: R{total/100:.2f}")
    message = quote("\n".join(lines))
    number = re.sub(r"\D", "", shop["whatsapp"] or "")
    if number.startswith("0"):
        number = "27" + number[1:]
    if not number:
        return page(
            f"<p>Order #{order_id} saved, but this shop has not set a WhatsApp number.</p>"
            f"<p>Total: R{total/100:.2f}</p>"
        )
    return page(
        f"<h3>Order #{order_id} saved</h3>"
        f"<p>Total: R{total/100:.2f}</p>"
        f'<p><a href="https://wa.me/{number}?text={message}" '
        'target="_blank" rel="noopener">Continue to WhatsApp</a></p>'
        '<p>Send the message in WhatsApp to place your request.</p>'
    )


@app.route("/settings", methods=["GET", "POST"])
def shop_settings():
    if not session.get("user_id") or not session.get("shop_id"):
        return redirect(url_for("login"))
    if request.method == "POST":
        number = request.form.get("whatsapp", "").strip()
        if number and not re.fullmatch(r"[+0-9 ()-]{7,25}", number):
            return page("<p>Enter a valid phone number.</p>"), 400
        with dbopen() as d:
            d.execute("UPDATE shops SET whatsapp=? WHERE id=?",
                      (number, session["shop_id"]))
        return redirect(url_for("shop_settings"))
    with dbopen() as d:
        shop = d.execute("SELECT name,whatsapp FROM shops WHERE id=?",
                         (session["shop_id"],)).fetchone()
    return page(
        f"<h3>Shop settings</h3><p>Customer order link: "
        f"/shop/{session['shop_id']}</p>"
        '<form method="post"><input type="hidden" name="csrf" value="{{csrf}}">'
        f'<label>WhatsApp number for {__import__("html").escape(shop["name"])}</label>'
        f'<input name="whatsapp" value="{__import__("html").escape(shop["whatsapp"], quote=True)}" '
        'placeholder="e.g. 0821234567" maxlength="25">'
        '<button>Save settings</button></form>'
        '<p><a href="/dashboard">Back to dashboard</a></p>'
    )


@app.get("/orders")
def owner_orders():
    if not session.get("user_id") or not session.get("shop_id"):
        return redirect(url_for("login"))
    import json
    with dbopen() as d:
        rows = d.execute(
            "SELECT id,customer_name,items_json,total_cents,status,created_at "
            "FROM orders WHERE shop_id=? ORDER BY id DESC LIMIT 100",
            (session["shop_id"],)
        ).fetchall()
    body = "<h3>Customer orders</h3>"
    if not rows:
        body += "<p>No orders yet.</p>"
    for order in rows:
        body += (
            f"<section><b>Order #{order['id']}</b> — "
            f"{__import__('html').escape(order['customer_name'])}<br>"
            f"Total: R{order['total_cents']//100}.{order['total_cents']%100:02d}"
            f" — {order['status']}<ul>"
        )
        for item in json.loads(order["items_json"]):
            body += (
                f"<li>{__import__('html').escape(item['name'])} × "
                f"{item['quantity']}</li>"
            )
        body += (
            f"</ul><small>{order['created_at']}</small>"
            f' <a href="/orders/{order["id"]}/receipt">View / print receipt</a>'
            '<form method="post" action="/orders/'
            f"{order['id']}/status" + '">'
            '<input type="hidden" name="csrf" value="{{csrf}}">'
            '<select name="status">'
            '<option value="CONFIRMED">Confirmed</option>'
            '<option value="COMPLETED">Completed</option>'
            '<option value="CANCELLED">Cancelled</option>'
            '</select><button>Update status</button></form></section>'
        )
    body += '<p><a href="/dashboard">Back to dashboard</a></p>'
    return page(body)




@app.get("/orders/<int:order_id>/receipt")
def order_receipt(order_id):
    if not session.get("user_id") or not session.get("shop_id"):
        return redirect(url_for("login"))

    import json
    from html import escape
    with dbopen() as d:
        row = d.execute(
            "SELECT o.id,o.customer_name,o.items_json,o.total_cents,"
            "o.status,o.created_at,s.name AS shop_name "
            "FROM orders o JOIN shops s ON s.id=o.shop_id "
            "WHERE o.id=? AND o.shop_id=?",
            (order_id, session["shop_id"])
        ).fetchone()

    if not row:
        return "Receipt not found.", 404

    body = (
        '<div class="receipt">'
        f'<h2>{escape(row["shop_name"])}</h2>'
        '<h3>ORDER RECEIPT</h3>'
        f'<p>Receipt / Order #: {row["id"]}</p>'
        f'<p>Customer: {escape(row["customer_name"])}</p>'
        f'<p>Date: {escape(row["created_at"])}</p>'
        f'<p>Status: {escape(row["status"])}</p>'
        '<table><thead><tr><th>Item</th><th>Qty</th>'
        '<th>Unit price</th><th>Line total</th></tr></thead><tbody>'
    )
    for item in json.loads(row["items_json"]):
        unit = item["unit_price_cents"]
        line = item["line_total_cents"]
        body += (
            '<tr>'
            f'<td>{escape(str(item["name"]))}</td>'
            f'<td>{item["quantity"]}</td>'
            f'<td>R{unit // 100}.{unit % 100:02d}</td>'
            f'<td>R{line // 100}.{line % 100:02d}</td>'
            '</tr>'
        )
    total = row["total_cents"]
    body += (
        '</tbody></table>'
        f'<h3>TOTAL: R{total // 100}.{total % 100:02d}</h3>'
        '<p>Thank you for your order!</p>'
        '<button onclick="window.print()">Print / Save PDF</button> '
        '<a href="/orders">Back to orders</a></div>'
        '<style>@media print{button,a{display:none}}'
        '.receipt{max-width:700px;margin:auto;padding:18px}'
        'table{width:100%;border-collapse:collapse}'
        'th,td{border-bottom:1px solid #aaa;padding:8px;text-align:left}'
        '</style>'
    )
    return page(body)

@app.post("/orders/<int:order_id>/status")
def update_order_status(order_id):
    if not session.get("user_id") or not session.get("shop_id"):
        return redirect(url_for("login"))

    status = request.form.get("status", "")
    allowed = {"CONFIRMED", "COMPLETED", "CANCELLED"}
    if status not in allowed:
        return page("<p>Invalid order status.</p>"), 400

    with dbopen() as d:
        cur = d.execute(
            "UPDATE orders SET status=? WHERE id=? AND shop_id=?",
            (status, order_id, session["shop_id"])
        )
        changed = cur.rowcount
    if not changed:
        return "Order not found.", 404
    return redirect(url_for("owner_orders"))

@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/health")
def health():
    with dbopen() as d:
        d.execute("SELECT 1").fetchone()
    return {"status": "ok", "database": "ok"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8091, debug=False)
