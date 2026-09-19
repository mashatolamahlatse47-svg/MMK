import sys
from pathlib import Path

ENGINE_PATH = Path(__file__).resolve().parents[1] / "engine"

if str(ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(ENGINE_PATH))

from sites import create_site, get_site, list_sites
from occurrences import (
    create_occurrence,
    get_occurrence,
    list_occurrences,
    close_occurrence,
)
from incidents import (
    create_incident,
    get_incident,
    list_incidents,
    resolve_incident,
)
from shifts import (
    create_shift,
    get_shift,
    list_shifts,
    close_shift,
)
from handovers import (
    create_handover,
    get_handover,
    list_handovers,
    complete_handover,
)
from reports import (
    daily_occurrence_report,
    incident_report,
    shift_report,
    handover_report,
    monthly_summary,
)


class SecurityService:
    """Unified application service for the MMK Security System."""

    # Sites
    def create_site(self, name, address=None, business_id=None):
        return create_site(name, address, business_id)

    def get_site(self, site_id):
        return get_site(site_id)

    def list_sites(self):
        return list_sites()

    # Occurrences
    def create_occurrence(self, **kwargs):
        return create_occurrence(**kwargs)

    def get_occurrence(self, occurrence_id):
        return get_occurrence(occurrence_id)

    def list_occurrences(self, site_id=None):
        return list_occurrences(site_id)

    def close_occurrence(self, occurrence_id):
        return close_occurrence(occurrence_id)

    # Incidents
    def create_incident(self, **kwargs):
        return create_incident(**kwargs)

    def get_incident(self, incident_id):
        return get_incident(incident_id)

    def list_incidents(self, occurrence_id=None):
        return list_incidents(occurrence_id)

    def resolve_incident(self, incident_id, resolution):
        return resolve_incident(incident_id, resolution)

    # Shifts
    def create_shift(self, **kwargs):
        return create_shift(**kwargs)

    def get_shift(self, shift_id):
        return get_shift(shift_id)

    def list_shifts(self, site_id=None):
        return list_shifts(site_id)

    def close_shift(self, shift_id):
        return close_shift(shift_id)

    # Handovers
    def create_handover(self, **kwargs):
        return create_handover(**kwargs)

    def get_handover(self, handover_id):
        return get_handover(handover_id)

    def list_handovers(self, site_id=None):
        return list_handovers(site_id)

    def complete_handover(self, handover_id):
        return complete_handover(handover_id)

    # Reports
    def daily_occurrence_report(self, site_id, occurrence_date):
        return daily_occurrence_report(site_id, occurrence_date)

    def incident_report(self, site_id=None):
        return incident_report(site_id)

    def shift_report(self, site_id, shift_date):
        return shift_report(site_id, shift_date)

    def handover_report(self, site_id, handover_date):
        return handover_report(site_id, handover_date)

    def monthly_summary(self, site_id, year, month):
        return monthly_summary(site_id, year, month)
