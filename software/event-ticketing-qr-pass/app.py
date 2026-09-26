import csv
import hashlib
import hmac
import io
import os
import secrets
import sqlite3
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode

import qrcode
from flask import Flask, jsonify, make_response, redirect, render_template, request, send_file
from reportlab.lib.pagesizes import A6
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "mmk_event_ticketing.db"
SECRET_PATH = DATA_DIR / ".ticket-secret"

app = Flask(__name__, static_folder="website", static_url_path="/assets")


def get_secret() -> bytes:
    env = os.getenv("MMK_TICKET_SECRET")
    if env:
        return env.encode("utf-8")
    if SECRET_PATH.exists():
        return SECRET_PATH.read_text(encoding="utf-8").strip().encode("utf-8")
    secret = secrets.token_urlsafe(48)
    SECRET_PATH.write_text(secret, encoding="utf-8")
    try:
        SECRET_PATH.chmod(0o600)
    except OSError:
        pass
    return secret.encode("utf-8")


SECRET = get_secret()


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                event_date TEXT NOT NULL,
                event_time TEXT NOT NULL,
                venue TEXT NOT NULL,
                price_cents INTEGER NOT NULL DEFAULT 0,
                capacity INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                attendee_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                price_cents INTEGER NOT NULL DEFAULT 0,
                code TEXT NOT NULL UNIQUE,
                code_hash TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'issued',
                issued_at TEXT NOT NULL,
                checked_in_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_tickets_event ON tickets(event_id);
            CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
            """
        )


def admin_ok():
    expected = os.getenv("MMK_ADMIN_KEY", "")
    presented = request.headers.get("X-MMK-Admin-Key", "")
    return bool(expected) and hmac.compare_digest(presented, expected)


def require_admin():
    if not admin_ok():
        return jsonify({"error": "Admin key required"}), 401
    return None


def normalize_phone(phone: str) -> str:
    raw = "".join(ch for ch in (phone or "") if ch.isdigit() or ch == "+")
    if raw.startswith("00"):
        raw = "+" + raw[2:]
    if raw.startswith("0") and not raw.startswith("00"):
        raw = "+27" + raw[1:]
    return raw.replace("+", "+", 1)


def money_to_cents(value):
    text = str(value or "0").replace(",", "").strip()
    return int(round(float(text) * 100))


def money(cents):
    return f"R{cents / 100:.2f}"


def token_hash(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def signature(code: str, event_id: int) -> str:
    raw = f"MMK1|{event_id}|{code}".encode("utf-8")
    return hmac.new(SECRET, raw, hashlib.sha256).hexdigest()[:24]


def verify_signature(code: str, event_id: int, sig: str) -> bool:
    return hmac.compare_digest(signature(code, event_id), sig or "")


def public_base():
    configured = os.getenv("MMK_PUBLIC_BASE_URL", "").strip().rstrip("/")
    return configured or request.url_root.rstrip("/")


def ticket_url(code: str, event_id: int):
    sig = signature(code, event_id)
    return f"{public_base()}/checkin/{quote(code)}?{urlencode({'sig': sig})}"


def issue_one(event, attendee_name, phone, price_cents=None):
    attendee_name = (attendee_name or "").strip()
    if not attendee_name:
        raise ValueError("attendee_name is required")
    phone = normalize_phone(phone)
    if len(phone) < 8:
        raise ValueError("phone must contain a valid number")
    with db() as conn:
        if event["capacity"] > 0:
            count = conn.execute("SELECT COUNT(*) FROM tickets WHERE event_id=?", (event["id"],)).fetchone()[0]
            if count >= event["capacity"]:
                raise ValueError("Event capacity reached")
        price = event["price_cents"] if price_cents is None else int(price_cents)
        for _ in range(8):
            code = secrets.token_urlsafe(10).replace("-", "").replace("_", "").upper()[:13]
            try:
                conn.execute(
                    "INSERT INTO tickets(event_id,attendee_name,phone,price_cents,code,code_hash,status,issued_at) VALUES(?,?,?,?,?,?,?,?)",
                    (event["id"], attendee_name, phone, price, code, token_hash(code), "issued", now_iso()),
                )
                ticket_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                return {"id": ticket_id, "code": code, "attendee_name": attendee_name, "phone": phone, "price_cents": price}
            except sqlite3.IntegrityError:
                continue
    raise RuntimeError("Could not create a unique ticket code")


def find_ticket(code):
    with db() as conn:
        return conn.execute(
            """
            SELECT t.*, e.name AS event_name, e.event_date, e.event_time, e.venue
            FROM tickets t JOIN events e ON e.id=t.event_id
            WHERE t.code_hash=?
            """,
            (token_hash(code),),
        ).fetchone()


def build_ticket_pdf(ticket):
    code = ticket["raw_code"]
    qr_url = ticket_url(code, ticket["event_id"])
    qr = qrcode.make(qr_url)
    qr_mem = io.BytesIO()
    qr.save(qr_mem, format="PNG")
    qr_mem.seek(0)

    pdf = io.BytesIO()
    c = canvas.Canvas(pdf, pagesize=A6)
    width, height = A6
    c.setTitle(f"MMK Ticket {code}")
    c.setFont("Helvetica-Bold", 17)
    c.drawString(24, height - 32, ticket["event_name"][:34])
    c.setFont("Helvetica", 8.5)
    c.drawString(24, height - 46, f"{ticket['event_date']}  •  {ticket['event_time']}")
    c.drawString(24, height - 58, ticket["venue"][:48])

    c.setLineWidth(0.7)
    c.line(24, height - 68, width - 24, height - 68)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(24, height - 88, "ADMIT ONE")
    c.setFont("Helvetica", 10)
    c.drawString(24, height - 103, ticket["attendee_name"][:42])
    c.drawString(24, height - 118, f"Ticket: {code}")
    c.drawString(24, height - 133, f"Price: {money(ticket['price_cents'])}")

    c.drawImage(ImageReader(qr_mem), width - 124, 42, 92, 92, preserveAspectRatio=True, mask="auto")
    c.setFont("Helvetica", 7.5)
    c.drawString(24, 52, "Scan QR at the entrance")
    c.drawString(24, 41, "Powered by MMK Event Ticketing")
    c.showPage()
    c.save()
    pdf.seek(0)
    return pdf


@app.get("/")
def index():
    return send_file(BASE_DIR / "website" / "index.html")


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "product": "MMK Event Ticketing & QR Pass Generator", "version": "1.0.0"})


@app.get("/api/events")
def list_events():
    with db() as conn:
        rows = conn.execute(
            """
            SELECT e.*, COUNT(t.id) AS ticket_count,
              SUM(CASE WHEN t.status='checked_in' THEN 1 ELSE 0 END) AS checked_in
            FROM events e LEFT JOIN tickets t ON t.event_id=e.id
            GROUP BY e.id ORDER BY e.id DESC
            """
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/events")
def create_event():
    denied = require_admin()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    required = ["name", "event_date", "event_time", "venue"]
    if any(not str(data.get(k, "")).strip() for k in required):
        return jsonify({"error": "name, event_date, event_time and venue are required"}), 400
    capacity = int(data.get("capacity") or 0)
    price = money_to_cents(data.get("price"))
    if capacity < 0 or price < 0:
        return jsonify({"error": "capacity and price cannot be negative"}), 400
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO events(name,event_date,event_time,venue,price_cents,capacity,created_at) VALUES(?,?,?,?,?,?,?)",
            (str(data["name"]).strip(), str(data["event_date"]), str(data["event_time"]), str(data["venue"]).strip(), price, capacity, now_iso()),
        )
        event_id = cur.lastrowid
        row = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    return jsonify(dict(row)), 201


@app.post("/api/tickets")
def create_ticket():
    denied = require_admin()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    try:
        event_id = int(data.get("event_id"))
    except Exception:
        return jsonify({"error": "event_id is required"}), 400
    with db() as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        return jsonify({"error": "Event not found"}), 404
    try:
        item = issue_one(event, data.get("attendee_name"), data.get("phone"), money_to_cents(data["price"]) if "price" in data else None)
    except (ValueError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400
    item["event_id"] = event_id
    item["event_name"] = event["name"]
    item["ticket_url"] = ticket_url(item["code"], event_id)
    item["pdf_url"] = f"{public_base()}/tickets/{quote(item['code'])}.pdf?{urlencode({'sig': signature(item['code'], event_id)})}"
    item["whatsapp_url"] = whatsapp_url(item)
    return jsonify(item), 201


@app.post("/api/tickets/bulk")
def bulk_tickets():
    denied = require_admin()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    event_id = int(data.get("event_id"))
    csv_text = data.get("csv", "")
    with db() as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        return jsonify({"error": "Event not found"}), 404
    reader = csv.DictReader(io.StringIO(csv_text))
    created = []
    errors = []
    for line_no, row in enumerate(reader, start=2):
        try:
            price = money_to_cents(row["price"]) if row.get("price") else None
            item = issue_one(event, row.get("attendee_name"), row.get("phone"), price)
            item["event_id"] = event_id
            item["event_name"] = event["name"]
            item["ticket_url"] = ticket_url(item["code"], event_id)
            item["pdf_url"] = f"{public_base()}/tickets/{quote(item['code'])}.pdf?{urlencode({'sig': signature(item['code'], event_id)})}"
            created.append(item)
        except Exception as exc:
            errors.append({"line": line_no, "error": str(exc)})
    return jsonify({"created": created, "errors": errors})


@app.get("/api/tickets/<code>")
def ticket_info(code):
    sig = request.args.get("sig", "")
    ticket = find_ticket(code)
    if not ticket or not verify_signature(code, ticket["event_id"], sig):
        return jsonify({"valid": False, "status": "invalid"}), 404
    out = dict(ticket)
    out.pop("code_hash", None)
    out["code"] = code
    out["valid"] = ticket["status"] != "cancelled"
    return jsonify(out)


def whatsapp_url(item):
    url = item.get("ticket_url") or ticket_url(item["code"], item["event_id"])
    message = f"MMK Ticket — {item.get('event_name','Event')}\nName: {item.get('attendee_name','')}\nTicket: {item['code']}\nPass: {url}"
    phone = normalize_phone(item.get("phone", ""))
    digits = phone.replace("+", "")
    return f"https://wa.me/{digits}?text={quote(message)}"


@app.get("/api/tickets/<code>/whatsapp")
def whatsapp_ticket(code):
    denied = require_admin()
    if denied:
        return denied
    ticket = find_ticket(code)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify({"whatsapp_url": whatsapp_url({"code": code, "event_id": ticket["event_id"], "event_name": ticket["event_name"], "attendee_name": ticket["attendee_name"], "phone": ticket["phone"]})})


@app.get("/tickets/<code>.pdf")
def ticket_pdf(code):
    ticket = find_ticket(code)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    sig = request.args.get("sig", "")
    if not verify_signature(code, ticket["event_id"], sig):
        return jsonify({"error": "Invalid ticket signature"}), 403
    mutable = dict(ticket)
    mutable["raw_code"] = code
    pdf = build_ticket_pdf(mutable)
    return send_file(pdf, mimetype="application/pdf", as_attachment=True, download_name=f"MMK-Ticket-{code}.pdf")


@app.get("/checkin/<code>")
def checkin(code):
    sig = request.args.get("sig", "")
    ticket = find_ticket(code)
    valid_signature = bool(ticket and verify_signature(code, ticket["event_id"], sig))
    return render_template("checkin.html", ticket=ticket, code=code, valid_signature=valid_signature)


@app.post("/api/checkin/<code>")
def do_checkin(code):
    denied = require_admin()
    if denied:
        return denied
    sig = request.args.get("sig", "")
    ticket = find_ticket(code)
    if not ticket or not verify_signature(code, ticket["event_id"], sig):
        return jsonify({"valid": False, "status": "invalid"}), 404
    if ticket["status"] == "cancelled":
        return jsonify({"valid": False, "status": "cancelled"}), 409
    if ticket["status"] == "checked_in":
        return jsonify({"valid": True, "status": "already_checked_in", "checked_in_at": ticket["checked_in_at"]}), 409
    with db() as conn:
        conn.execute("UPDATE tickets SET status='checked_in', checked_in_at=? WHERE id=?", (now_iso(), ticket["id"]))
    return jsonify({"valid": True, "status": "checked_in", "attendee_name": ticket["attendee_name"], "event_name": ticket["event_name"]})


@app.get("/api/events/<int:event_id>/stats")
def event_stats(event_id):
    denied = require_admin()
    if denied:
        return denied
    with db() as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not event:
            return jsonify({"error": "Event not found"}), 404
        counts = conn.execute(
            "SELECT COUNT(*) total, SUM(status='checked_in') checked_in, SUM(status='issued') issued, SUM(status='cancelled') cancelled, COALESCE(SUM(price_cents),0) revenue_cents FROM tickets WHERE event_id=?",
            (event_id,),
        ).fetchone()
    return jsonify({"event": dict(event), "counts": dict(counts)})


@app.get("/api/events/<int:event_id>/export.zip")
def export_event(event_id):
    denied = require_admin()
    if denied:
        return denied
    with db() as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        tickets = conn.execute("SELECT * FROM tickets WHERE event_id=? ORDER BY id", (event_id,)).fetchall()
    if not event:
        return jsonify({"error": "Event not found"}), 404
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for ticket in tickets:
            mutable = dict(ticket)
            pdf = build_ticket_pdf(mutable)
            z.writestr(f"tickets/MMK-Ticket-{ticket['code']}.pdf", pdf.getvalue())
        ledger = io.StringIO()
        writer = csv.writer(ledger)
        writer.writerow(["id", "attendee_name", "phone", "price", "status", "issued_at", "checked_in_at"])
        for ticket in tickets:
            writer.writerow([ticket["id"], ticket["attendee_name"], ticket["phone"], money(ticket["price_cents"]), ticket["status"], ticket["issued_at"], ticket["checked_in_at"] or ""])
        z.writestr("attendance-ledger.csv", ledger.getvalue())
    out.seek(0)
    return send_file(out, mimetype="application/zip", as_attachment=True, download_name=f"MMK-{event['name'].replace(' ','-')}-export.zip")


init_db()

if __name__ == "__main__":
    host = os.getenv("MMK_HOST", "127.0.0.1")
    port = int(os.getenv("MMK_PORT", "5055"))
    app.run(host=host, port=port, debug=False)
