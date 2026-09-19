import sys
from pathlib import Path

ENGINE_PATH = Path(__file__).resolve().parents[1] / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from sites import create_site
from occurrences import create_occurrence
from incidents import (
    create_incident,
    get_incident,
    list_incidents,
    resolve_incident,
)


def test_incident_management():
    site_id = create_site(
        "MMK Incident Test Site",
        "Development Address"
    )

    occurrence_id = create_occurrence(
        site_id=site_id,
        occurrence_date="2026-09-18",
        occurrence_time="20:00",
        category="Security Incident Test",
        description="Development incident occurrence",
        action_taken="Supervisor notified",
    )

    incident_id = create_incident(
        occurrence_id=occurrence_id,
        severity="high",
        description="Development test incident",
        response="Supervisor response recorded",
    )

    incident = get_incident(incident_id)

    assert incident is not None
    assert incident["occurrence_id"] == occurrence_id
    assert incident["severity"] == "high"
    assert incident["status"] == "open"

    incidents = list_incidents(occurrence_id)

    assert any(
        item["id"] == incident_id
        for item in incidents
    )

    resolve_incident(
        incident_id,
        "Development incident resolved",
    )

    incident = get_incident(incident_id)

    assert incident["status"] == "resolved"
    assert incident["resolution"] == "Development incident resolved"


if __name__ == "__main__":
    test_incident_management()

    print("MMK Security Incident Test: PASS")
    print("Create incident: PASS")
    print("Retrieve incident: PASS")
    print("List incidents: PASS")
    print("Resolve incident: PASS")
