import sqlite3
from datetime import datetime

OPPORTUNITY_TRANSITIONS = {
    "IDEA": {"ASSESSMENT"},
    "ASSESSMENT": {"APPROVED", "REJECTED", "ON_HOLD"},
    "ON_HOLD": {"ASSESSMENT"},
}

MANUFACTURING_TRANSITIONS = {
    "INTAKE": {"PLAN"},
    "PLAN": {"BUILD"},
    "BUILD": {"CHECK"},
    "CHECK": {"TEST", "FIX"},
    "TEST": {"FIX", "QUALITY REVIEW"},
    "FIX": {"CHECK"},
    "QUALITY REVIEW": {"PACKAGE", "FIX"},
    "PACKAGE": {"RELEASE"},
    "RELEASE": {"PRESERVE"},
}

APPROVAL_DECISIONS = {
    "PENDING",
    "APPROVED",
    "REJECTED",
}


def transition(
    con,
    entity_type,
    entity_id,
    from_status,
    to_status,
    actor="",
    reason="",
):
    """
    Validate and record a controlled workflow transition.
    The caller supplies the current status explicitly so the
    transition can be checked against the Factory state machine.
    """

    transitions = {
        "OPPORTUNITY": OPPORTUNITY_TRANSITIONS,
        "MANUFACTURING": MANUFACTURING_TRANSITIONS,
    }

    if entity_type not in transitions:
        raise ValueError(f"Unsupported workflow entity: {entity_type}")

    allowed = transitions[entity_type].get(from_status, set())

    if to_status not in allowed:
        raise ValueError(
            f"Invalid transition for {entity_type}: "
            f"{from_status} -> {to_status}"
        )

    event_id = f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    con.execute(
        """
        INSERT INTO audit_events (
            event_id,
            entity_type,
            entity_id,
            action,
            from_status,
            to_status,
            actor,
            reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            entity_type,
            entity_id,
            "STATUS_TRANSITION",
            from_status,
            to_status,
            actor,
            reason,
        ),
    )

    return event_id


def record_approval(
    con,
    approval_id,
    entity_type,
    entity_id,
    decision="PENDING",
    approved_by="",
    reason="",
):
    """Record a Founder/control approval decision."""

    if decision not in APPROVAL_DECISIONS:
        raise ValueError(f"Invalid approval decision: {decision}")

    con.execute(
        """
        INSERT INTO approval_records (
            approval_id,
            entity_type,
            entity_id,
            decision,
            approved_by,
            reason
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            approval_id,
            entity_type,
            entity_id,
            decision,
            approved_by,
            reason,
        ),
    )


def audit_event(
    con,
    event_id,
    entity_type,
    entity_id,
    action,
    actor="",
    reason="",
):
    """Record a general Factory audit event."""

    con.execute(
        """
        INSERT INTO audit_events (
            event_id,
            entity_type,
            entity_id,
            action,
            actor,
            reason
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            entity_type,
            entity_id,
            action,
            actor,
            reason,
        ),
    )
