from flask import request, redirect, render_template_string

from database import get_connection


SERVICE_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MMK - Create Service</title>
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
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }

        form {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        label {
            display: block;
            margin-top: 16px;
            font-weight: bold;
        }

        input, textarea, select {
            width: 100%;
            box-sizing: border-box;
            margin-top: 7px;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 16px;
        }

        textarea {
            min-height: 100px;
        }

        button {
            margin-top: 20px;
            padding: 13px 20px;
            border: 0;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
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
    <h1>MMK Service System</h1>
    <p>Create a service from a Factory opportunity</p>
</header>

<main>

    <form method="post">

        <label for="service_id">Service ID</label>
        <input id="service_id" name="service_id"
               placeholder="Example: SRV-0001" required>

        <label for="name">Service Name</label>
        <input id="name" name="name"
               placeholder="Service name" required>

        <label for="description">Description</label>
        <textarea id="description" name="description"
                  placeholder="What does this service provide?"></textarea>

        <label for="opportunity_id">Source Opportunity ID</label>
        <input id="opportunity_id" name="opportunity_id"
               placeholder="Example: OPP-0001">

        <label for="required_skills">Required Skills</label>
        <input id="required_skills" name="required_skills"
               placeholder="Skills needed">

        <label for="delivery_workflow">Delivery Workflow</label>
        <textarea id="delivery_workflow" name="delivery_workflow"
                  placeholder="Describe how the service is delivered"></textarea>

        <label for="pricing_model">Pricing Model</label>
        <input id="pricing_model" name="pricing_model"
               placeholder="Example: Per job, hourly, monthly">

        <label for="responsible_member_id">Responsible Member ID</label>
        <input id="responsible_member_id" name="responsible_member_id"
               placeholder="Optional">

        <label for="service_status">Service Status</label>
        <select id="service_status" name="service_status">
            <option value="PLANNED">PLANNED</option>
            <option value="IN_PROGRESS">IN PROGRESS</option>
            <option value="TEST">TEST</option>
            <option value="READY">READY</option>
            <option value="ACTIVE">ACTIVE</option>
        </select>

        <label for="quality_requirements">Quality Requirements</label>
        <textarea id="quality_requirements" name="quality_requirements"
                  placeholder="What must be checked before delivery?"></textarea>

        <button type="submit">SAVE SERVICE</button>

    </form>

    <a class="back" href="/dashboard">← Back to Dashboard</a>

</main>

</body>
</html>
"""


def service_page():
    if request.method == "POST":
        connection = get_connection()

        opportunity_id = request.form.get("opportunity_id", "").strip()
        responsible_member_id = request.form.get(
            "responsible_member_id", ""
        ).strip()

        opportunity_db_id = None
        member_db_id = None

        if opportunity_id:
            row = connection.execute(
                """
                SELECT id
                FROM opportunities
                WHERE opportunity_id = ?
                """,
                (opportunity_id,),
            ).fetchone()

            if row is None:
                connection.close()
                return "Source Opportunity ID not found.", 400

            opportunity_db_id = row["id"]

        if responsible_member_id:
            row = connection.execute(
                """
                SELECT id
                FROM members
                WHERE member_id = ?
                """,
                (responsible_member_id,),
            ).fetchone()

            if row is None:
                connection.close()
                return "Responsible Member ID not found.", 400

            member_db_id = row["id"]

        connection.execute(
            """
            INSERT INTO services (
                service_id,
                name,
                description,
                opportunity_id,
                required_skills,
                delivery_workflow,
                pricing_model,
                responsible_member_id,
                service_status,
                quality_requirements
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["service_id"].strip(),
                request.form["name"].strip(),
                request.form.get("description", "").strip(),
                opportunity_db_id,
                request.form.get("required_skills", "").strip(),
                request.form.get("delivery_workflow", "").strip(),
                request.form.get("pricing_model", "").strip(),
                member_db_id,
                request.form.get("service_status", "PLANNED"),
                request.form.get("quality_requirements", "").strip(),
            ),
        )

        connection.commit()
        connection.close()

        return redirect("/dashboard")

    return render_template_string(SERVICE_HTML)
