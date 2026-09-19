import sys
from pathlib import Path

ENGINE_PATH = Path(__file__).resolve().parents[1] / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from sites import create_site
from occurrences import (
    create_occurrence,
    get_occurrence,
    list_occurrences,
    close_occurrence,
)


def test_occurrence_management():
    site_id = create_site(
        "MMK Security Test Site",
        "Development Address"
    )

    occurrence_id = create_occurrence(
        site_id=site_id,
        occurrence_date="2026-09-18",
        occurrence_time="19:00",
        category="Routine Patrol",
        description="Development test occurrence",
        action_taken="Routine check completed",
    )

    occurrence = get_occurrence(occurrence_id)

    assert occurrence is not None
    assert occurrence["site_id"] == site_id
    assert occurrence["category"] == "Routine Patrol"
    assert occurrence["status"] == "open"

    occurrences = list_occurrences(site_id)

    assert any(
        item["id"] == occurrence_id
        for item in occurrences
    )

    close_occurrence(occurrence_id)

    occurrence = get_occurrence(occurrence_id)

    assert occurrence["status"] == "closed"


if __name__ == "__main__":
    test_occurrence_management()

    print("MMK Security Occurrence Test: PASS")
    print("Create occurrence: PASS")
    print("Retrieve occurrence: PASS")
    print("List occurrences: PASS")
    print("Close occurrence: PASS")
