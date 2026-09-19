import sys
from pathlib import Path

ENGINE_PATH = Path(__file__).resolve().parents[1] / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from sites import create_site
from shifts import (
    create_shift,
    get_shift,
    list_shifts,
    close_shift,
)


def test_shift_management():
    site_id = create_site(
        "MMK Shift Test Site",
        "Development Address"
    )

    shift_id = create_shift(
        site_id=site_id,
        shift_date="2026-09-18",
        start_time="18:00",
        end_time="06:00",
        notes="Development shift test",
    )

    shift = get_shift(shift_id)

    assert shift is not None
    assert shift["site_id"] == site_id
    assert shift["start_time"] == "18:00"
    assert shift["status"] == "active"

    shifts = list_shifts(site_id)

    assert any(
        item["id"] == shift_id
        for item in shifts
    )

    close_shift(shift_id)

    shift = get_shift(shift_id)

    assert shift["status"] == "closed"


if __name__ == "__main__":
    test_shift_management()

    print("MMK Security Shift Test: PASS")
    print("Create shift: PASS")
    print("Retrieve shift: PASS")
    print("List shifts: PASS")
    print("Close shift: PASS")
