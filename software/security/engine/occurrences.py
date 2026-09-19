from database import get_connection


def create_occurrence(
    site_id,
    occurrence_date,
    occurrence_time,
    category,
    description,
    action_taken=None,
    user_id=None,
):
    if not site_id:
        raise ValueError("Site ID is required")

    if not occurrence_date:
        raise ValueError("Occurrence date is required")

    if not occurrence_time:
        raise ValueError("Occurrence time is required")

    if not category or not category.strip():
        raise ValueError("Occurrence category is required")

    if not description or not description.strip():
        raise ValueError("Occurrence description is required")

    with get_connection() as connection:
        site = connection.execute(
            "SELECT id FROM security_sites WHERE id = ?",
            (site_id,),
        ).fetchone()

        if site is None:
            raise ValueError("Security site does not exist")

        cursor = connection.execute(
            """
            INSERT INTO security_occurrences
            (
                site_id,
                user_id,
                occurrence_date,
                occurrence_time,
                category,
                description,
                action_taken
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                site_id,
                user_id,
                occurrence_date,
                occurrence_time,
                category.strip(),
                description.strip(),
                action_taken,
            ),
        )

        connection.commit()

        return cursor.lastrowid


def get_occurrence(occurrence_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM security_occurrences
            WHERE id = ?
            """,
            (occurrence_id,),
        ).fetchone()

    return dict(row) if row else None


def list_occurrences(site_id=None):
    with get_connection() as connection:
        if site_id is None:
            rows = connection.execute(
                """
                SELECT *
                FROM security_occurrences
                ORDER BY occurrence_date DESC, occurrence_time DESC, id DESC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM security_occurrences
                WHERE site_id = ?
                ORDER BY occurrence_date DESC, occurrence_time DESC, id DESC
                """,
                (site_id,),
            ).fetchall()

    return [dict(row) for row in rows]


def close_occurrence(occurrence_id):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE security_occurrences
            SET status = 'closed',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (occurrence_id,),
        )
        connection.commit()
