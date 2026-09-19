from database import get_connection


def create_shift(
    site_id,
    shift_date,
    start_time,
    end_time=None,
    supervisor_id=None,
    notes=None,
):
    if not site_id:
        raise ValueError("Site ID is required")

    if not shift_date:
        raise ValueError("Shift date is required")

    if not start_time:
        raise ValueError("Shift start time is required")

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

        cursor = connection.execute(
            """
            INSERT INTO security_shifts
            (
                site_id,
                supervisor_id,
                shift_date,
                start_time,
                end_time,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                site_id,
                supervisor_id,
                shift_date,
                start_time,
                end_time,
                notes,
            ),
        )

        connection.commit()

        return cursor.lastrowid


def get_shift(shift_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM security_shifts
            WHERE id = ?
            """,
            (shift_id,),
        ).fetchone()

    return dict(row) if row else None


def list_shifts(site_id=None):
    with get_connection() as connection:
        if site_id is None:
            rows = connection.execute(
                """
                SELECT *
                FROM security_shifts
                ORDER BY shift_date DESC, start_time DESC, id DESC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM security_shifts
                WHERE site_id = ?
                ORDER BY shift_date DESC, start_time DESC, id DESC
                """,
                (site_id,),
            ).fetchall()

    return [dict(row) for row in rows]


def close_shift(shift_id):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE security_shifts
            SET status = 'closed',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (shift_id,),
        )
        connection.commit()
