import sqlite3
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = FACTORY_ROOT / "website" / "data" / "factory.db"


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database():
    connection = get_connection()

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT '',
            target_customer TEXT NOT NULL DEFAULT '',
            expected_value REAL,
            required_skills TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'IDEA',
            owner TEXT NOT NULL DEFAULT 'MMK',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            notes TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            skills TEXT NOT NULL DEFAULT '',
            training_status TEXT NOT NULL DEFAULT 'NOT_STARTED',
            portfolio TEXT NOT NULL DEFAULT '',
            participation_status TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            version TEXT NOT NULL DEFAULT '0.1.0',
            description TEXT NOT NULL DEFAULT '',
            opportunity_id INTEGER,
            owner TEXT NOT NULL DEFAULT 'MMK',
            manufacturing_status TEXT NOT NULL DEFAULT 'PLANNED',
            quality_status TEXT NOT NULL DEFAULT 'PENDING',
            pricing TEXT NOT NULL DEFAULT '',
            ip_status TEXT NOT NULL DEFAULT 'REVIEW',
            release_status TEXT NOT NULL DEFAULT 'INTERNAL',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
        );

        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            opportunity_id INTEGER,
            required_skills TEXT NOT NULL DEFAULT '',
            delivery_workflow TEXT NOT NULL DEFAULT '',
            pricing_model TEXT NOT NULL DEFAULT '',
            responsible_member_id INTEGER,
            service_status TEXT NOT NULL DEFAULT 'PLANNED',
            quality_requirements TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id),
            FOREIGN KEY (responsible_member_id) REFERENCES members(id)
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            owner TEXT NOT NULL DEFAULT 'MMK',
            project_type TEXT NOT NULL DEFAULT 'OTHER',
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'IDEA',
            current_version TEXT NOT NULL DEFAULT '0.1.0',
            opportunity_id INTEGER,
            product_id INTEGER,
            service_id INTEGER,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            notes TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        );

        CREATE TABLE IF NOT EXISTS manufacturing_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturing_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            opportunity_id INTEGER,
            product_id INTEGER,
            service_id INTEGER,
            assigned_member_id INTEGER,
            stage TEXT NOT NULL DEFAULT 'INTAKE',
            status TEXT NOT NULL DEFAULT 'OPEN',
            expected_outcome TEXT NOT NULL DEFAULT '',
            quality_requirements TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (service_id) REFERENCES services(id),
            FOREIGN KEY (assigned_member_id) REFERENCES members(id)
        );

        CREATE TABLE IF NOT EXISTS quality_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quality_id TEXT NOT NULL UNIQUE,
            manufacturing_id INTEGER NOT NULL,
            functionality TEXT NOT NULL DEFAULT 'PENDING',
            usability TEXT NOT NULL DEFAULT 'PENDING',
            correctness TEXT NOT NULL DEFAULT 'PENDING',
            documentation TEXT NOT NULL DEFAULT 'PENDING',
            security TEXT NOT NULL DEFAULT 'PENDING',
            ip_review TEXT NOT NULL DEFAULT 'PENDING',
            customer_readiness TEXT NOT NULL DEFAULT 'PENDING',
            result TEXT NOT NULL DEFAULT 'PENDING',
            reviewer TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manufacturing_id) REFERENCES manufacturing_jobs(id)
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            customer_type TEXT NOT NULL DEFAULT '',
            contact TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS training_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            training_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            source_manufacturing_id INTEGER,
            asset_type TEXT NOT NULL DEFAULT 'GUIDE',
            status TEXT NOT NULL DEFAULT 'DRAFT',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_manufacturing_id) REFERENCES manufacturing_jobs(id)
        );

        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL UNIQUE,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            from_status TEXT,
            to_status TEXT,
            actor TEXT NOT NULL DEFAULT '',
            reason TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

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
        """
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    init_database()
    print("[MMK DIGITAL FACTORY DATABASE READY]")
    print(f"Database: {DATABASE_PATH}")
