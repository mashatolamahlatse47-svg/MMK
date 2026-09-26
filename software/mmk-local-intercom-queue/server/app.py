from flask import Flask, jsonify
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "mmk_intercom.db"

app = Flask(__name__)


def get_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS system_info (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            product TEXT NOT NULL,
            version TEXT NOT NULL
        )
    """)
    conn.execute("""
        INSERT OR REPLACE INTO system_info (id, product, version)
        VALUES (1, ?, ?)
    """, ("MMK Local Intercom & Queue System", "0.1.0"))
    conn.commit()
    conn.close()


@app.get("/api/health")
def health():
    return jsonify({
        "ok": True,
        "product": "MMK Local Intercom & Queue System",
        "version": "0.1.0"
    })


@app.post("/api/check-in")
def check_in():
    from flask import request

    data = request.get_json(silent=True) or {}
    full_name = str(data.get("full_name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    department = str(data.get("department", "General")).strip() or "General"

    if not full_name:
        return jsonify({
            "ok": False,
            "error": "full_name is required"
        }), 400

    conn = get_db()

    patient = conn.execute(
        "INSERT INTO patients (full_name, phone) VALUES (?, ?)",
        (full_name, phone)
    )

    patient_id = patient.lastrowid

    next_number = conn.execute("""
        SELECT COALESCE(MAX(queue_number), 0) + 1
        FROM queue_entries
    """).fetchone()[0]

    conn.execute("""
        INSERT INTO queue_entries
        (queue_number, patient_id, department, status)
        VALUES (?, ?, ?, 'WAITING')
    """, (next_number, patient_id, department))

    conn.commit()
    conn.close()

    return jsonify({
        "ok": True,
        "patient_id": patient_id,
        "queue_number": next_number,
        "department": department,
        "status": "WAITING"
    }), 201


@app.get("/api/queue")
def queue():
    conn = get_db()

    rows = conn.execute("""
        SELECT
            q.queue_number,
            p.full_name,
            p.phone,
            q.department,
            q.priority,
            q.status,
            q.checked_in_at
        FROM queue_entries q
        JOIN patients p ON p.id = q.patient_id
        ORDER BY q.priority DESC, q.id ASC
    """).fetchall()

    conn.close()

    return jsonify([
        {
            "queue_number": row["queue_number"],
            "full_name": row["full_name"],
            "phone": row["phone"],
            "department": row["department"],
            "priority": row["priority"],
            "status": row["status"],
            "checked_in_at": row["checked_in_at"]
        }
        for row in rows
    ])


@app.get("/api/info")
def info():
    conn = get_db()
    row = conn.execute(
        "SELECT product, version FROM system_info WHERE id = 1"
    ).fetchone()
    conn.close()

    return jsonify({
        "product": row["product"],
        "version": row["version"],
        "database": "SQLite",
        "mode": "local-server"
    })


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5056, debug=False)
