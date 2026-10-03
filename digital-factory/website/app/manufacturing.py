from flask import request, redirect, render_template_string

from database import get_connection
from workflow import audit_event, transition


MANUFACTURING_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MMK Manufacturing</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f5f7;
            margin: 0;
            color: #202124;
        }

        header {
            background: #111827;
            color: white;
            padding: 20px;
        }

        main {
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }

        form {
            background: white;
            padding: 20px;
            border-radius: 12px;
        }

        label {
            display: block;
            margin-top: 15px;
            font-weight: bold;
        }

        input,
        textarea,
        select {
            width: 100%;
            box-sizing: border-box;
            margin-top: 6px;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 16px;
        }

        textarea {
            min-height: 90px;
        }

        button {
            margin-top: 20px;
            padding: 13px 20px;
            border: 0;
            border-radius: 8px;
            font-weight: bold;
        }

        .back {
            display: inline-block;
            margin-top: 18px;
        }
    </style>
</head>

<body>

<header>
    <h1>MMK Manufacturing System</h1>
    <p>Create and track Factory production work</p>
</header>

<main>

<form method="post">

<label>Manufacturing ID</label>
<input name="manufacturing_id"
       placeholder="Example: MFG-0001"
       required>

<label>Job Title</label>
<input name="title"
       placeholder="Manufacturing job title"
       required>

<label>Opportunity ID</label>
<input name="opportunity_id"
       placeholder="Example: OPP-0001">

<label>Product ID</label>
<input name="product_id"
       placeholder="Example: PRD-0001">

<label>Service ID</label>
<input name="service_id"
       placeholder="Example: SRV-0001">

<label>Assigned Member ID</label>
<input name="assigned_member_id"
       placeholder="Example: MBR-0001">

<label>Manufacturing Stage</label>
<input type="text" value="INTAKE" disabled>
<input type="hidden" name="stage" value="INTAKE">
<small>
    New manufacturing jobs always enter the Factory at INTAKE.
    Stage changes happen through the controlled workflow.
</small>

<label>Job Status</label>
<select name="status">
    <option value="OPEN">OPEN</option>
    <option value="IN_PROGRESS">IN PROGRESS</option>
    <option value="BLOCKED">BLOCKED</option>
    <option value="COMPLETED">COMPLETED</option>
</select>

<label>Expected Outcome</label>
<textarea name="expected_outcome"
          placeholder="What should this job produce?"></textarea>

<label>Quality Requirements</label>
<textarea name="quality_requirements"
          placeholder="What must be checked?"></textarea>

<button type="submit">
    SAVE MANUFACTURING JOB
</button>

</form>

<a class="back" href="/dashboard">
    ← Back to Dashboard
</a>

</main>

</body>
</html>
"""


def manufacturing_page():
    if request.method == "POST":
        connection = get_connection()

        opportunity_id = request.form.get(
            "opportunity_id", ""
        ).strip()

        product_id = request.form.get(
            "product_id", ""
        ).strip()

        service_id = request.form.get(
            "service_id", ""
        ).strip()

        member_id = request.form.get(
            "assigned_member_id", ""
        ).strip()

        opportunity_db_id = None
        product_db_id = None
        service_db_id = None
        member_db_id = None

        if opportunity_id:
            row = connection.execute(
                """
                SELECT id FROM opportunities
                WHERE opportunity_id = ?
                """,
                (opportunity_id,),
            ).fetchone()

            if row is None:
                connection.close()
                return "Opportunity ID not found.", 400

            opportunity_db_id = row["id"]

        if product_id:
            row = connection.execute(
                """
                SELECT id FROM products
                WHERE product_id = ?
                """,
                (product_id,),
            ).fetchone()

            if row is None:
                connection.close()
                return "Product ID not found.", 400

            product_db_id = row["id"]

        if service_id:
            row = connection.execute(
                """
                SELECT id FROM services
                WHERE service_id = ?
                """,
                (service_id,),
            ).fetchone()

            if row is None:
                connection.close()
                return "Service ID not found.", 400

            service_db_id = row["id"]

        if member_id:
            row = connection.execute(
                """
                SELECT id FROM members
                WHERE member_id = ?
                """,
                (member_id,),
            ).fetchone()

            if row is None:
                connection.close()
                return "Member ID not found.", 400

            member_db_id = row["id"]

        connection.execute(
            """
            INSERT INTO manufacturing_jobs (
                manufacturing_id,
                title,
                opportunity_id,
                product_id,
                service_id,
                assigned_member_id,
                stage,
                status,
                expected_outcome,
                quality_requirements
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["manufacturing_id"].strip(),
                request.form["title"].strip(),
                opportunity_db_id,
                product_db_id,
                service_db_id,
                member_db_id,
                "INTAKE",
                request.form.get("status", "OPEN"),
                request.form.get(
                    "expected_outcome", ""
                ).strip(),
                request.form.get(
                    "quality_requirements", ""
                ).strip(),
            ),
        )

        manufacturing_row = connection.execute(
            "SELECT id FROM manufacturing_jobs WHERE manufacturing_id = ?",
            (request.form["manufacturing_id"].strip(),),
        ).fetchone()

        audit_event(
            connection,
            f"MFG-CREATE-{request.form['manufacturing_id'].strip()}",
            "MANUFACTURING",
            manufacturing_row["id"],
            "MANUFACTURING_CREATED",
            actor="MMK Founder",
            reason="New manufacturing job entered Factory workflow at INTAKE.",
        )

        connection.commit()
        connection.close()

        return redirect("/dashboard")

    return render_template_string(MANUFACTURING_HTML)


def transition_manufacturing(
    manufacturing_id,
    to_stage,
    actor="MMK Founder",
    reason="",
):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT id, stage
            FROM manufacturing_jobs
            WHERE manufacturing_id = ?
            """,
            (manufacturing_id,),
        ).fetchone()

        if row is None:
            raise ValueError(
                f"Manufacturing job not found: {manufacturing_id}"
            )

        from_stage = row["stage"]

        event_id = transition(
            connection,
            "MANUFACTURING",
            row["id"],
            from_stage,
            to_stage,
            actor=actor,
            reason=reason,
        )

        connection.execute(
            """
            UPDATE manufacturing_jobs
            SET stage = ?
            WHERE id = ?
            """,
            (to_stage, row["id"]),
        )

        connection.commit()
        return event_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
