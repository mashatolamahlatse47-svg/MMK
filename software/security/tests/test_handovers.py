import sys
from pathlib import Path

ENGINE_PATH = Path(__file__).resolve().parents[1] / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from sites import create_site
from shifts import create_shift
from handovers import (
    create_handover,
    get_handover,
    list_handovers,
    complete_handover,
)


def test_handover_management():
    site_id = create_site(
        "MMK Handover Test Site",
        "Development Address"
    )

    shift_id = create_shift(
        site_id=site_id,
        shift_date="2026-09-18",
        start_time="18:00",
        end_time="06:00",
        notes="Development shift",
    )

    handover_id = create_handover(
        site_id=site_id,
        shift_id=shift_id,
        handover_date="2026-09-18",
        notes="Development handover test",
        outstanding_items="Test item",
    )

    handover = get_handover(handover_id)

    assert handover is not None
    assert handover["site_id"] == site_id
    assert handover["shift_id"] == shift_id
    assert handover["status"] == "pending"

    handovers = list_handovers(site_id)

    assert any(
        item["id"] == handover_id
        for item in handovers
    )

    complete_handover(handover_id)

    handover = get_handover(handover_id)

    assert handover["status"] == "completed"


if __name__ == "__main__":
    test_handover_management()

    print("MMK Security Handover Test: PASS")
    print("Create handover: PASS")
    print("Retrieve handover: PASS")
    print("List handovers: PASS")
    print("Complete handover: PASS")
