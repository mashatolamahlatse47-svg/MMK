from database import get_connection


def create_site(name, address=None, business_id=None):
    if not name or not name.strip():
        raise ValueError("Site name is required")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO security_sites
            (business_id, name, address)
            VALUES (?, ?, ?)
            """,
            (business_id, name.strip(), address),
        )
        connection.commit()

        return cursor.lastrowid


def get_site(site_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM security_sites
            WHERE id = ?
            """,
            (site_id,),
        ).fetchone()

    return dict(row) if row else None


def list_sites():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM security_sites
            ORDER BY id
            """
        ).fetchall()

    return [dict(row) for row in rows]


def deactivate_site(site_id):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE security_sites
            SET status = 'inactive',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (site_id,),
        )
        connection.commit()
