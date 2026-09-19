from database import get_connection


def daily_occurrence_report(site_id, occurrence_date):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM security_occurrences
            WHERE site_id = ?
              AND occurrence_date = ?
            ORDER BY occurrence_time ASC, id ASC
            """,
            (site_id, occurrence_date),
        ).fetchall()

    return [dict(row) for row in rows]


def incident_report(site_id=None):
    with get_connection() as connection:
        if site_id is None:
            rows = connection.execute(
                """
                SELECT
                    i.*,
                    o.site_id,
                    o.occurrence_date,
                    o.occurrence_time,
                    o.category
                FROM security_incidents i
                JOIN security_occurrences o
                    ON i.occurrence_id = o.id
                ORDER BY i.id DESC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                    i.*,
                    o.site_id,
                    o.occurrence_date,
                    o.occurrence_time,
                    o.category
                FROM security_incidents i
                JOIN security_occurrences o
                    ON i.occurrence_id = o.id
                WHERE o.site_id = ?
                ORDER BY i.id DESC
                """,
                (site_id,),
            ).fetchall()

    return [dict(row) for row in rows]


def shift_report(site_id, shift_date):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM security_shifts
            WHERE site_id = ?
              AND shift_date = ?
            ORDER BY start_time ASC, id ASC
            """,
            (site_id, shift_date),
        ).fetchall()

    return [dict(row) for row in rows]


def handover_report(site_id, handover_date):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM security_handovers
            WHERE site_id = ?
              AND handover_date = ?
            ORDER BY id ASC
            """,
            (site_id, handover_date),
        ).fetchall()

    return [dict(row) for row in rows]


def monthly_summary(site_id, year, month):
    month_text = f"{year:04d}-{month:02d}"

    with get_connection() as connection:
        occurrence_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM security_occurrences
            WHERE site_id = ?
              AND substr(occurrence_date, 1, 7) = ?
            """,
            (site_id, month_text),
        ).fetchone()[0]

        incident_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM security_incidents i
            JOIN security_occurrences o
                ON i.occurrence_id = o.id
            WHERE o.site_id = ?
              AND substr(o.occurrence_date, 1, 7) = ?
            """,
            (site_id, month_text),
        ).fetchone()[0]

        shift_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM security_shifts
            WHERE site_id = ?
              AND substr(shift_date, 1, 7) = ?
            """,
            (site_id, month_text),
        ).fetchone()[0]

        handover_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM security_handovers
            WHERE site_id = ?
              AND substr(handover_date, 1, 7) = ?
            """,
            (site_id, month_text),
        ).fetchone()[0]

    return {
        "site_id": site_id,
        "month": month_text,
        "occurrences": occurrence_count,
        "incidents": incident_count,
        "shifts": shift_count,
        "handovers": handover_count,
    }
