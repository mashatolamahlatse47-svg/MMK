import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "website" / "data" / "factory.db"

def migrate():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")

    con.executescript("""
CREATE TABLE IF NOT EXISTS approval_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    approval_id TEXT NOT NULL UNIQUE,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    decision TEXT NOT NULL DEFAULT 'PENDING',
    approved_by TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    action TEXT NOT NULL,
    from_status TEXT NOT NULL DEFAULT '',
    to_status TEXT NOT NULL DEFAULT '',
    actor TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS releases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    release_id TEXT NOT NULL UNIQUE,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    version TEXT NOT NULL,
    release_status TEXT NOT NULL DEFAULT 'DRAFT',
    package_path TEXT NOT NULL DEFAULT '',
    changelog TEXT NOT NULL DEFAULT '',
    approved_by TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id TEXT NOT NULL UNIQUE,
    customer_id INTEGER,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    feedback_type TEXT NOT NULL DEFAULT 'GENERAL',
    message TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'OPEN',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
""")

    con.commit()

    for table in (
        "approval_records",
        "audit_events",
        "releases",
        "feedback",
    ):
        count = con.execute(
            f'SELECT COUNT(*) FROM "{table}"'
        ).fetchone()[0]
        print(f"{table}: READY | rows={count}")

    con.close()

if __name__ == "__main__":
    migrate()
