import os
import re
import secrets
import sqlite3
import time
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import (
    Flask, abort, flash, g, redirect, render_template_string,
    request, session, url_for
)
from werkzeug.security import check_password_hash

# Load private local settings without displaying their contents.
ENV_FILE = Path(__file__).resolve().parent / ".env"
if ENV_FILE.is_file():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            if key and key not in __import__("os").environ:
                __import__("os").environ[key] = value.strip()

LOGIN_MAX_FAILURES = 5
LOGIN_WINDOW_SECONDS = 15 * 60
_LOGIN_FAILURES = {}

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
app.secret_key = os.environ.get("BOITSHOLO_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("Missing BOITSHOLO_SECRET_KEY. Configure private settings first.")

app.config.update(
    DATABASE=str(BASE / "instance" / "boitsholo.db"),
    AUTH_USERNAME=os.environ.get("BOITSHOLO_USERNAME", ""),
    AUTH_PASSWORD_HASH=os.environ.get("BOITSHOLO_PASSWORD_HASH", ""),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("BOITSHOLO_COOKIE_SECURE", "0") == "1",
)

if not app.config["AUTH_USERNAME"] or not app.config["AUTH_PASSWORD_HASH"]:
    raise RuntimeError("Missing staff login settings. Configure private settings first.")

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT NOT NULL,
    location TEXT NOT NULL,
    served_by TEXT NOT NULL,
    approver TEXT NOT NULL DEFAULT '',
    amount_paid INTEGER NOT NULL CHECK(amount_paid >= 0),
    total INTEGER NOT NULL CHECK(total > 0),
    change_owed INTEGER NOT NULL CHECK(change_owed >= 0),
    status TEXT NOT NULL CHECK(status IN ('PENDING','GIVEN','NO_CHANGE')),
    created_at TEXT NOT NULL,
    confirmed_at TEXT,
    confirmed_by TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id),
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price INTEGER NOT NULL CHECK(unit_price >= 0),
    line_total INTEGER NOT NULL CHECK(line_total >= 0)
);

CREATE TABLE IF NOT EXISTS money_owed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person TEXT NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('BUSINESS_OWES','OWES_BUSINESS')),
    reason TEXT NOT NULL,
    amount INTEGER NOT NULL CHECK(amount > 0),
    status TEXT NOT NULL DEFAULT 'OPEN' CHECK(status IN ('OPEN','SETTLED')),
    created_at TEXT NOT NULL,
    recorded_by TEXT NOT NULL,
    settled_at TEXT,
    settled_by TEXT NOT NULL DEFAULT ''
);

"""

def money_to_cents(value):
    try:
        amount = Decimal(str(value).strip().replace(",", "."))
        if not amount.is_finite() or amount < 0:
            raise ValueError("Enter a valid non-negative amount.")
        if amount.as_tuple().exponent < -2:
            raise ValueError("Use no more than two decimal places.")
        return int(amount * 100)
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid amount, for example 25 or 25.50.")

def money(cents):
    return f"R{cents / 100:,.2f}"

app.jinja_env.filters["money"] = money

class PostgresAdapter:
    postgres = True

    def __init__(self, connection):
        self.connection = connection

    def execute(self, sql, params=()):
        return self.connection.execute(sql.replace("?", "%s"), params)

    def executemany(self, sql, rows):
        cursor = self.connection.cursor()
        cursor.executemany(sql.replace("?", "%s"), rows)
        return cursor

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


def get_db():
    if "db" not in g:
        database_url = os.environ.get("DATABASE_URL", "").strip()
        if database_url:
            import psycopg
            from psycopg.rows import dict_row

            connection = psycopg.connect(
                database_url, row_factory=dict_row, connect_timeout=10
            )
            g.db = PostgresAdapter(connection)
            schema = SCHEMA.replace(
                "INTEGER PRIMARY KEY AUTOINCREMENT", "BIGSERIAL PRIMARY KEY"
            )
            for statement in schema.split(";"):
                if statement.strip():
                    g.db.execute(statement)
            g.db.commit()
        else:
            Path(app.config["DATABASE"]).parent.mkdir(
                parents=True, exist_ok=True
            )
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
            g.db.executescript(SCHEMA)
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(24)
    return session["csrf"]

def check_csrf():
    if not session.get("csrf") or not secrets.compare_digest(
        session["csrf"], request.form.get("csrf", "")
    ):
        abort(400, description="Form expired. Reload and try again.")

PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} · Boitsholo</title>
<style>
:root{color-scheme:dark;--bg:#101114;--panel:#1b1d22;--gold:#e7bd66;
--muted:#b8bac2;--line:#373941;--green:#8fe0ad}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:#f7f7f8;font:16px/1.5 system-ui,sans-serif}
header,main{max-width:900px;margin:auto;padding:18px}
header{border-bottom:1px solid var(--line)}
.brand{color:var(--gold);font-size:1.45rem;font-weight:800;letter-spacing:.08em}
small,.muted{color:var(--muted)}
nav{display:flex;gap:16px;margin-top:10px;flex-wrap:wrap}
a{color:var(--gold)}
h1{font-size:1.5rem}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;
padding:16px;margin:16px 0}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
label{display:block;font-weight:600;margin-bottom:5px}
input{width:100%;min-width:0;padding:12px;border-radius:8px;
border:1px solid #50525b;background:#111216;color:white;font:inherit}
button,.button{display:inline-block;border:0;border-radius:9px;padding:12px 15px;
background:var(--gold);color:#17130b;font-weight:750;font-size:1rem;cursor:pointer}
.secondary{background:#333640;color:white}
.danger{color:#ffccba}
.row{display:grid;grid-template-columns:2fr .7fr 1fr auto;gap:8px;margin:10px 0;align-items:end}
.row label{font-size:.85rem}
.summary{font-size:1.2rem;display:flex;justify-content:space-between;gap:12px}
.amount{font-size:1.8rem;font-weight:800;color:var(--green)}
table{width:100%;border-collapse:collapse}
th,td{text-align:left;padding:10px 7px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-size:.85rem}
.table-wrap{overflow-x:auto}
.status{font-weight:750}
.pending{color:#ffd27b}.given{color:var(--green)}
.flash{padding:10px;border-radius:8px;background:#333640;margin:8px 0}
@media(max-width:560px){.grid{grid-template-columns:1fr}.row{grid-template-columns:1fr 1fr}
.row .item-name{grid-column:1/-1}.row button{padding:10px}
table{font-size:.9rem}}
</style>
</head>
<body>
<header>
  <div class="brand">BOITSHOLO</div>
  <div class="muted">Catering & Event Services</div>
  {% if session.get('staff_username') %}
  <nav>
    <a href="{{ url_for('index') }}">Transaction history</a>
    <a href="{{ url_for('new_transaction') }}">+ New record</a>
    <a href="{{ url_for('money_owed') }}">Money Owed</a>
    <form method="post" action="{{ url_for('logout') }}" style="margin:0">
      <input type="hidden" name="csrf" value="{{ token }}">
      <button type="submit" class="secondary">Sign out</button>
    </form>
  </nav>
  {% endif %}
</header>
<main>
{% for message in get_flashed_messages() %}
<div class="flash">{{ message }}</div>
{% endfor %}
{{ body|safe }}
<footer class="muted"><small>MMK Software · Boitsholo transaction tracker</small></footer>
</main>
</body>
</html>
"""

LOGIN = """
<div class="card">
  <h1>Staff sign in</h1>
  <p class="muted">Sign in to access the Boitsholo transaction tracker.</p>
  <form method="post" action="{{ url_for('login') }}">
    <input type="hidden" name="csrf" value="{{ token }}">
    <label for="username">Staff username</label>
    <input id="username" name="username" autocomplete="username"
           required maxlength="100">
    <label for="password" style="margin-top:12px">Password</label>
    <input id="password" name="password" type="password"
           autocomplete="current-password" required>
    <button type="submit" style="margin-top:16px">Sign in</button>
  </form>
</div>
"""

FORM = """
<h1>New customer transaction</h1>
<p class="muted">Enter the items manually. Change remains pending until staff confirm it was given.</p>
<form method="post" action="{{ url_for('new_transaction') }}" class="card" id="sale-form">
<input type="hidden" name="csrf" value="{{ token }}">
<div class="grid">
<div><label>Customer / worker name *</label>
<input name="customer" required maxlength="120" autocomplete="off"></div>
<div><label>Where were items taken? *</label>
<input name="location" required maxlength="160" placeholder="Counter, venue or event"></div>
<div><label>Staff member serving *</label>
<input name="served_by" required maxlength="120"></div>
<div><label>Approver (if required)</label>
<input name="approver" maxlength="120"></div>
</div>
<h2>Items taken</h2>
<div id="items">
<div class="row">
<div class="item-name"><label>Item name *</label><input name="item_name" required maxlength="120"></div>
<div><label>Quantity *</label><input name="quantity" type="number" min="1" step="1" value="1" required></div>
<div><label>Price each (R) *</label><input name="price" type="number" min="0" step="0.01" placeholder="0.00" required></div>
</div>
</div>
<button type="button" class="secondary" id="add-row">+ Add another item</button>
<div style="margin-top:18px"><label>Amount paid (R) *</label>
<input name="amount_paid" type="number" min="0" step="0.01" required placeholder="0.00"></div>
<p class="muted">The total and change will be calculated and saved when you submit.</p>
<button type="submit">Save transaction</button>
</form>
<script>
const items=document.getElementById('items');
document.getElementById('add-row').addEventListener('click',()=>{
 const row=document.createElement('div');
 row.className='row';
 row.innerHTML='<div class="item-name"><label>Item name *</label><input name="item_name" required maxlength="120"></div>'+
 '<div><label>Quantity *</label><input name="quantity" type="number" min="1" step="1" value="1" required></div>'+
 '<div><label>Price each (R) *</label><input name="price" type="number" min="0" step="0.01" required placeholder="0.00"></div>'+
 '<button type="button" class="secondary remove">Remove</button>';
 items.appendChild(row);
 row.querySelector('.remove').addEventListener('click',()=>row.remove());
});
</script>
"""

DETAIL = """
<h1>Transaction #{{ tx.id }}</h1>
<div class="card">
<p><b>Customer / worker:</b> {{ tx.customer }}</p>
<p><b>Location:</b> {{ tx.location }}</p>
<p><b>Served by:</b> {{ tx.served_by }}</p>
<p><b>Approver:</b> {{ tx.approver or 'Not recorded' }}</p>
<p><b>Date and time:</b> {{ tx.created_at }}</p>
<div class="table-wrap"><table><thead><tr><th>Item</th><th>Qty</th>
<th>Each</th><th>Line total</th></tr></thead><tbody>
{% for item in items %}<tr><td>{{ item.item_name }}</td><td>{{ item.quantity }}</td>
<td>{{ item.unit_price|money }}</td><td>{{ item.line_total|money }}</td></tr>{% endfor %}
</tbody></table></div>
<p class="summary"><span>Total cost</span><b>{{ tx.total|money }}</b></p>
<p class="summary"><span>Amount paid</span><b>{{ tx.amount_paid|money }}</b></p>
<p class="summary"><span>Change owed</span><b class="amount">{{ tx.change_owed|money }}</b></p>
<p>Status:
<span class="status {{ 'pending' if tx.status == 'PENDING' else 'given' }}">
{{ {'PENDING':'CHANGE PENDING','GIVEN':'CHANGE GIVEN','NO_CHANGE':'NO CHANGE DUE'}[tx.status] }}
</span></p>
{% if tx.status == 'PENDING' %}
<form method="post" action="{{ url_for('confirm_change', tx_id=tx.id) }}">
<input type="hidden" name="csrf" value="{{ token }}">
<label>Staff member confirming change was given *</label>
<input name="confirmed_by" required maxlength="120" placeholder="Enter your name">
<p class="muted">Only press this after physically handing the change to the customer.</p>
<button type="submit">Mark Change as Given</button>
</form>
{% elif tx.status == 'GIVEN' %}
<p><b>Confirmed by:</b> {{ tx.confirmed_by }}</p>
<p><b>Confirmation time:</b> {{ tx.confirmed_at }}</p>
{% endif %}
</div>
<a href="{{ url_for('index') }}">← Back to transaction history</a>
"""

@app.before_request
def require_staff_login():
    if request.endpoint in ("login", "static"):
        return None
    if not session.get("staff_username"):
        return redirect(url_for("login", next=request.path))
    return None


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("staff_username"):
            return redirect(url_for("index"))
        return render_template_string(
            PAGE, title="Staff sign in", token=csrf_token(),
            body=render_template_string(LOGIN, token=csrf_token())
        )

    check_csrf()
    client_ip = request.remote_addr or "unknown"
    now = time.monotonic()
    attempts = [
        stamp for stamp in _LOGIN_FAILURES.get(client_ip, [])
        if now - stamp < LOGIN_WINDOW_SECONDS
    ]
    _LOGIN_FAILURES[client_ip] = attempts
    if len(attempts) >= LOGIN_MAX_FAILURES:
        flash("Too many sign-in attempts. Please wait 15 minutes.")
        return redirect(url_for("login"))

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    expected_username = app.config["AUTH_USERNAME"]
    password_hash = app.config["AUTH_PASSWORD_HASH"]
    username_ok = secrets.compare_digest(username, expected_username)
    password_ok = check_password_hash(password_hash, password)

    if not (username_ok and password_ok):
        _LOGIN_FAILURES.setdefault(client_ip, []).append(now)
        flash("Sign-in failed. Check your username and password.")
        return redirect(url_for("login"))

    _LOGIN_FAILURES.pop(client_ip, None)
    session.clear()
    session["staff_username"] = expected_username
    session["csrf"] = secrets.token_urlsafe(24)
    return redirect(url_for("index"))


@app.post("/logout")
def logout():
    check_csrf()
    session.clear()
    flash("You have signed out.")
    return redirect(url_for("login"))


@app.get("/")
def index():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM transactions ORDER BY id DESC LIMIT 200"
    ).fetchall()
    body = """
    <h1>Transaction history</h1>
    <p class="muted">Latest 200 records. No expected-cash or cash-float tracking.</p>
    <a class="button" href="{{ url_for('new_transaction') }}">+ New transaction</a>
    <form method="post" action="{{ url_for('clear_history') }}"
          onsubmit="return confirm('Permanently clear all transaction history and associated line items? This cannot be undone without restoring a backup.');"
          style="margin-top:12px">
      <input type="hidden" name="csrf" value="{{ token }}">
      <button type="submit" style="background:#8d2f2f;color:#fff;border:0;padding:12px 16px;border-radius:9px;font-weight:700">Clear Transaction History</button>
    </form>
    <div class="card table-wrap"><table><thead><tr>
    <th>Record / time</th><th>Customer</th><th>Total</th><th>Paid</th>
    <th>Change</th><th>Status</th></tr></thead><tbody>
    {% for tx in rows %}<tr>
    <td><a href="{{ url_for('transaction_detail', tx_id=tx.id) }}">#{{ tx.id }}</a><br>
    <small>{{ tx.created_at }}</small></td><td>{{ tx.customer }}</td>
    <td>{{ tx.total|money }}</td><td>{{ tx.amount_paid|money }}</td>
    <td>{{ tx.change_owed|money }}</td>
    <td class="status {{ 'pending' if tx.status == 'PENDING' else 'given' }}">
    {{ {'PENDING':'Pending','GIVEN':'Given','NO_CHANGE':'No change'}[tx.status] }}</td>
    </tr>{% else %}<tr><td colspan="6">No transactions recorded yet.</td></tr>{% endfor %}
    </tbody></table></div>
    """
    return render_template_string(PAGE, title="History", body=render_template_string(
        body, rows=rows, token=csrf_token()
    ), token=csrf_token())

@app.route("/new", methods=["GET", "POST"])
def new_transaction():
    if request.method == "GET":
        return render_template_string(
            PAGE, title="New transaction", token=csrf_token(),
            body=render_template_string(FORM, token=csrf_token())
        )
    check_csrf()
    customer = request.form.get("customer", "").strip()
    location = request.form.get("location", "").strip()
    served_by = request.form.get("served_by", "").strip()
    approver = request.form.get("approver", "").strip()
    if not customer or not location or not served_by:
        flash("Enter the customer, location and serving worker.")
        return redirect(url_for("new_transaction"))

    names = request.form.getlist("item_name")
    quantities = request.form.getlist("quantity")
    prices = request.form.getlist("price")
    if not (len(names) == len(quantities) == len(prices)):
        abort(400, description="Item fields do not match.")

    items = []
    total = 0
    try:
        for name, qty_text, price_text in zip(names, quantities, prices):
            name = name.strip()
            if not name and not qty_text and not price_text:
                continue
            if not name or not re.fullmatch(r"[1-9][0-9]*", qty_text.strip()):
                raise ValueError("Each item needs a name and a whole-number quantity.")
            qty = int(qty_text)
            if qty > 100000:
                raise ValueError("Quantity is too large.")
            unit_price = money_to_cents(price_text)
            line_total = qty * unit_price
            if line_total > 100000000000:
                raise ValueError("Item total is too large.")
            items.append((name, qty, unit_price, line_total))
            total += line_total
        if not items or total <= 0:
            raise ValueError("Enter at least one item with a total above R0.00.")
        paid = money_to_cents(request.form.get("amount_paid", ""))
        if paid < total:
            raise ValueError("Amount paid is less than the total cost.")
    except (ValueError, InvalidOperation) as exc:
        flash(str(exc))
        return redirect(url_for("new_transaction"))

    change = paid - total
    status = "PENDING" if change > 0 else "NO_CHANGE"
    db = get_db()
    insert_sql = """INSERT INTO transactions
        (customer,location,served_by,approver,amount_paid,total,change_owed,
         status,created_at) VALUES (?,?,?,?,?,?,?,?,?)"""
    params = (
        customer, location, served_by, approver, paid, total, change,
        status, datetime.now().astimezone().isoformat(timespec="seconds")
    )
    if getattr(db, "postgres", False):
        cur = db.execute(insert_sql + " RETURNING id", params)
        tx_id = cur.fetchone()["id"]
    else:
        cur = db.execute(insert_sql, params)
        tx_id = cur.lastrowid
    db.executemany(
        """INSERT INTO items
        (transaction_id,item_name,quantity,unit_price,line_total)
        VALUES (?,?,?,?,?)""",
        [(tx_id, *item) for item in items]
    )
    db.commit()
    flash("Transaction saved. Change remains pending until staff confirm it was given."
          if change else "Transaction saved. No change is due.")
    return redirect(url_for("transaction_detail", tx_id=tx_id))

@app.get("/transaction/<int:tx_id>")
def transaction_detail(tx_id):
    db = get_db()
    tx = db.execute("SELECT * FROM transactions WHERE id=?", (tx_id,)).fetchone()
    if tx is None:
        abort(404)
    items = db.execute(
        "SELECT * FROM items WHERE transaction_id=? ORDER BY id", (tx_id,)
    ).fetchall()
    return render_template_string(
        PAGE, title=f"Transaction {tx_id}", token=csrf_token(),
        body=render_template_string(
            DETAIL, tx=tx, items=items, token=csrf_token()
        )
    )

@app.post("/transaction/<int:tx_id>/confirm")
def confirm_change(tx_id):
    check_csrf()
    confirmed_by = request.form.get("confirmed_by", "").strip()
    if not confirmed_by:
        flash("Enter the name of the staff member confirming the change.")
        return redirect(url_for("transaction_detail", tx_id=tx_id))
    db = get_db()
    cur = db.execute(
        """UPDATE transactions
        SET status='GIVEN', confirmed_by=?, confirmed_at=?
        WHERE id=? AND status='PENDING' AND change_owed>0""",
        (confirmed_by, datetime.now().astimezone().isoformat(timespec="seconds"),
         tx_id)
    )
    db.commit()
    if cur.rowcount == 1:
        flash("Change confirmation recorded.")
    else:
        flash("No change was made. This record may already be confirmed.")
    return redirect(url_for("transaction_detail", tx_id=tx_id))

@app.post("/history/clear")
def clear_history():
    check_csrf()
    db = get_db()
    db.execute("DELETE FROM items")
    db.execute("DELETE FROM transactions")
    db.commit()
    flash("Transaction history cleared, including its associated line items.")
    return redirect(url_for("index"))



@app.get("/money-owed")
def money_owed():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM money_owed ORDER BY id DESC LIMIT 200"
    ).fetchall()
    totals = db.execute("""
        SELECT
          COALESCE(SUM(CASE WHEN direction='BUSINESS_OWES' AND status='OPEN'
                            THEN amount ELSE 0 END), 0) AS business_owes,
          COALESCE(SUM(CASE WHEN direction='OWES_BUSINESS' AND status='OPEN'
                            THEN amount ELSE 0 END), 0) AS owed_to_business
        FROM money_owed
    """).fetchone()

    body = """
    <h1>Money Owed</h1>
    <p class="muted">Track balances only. This page does not hold or transfer money.</p>
    <div class="grid">
      <div class="card">
        <h3>Boitsholo owes</h3>
        <p>{{ totals.business_owes|money }}</p>
      </div>
      <div class="card">
        <h3>Owed to Boitsholo</h3>
        <p>{{ totals.owed_to_business|money }}</p>
      </div>
    </div>

    <div class="card">
      <h2>Record a balance</h2>
      <form method="post" action="{{ url_for('add_money_owed') }}">
        <input type="hidden" name="csrf" value="{{ token }}">
        <label>Direction</label>
        <select name="direction" required>
          <option value="BUSINESS_OWES">Boitsholo owes this person</option>
          <option value="OWES_BUSINESS">This person owes Boitsholo</option>
        </select>
        <label>Person or customer</label>
        <input name="person" maxlength="120" required>
        <label>Reason</label>
        <input name="reason" maxlength="250" required>
        <label>Amount (R)</label>
        <input name="amount" inputmode="decimal" placeholder="e.g. 250.00" required>
        <button type="submit">Save balance</button>
      </form>
    </div>

    <h2>Balance records</h2>
    <div class="card table-wrap">
    <table><thead><tr>
      <th>Date</th><th>Direction</th><th>Person</th><th>Reason</th>
      <th>Amount</th><th>Status</th><th>Action</th>
    </tr></thead><tbody>
    {% for item in rows %}
      <tr>
        <td>{{ item.created_at }}</td>
        <td>{{ 'Boitsholo owes' if item.direction == 'BUSINESS_OWES' else 'Owes Boitsholo' }}</td>
        <td>{{ item.person }}</td><td>{{ item.reason }}</td>
        <td>{{ item.amount|money }}</td>
        <td>{{ 'Outstanding' if item.status == 'OPEN' else 'Settled' }}</td>
        <td>
        {% if item.status == 'OPEN' %}
          <form method="post" action="{{ url_for('settle_money_owed', debt_id=item.id) }}">
            <input type="hidden" name="csrf" value="{{ token }}">
            <button type="submit">Mark settled</button>
          </form>
        {% else %}
          {{ item.settled_at }}
        {% endif %}
        </td>
      </tr>
    {% else %}
      <tr><td colspan="7">No money-owed records yet.</td></tr>
    {% endfor %}
    </tbody></table></div>
    """
    return render_template_string(
        PAGE, title="Money Owed", token=csrf_token(),
        body=render_template_string(
            body, rows=rows, totals=totals, token=csrf_token()
        )
    )


@app.post("/money-owed/new")
def add_money_owed():
    check_csrf()
    direction = request.form.get("direction", "")
    person = request.form.get("person", "").strip()
    reason = request.form.get("reason", "").strip()
    if direction not in ("BUSINESS_OWES", "OWES_BUSINESS"):
        abort(400, description="Choose a valid money-owed direction.")
    if not person or len(person) > 120 or not reason or len(reason) > 250:
        flash("Enter a person and a reason within the allowed length.")
        return redirect(url_for("money_owed"))
    try:
        amount = money_to_cents(request.form.get("amount", ""))
        if amount <= 0:
            raise ValueError("Amount must be greater than R0.00.")
    except ValueError as exc:
        flash(str(exc))
        return redirect(url_for("money_owed"))

    db = get_db()
    db.execute(
        """INSERT INTO money_owed
        (person, direction, reason, amount, status, created_at, recorded_by)
        VALUES (?, ?, ?, ?, 'OPEN', ?, ?)""",
        (person, direction, reason, amount,
         datetime.now().astimezone().isoformat(timespec="seconds"),
         session.get("staff_username", ""))
    )
    db.commit()
    flash("Money-owed record saved.")
    return redirect(url_for("money_owed"))


@app.post("/money-owed/<int:debt_id>/settle")
def settle_money_owed(debt_id):
    check_csrf()
    db = get_db()
    cur = db.execute(
        """UPDATE money_owed
           SET status='SETTLED', settled_at=?, settled_by=?
           WHERE id=? AND status='OPEN'""",
        (datetime.now().astimezone().isoformat(timespec="seconds"),
         session.get("staff_username", ""), debt_id)
    )
    db.commit()
    flash("Balance marked as settled." if cur.rowcount == 1
          else "No change made. This record may already be settled.")
    return redirect(url_for("money_owed"))



if __name__ == "__main__":
    # Local-only development server. Do not expose this MVP to the internet.
    app.run(host="127.0.0.1", port=8065, debug=False)
