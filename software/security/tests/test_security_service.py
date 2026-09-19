import sys
from pathlib import Path

SERVICE_PATH = Path(__file__).resolve().parents[1] / "services"
sys.path.insert(0, str(SERVICE_PATH))

from security_service import SecurityService


def test_security_service():
    service = SecurityService()

    site_id = service.create_site(
        "MMK Service Test Site",
        "Development Address",
    )

    site = service.get_site(site_id)

    assert site is not None
    assert site["name"] == "MMK Service Test Site"

    occurrence_id = service.create_occurrence(
        site_id=site_id,
        occurrence_date="2026-09-18",
        occurrence_time="22:00",
        category="Service Test",
        description="Development service occurrence",
        action_taken="Service test action",
    )

    occurrence = service.get_occurrence(occurrence_id)

    assert occurrence["site_id"] == site_id

    incident_id = service.create_incident(
        occurrence_id=occurrence_id,
        severity="low",
        description="Development service incident",
    )

    incident = service.get_incident(incident_id)

    assert incident["occurrence_id"] == occurrence_id

    shift_id = service.create_shift(
        site_id=site_id,
        shift_date="2026-09-18",
        start_time="18:00",
        end_time="06:00",
    )

    shift = service.get_shift(shift_id)

    assert shift["site_id"] == site_id

    handover_id = service.create_handover(
        site_id=site_id,
        shift_id=shift_id,
        handover_date="2026-09-18",
        notes="Development service handover",
        outstanding_items="None",
    )

    handover = service.get_handover(handover_id)

    assert handover["shift_id"] == shift_id

    summary = service.monthly_summary(
        site_id,
        2026,
        9,
    )

    assert summary["occurrences"] >= 1
    assert summary["incidents"] >= 1
    assert summary["shifts"] >= 1
    assert summary["handovers"] >= 1


if __name__ == "__main__":
    test_security_service()

    print("MMK Security Service Test: PASS")
    print("Site service: PASS")
    print("Occurrence service: PASS")
    print("Incident service: PASS")
    print("Shift service: PASS")
    print("Handover service: PASS")
    print("Reporting service: PASS")
