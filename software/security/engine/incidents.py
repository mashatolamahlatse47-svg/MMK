from database import get_connection


VALID_SEVERITIES = {
    "low",
    "medium",
    "high",
    "critical",
}


def create_incident(
    occurrence_id,
    severity,
    description,
    response=None,
    supervisor_id=None,
):
    if not occurrence_id:
        raise ValueError("Occurrence ID is required")

    if severity not in VALID_SEVERITIES:
        raise ValueError(
            f"Invalid severity. Use: {sorted(VALID_SEVERITIES)}"
        )

    if not description or not description.strip():
        raise ValueError("Incident description is required")

    with get_connection() as connection:
        occurrence = connection.execute(
            """
            SELECT id
            FROM security_occurrences
            WHERE id = ?
            """,
            (occurrence_id,),
        ).fetchone()

        if occurrence is None:
            raise ValueError("Occurrence does not exist")

        cursor = connection.execute(
            """
            INSERT INTO security_incidents
            (
                occurrence_id,
                severity,
                description,
                response,
                supervisor_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                occurrence_id,
                severity,
                description.strip(),
                response,
                supervisor_id,
            ),
        )

        connection.commit()

        return cursor.lastrowid


def get_incident(incident_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM security_incidents
            WHERE id = ?
            """,
            (incident_id,),
        ).fetchone()

    return dict(row) if row else None


def list_incidents(occurrence_id=None):
    with get_connection() as connection:
        if occurrence_id is None:
            rows = connection.execute(
                """
                SELECT *
                FROM security_incidents
                ORDER BY id DESC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM security_incidents
                WHERE occurrence_id = ?
                ORDER BY id DESC
                """,
                (occurrence_id,),
            ).fetchall()

    return [dict(row) for row in rows]


def resolve_incident(incident_id, resolution):
    if not resolution or not resolution.strip():
        raise ValueError("Resolution is required")

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE security_incidents
            SET resolution = ?,
                status = 'resolved',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (resolution.strip(), incident_id),
        )
        connection.commit()
