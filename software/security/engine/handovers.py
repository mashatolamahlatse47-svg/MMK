from database import get_connection


VALID_STATUSES = {
    "pending",
    "completed",
    "cancelled",
}


def create_handover(
    site_id,
    handover_date,
    shift_id=None,
    from_user_id=None,
    to_user_id=None,
    notes=None,
    outstanding_items=None,
):
    if not site_id:
        raise ValueError("Site ID is required")

    if not handover_date:
        raise ValueError("Handover date is required")

    with get_connection() as connection:
        site = connection.execute(
            """
            SELECT id
            FROM security_sites
            WHERE id = ?
            """,
            (site_id,),
        ).fetchone()

        if site is None:
            raise ValueError("Security site does not exist")

        if shift_id is not None:
            shift = connection.execute(
                """
                SELECT id
                FROM security_shifts
                WHERE id = ?
                AND site_id = ?
                """,
                (shift_id, site_id),
            ).fetchone()

            if shift is None:
                raise ValueError(
                    "Shift does not exist for this site"
                )

        cursor = connection.execute(
            """
            INSERT INTO security_handovers
            (
                site_id,
                from_user_id,
                to_user_id,
                shift_id,
                handover_date,
                notes,
                outstanding_items
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                site_id,
                from_user_id,
                to_user_id,
                shift_id,
                handover_date,
                notes,
                outstanding_items,
            ),
        )

        connection.commit()

        return cursor.lastrowid


def get_handover(handover_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM security_handovers
            WHERE id = ?
            """,
            (handover_id,),
        ).fetchone()

    return dict(row) if row else None


def list_handovers(site_id=None):
    with get_connection() as connection:
        if site_id is None:
            rows = connection.execute(
                """
                SELECT *
                FROM security_handovers
                ORDER BY handover_date DESC, id DESC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM security_handovers
                WHERE site_id = ?
                ORDER BY handover_date DESC, id DESC
                """,
                (site_id,),
            ).fetchall()

    return [dict(row) for row in rows]


def complete_handover(handover_id):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE security_handovers
            SET status = 'completed',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (handover_id,),
        )
        connection.commit()
