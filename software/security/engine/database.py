from pathlib import Path
import sqlite3

DATABASE_PATH = (
    Path(__file__).resolve().parents[1]
    / "database"
    / "data"
    / "security.db"
)


def get_connection():
    """Create a connection to the MMK Security database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def database_exists():
    """Check whether the Security database exists."""
    return DATABASE_PATH.exists()


def get_tables():
    """Return the Security database table names."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

    return [row["name"] for row in rows]
