import sys
from pathlib import Path

ENGINE_PATH = Path(__file__).resolve().parents[1] / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from database import database_exists, get_tables


EXPECTED_TABLES = {
    "security_sites",
    "security_shifts",
    "security_occurrences",
    "security_incidents",
    "security_handovers",
}


def test_database_exists():
    assert database_exists(), "Security database does not exist"


def test_required_tables():
    tables = set(get_tables())

    missing = EXPECTED_TABLES - tables

    assert not missing, f"Missing tables: {sorted(missing)}"


if __name__ == "__main__":
    test_database_exists()
    test_required_tables()

    print("MMK Security Database Test: PASS")
    print("Database: PASS")
    print("Required tables: PASS")
