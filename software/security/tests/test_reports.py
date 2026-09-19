import sys
from pathlib import Path

ENGINE_PATH = Path(__file__).resolve().parents[1] / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from sites import create_site
from occurrences import create_occurrence
from incidents import create_incident
from shifts import create_shift
from handovers import create_handover
from reports import (
    daily_occurrence_report,
    incident_report,
    shift_report,
    handover_report,
    monthly_summary,
)


def test_reports():
    site_id = create_site(
        "MMK Reports Test Site",
        "Development Address"
    )

    occurrence_id = create_occurrence(
        site_id=site_id,
        occurrence_date="2026-09-18",
        occurrence_time="21:00",
        category="Report Test",
        description="Development report occurrence",
        action_taken="Test action",
    )

    create_incident(
        occurrence_id=occurrence_id,
        severity="medium",
        description="Development report incident",
    )

    create_shift(
        site_id=site_id,
        shift_date="2026-09-18",
        start_time="18:00",
        end_time="06:00",
    )

    create_handover(
        site_id=site_id,
        shift_id=None,
        handover_date="2026-09-18",
        notes="Development report handover",
    )

    occurrences = daily_occurrence_report(
        site_id,
        "2026-09-18",
    )

    assert len(occurrences) >= 1

    incidents = incident_report(site_id)
    assert len(incidents) >= 1

    shifts = shift_report(
        site_id,
        "2026-09-18",
    )
    assert len(shifts) >= 1

    handovers = handover_report(
        site_id,
        "2026-09-18",
    )
    assert len(handovers) >= 1

    summary = monthly_summary(
        site_id,
        2026,
        9,
    )

    assert summary["occurrences"] >= 1
    assert summary["incidents"] >= 1
    assert summary["shifts"] >= 1
    assert summary["handovers"] >= 1


if __name__ == "__main__":
    test_reports()

    print("MMK Security Reports Test: PASS")
    print("Daily occurrence report: PASS")
    print("Incident report: PASS")
    print("Shift report: PASS")
    print("Handover report: PASS")
    print("Monthly summary: PASS")
