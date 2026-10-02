from flask import redirect, render_template_string, request, url_for

from database import get_connection
from workflow import transition


OPPORTUNITY_LIST_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MMK - Opportunities</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f5f7;
            color: #202124;
        }

        header {
            background: #111827;
            color: white;
            padding: 22px;
        }

        main {
            max-width: 900px;
            margin: auto;
            padding: 20px;
        }

        .actions {
            margin-bottom: 20px;
        }

        a, button {
            display: inline-block;
            padding: 11px 16px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
        }

        .new {
            background: #111827;
            color: white;
        }

        .back {
            color: #111827;
        }

        .card {
            background: white;
            padding: 18px;
            margin-bottom: 14px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .id {
            font-size: 13px;
            color: #666;
        }

        h2 {
            margin-bottom: 8px;
        }

        .meta {
            margin-top: 10px;
            line-height: 1.6;
        }
    </style>
</head>

<body>

<header>
    <h1>MMK Opportunity System</h1>
    <p>Factory opportunities</p>
</header>

<main>

    <div class="actions">
        <a class="new" href="/opportunities/new">+ New Opportunity</a>
        <a class="back" href="/dashboard">← Dashboard</a>
    </div>

    {% if opportunities %}
        {% for opportunity in opportunities %}
        <div class="card">
            <div class="id">{{ opportunity["opportunity_id"] }}</div>
            <h2>{{ opportunity["title"] }}</h2>

            <div class="meta">
                <strong>Category:</strong> {{ opportunity["category"] or "Not set" }}<br>
                <strong>Target Customer:</strong> {{ opportunity["target_customer"] or "Not set" }}<br>
                <strong>Status:</strong> {{ opportunity["status"] }}<br>
                <strong>Owner:</strong> {{ opportunity["owner"] }}
            </div>

            {% set next_statuses = {
                "IDEA": ["ASSESSMENT"],
                "ASSESSMENT": ["APPROVED", "REJECTED", "ON_HOLD"],
                "ON_HOLD": ["ASSESSMENT"]
            } %}

            {% if next_statuses.get(opportunity["status"]) %}
                <div class="actions" style="margin-top: 14px;">
                    {% for next_status in next_statuses[opportunity["status"]] %}
                    <form method="post"
                          action="/opportunities/{{ opportunity["opportunity_id"] }}/transition"
                          style="display: inline;">
                        <input type="hidden" name="to_status" value="{{ next_status }}">
                        <button type="submit">
                            Move to {{ next_status }}
                        </button>
                    </form>
                    {% endfor %}
                </div>
            {% endif %}
        </div>
        {% endfor %}
    {% else %}
        <div class="card">
            <h2>No opportunities yet</h2>
            <p>Create the first Factory opportunity.</p>
        </div>
    {% endif %}

</main>

</body>
</html>
"""


def opportunity_list():
    connection = get_connection()

    opportunities = connection.execute(
        """
        SELECT *
        FROM opportunities
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template_string(
        OPPORTUNITY_LIST_HTML,
        opportunities=opportunities,
    )


def transition_opportunity_route(opportunity_id):
    to_status = request.form.get("to_status", "").strip()

    transition_opportunity(
        opportunity_id,
        to_status,
        actor="MMK Founder",
        reason=f"Controlled UI transition to {to_status}.",
    )

    return redirect(url_for("opportunities"))


def transition_opportunity(opportunity_id, to_status, actor="MMK", reason=""):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT id, status
            FROM opportunities
            WHERE opportunity_id = ?
            """,
            (opportunity_id,),
        ).fetchone()

        if row is None:
            raise ValueError(f"Opportunity not found: {opportunity_id}")

        from_status = row["status"]

        event_id = transition(
            connection,
            "OPPORTUNITY",
            row["id"],
            from_status,
            to_status,
            actor=actor,
            reason=reason,
        )

        connection.execute(
            """
            UPDATE opportunities
            SET status = ?
            WHERE id = ?
            """,
            (to_status, row["id"]),
        )

        connection.commit()
        return event_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
