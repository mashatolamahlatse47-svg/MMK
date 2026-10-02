from flask import request, redirect, render_template_string

from database import get_connection
from workflow import audit_event


OPPORTUNITY_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MMK - Create Opportunity</title>
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
    <h1>MMK Opportunity System</h1>
    <p>Create a new Factory opportunity</p>
</header>

<main>

    <form method="post">

        <label for="opportunity_id">Opportunity ID</label>
        <input id="opportunity_id" name="opportunity_id"
               placeholder="Example: OPP-0001" required>

        <label for="title">Title</label>
        <input id="title" name="title"
               placeholder="Opportunity name" required>

        <label for="description">Description</label>
        <textarea id="description" name="description"
                  placeholder="What is the opportunity?"></textarea>

        <label for="source">Source</label>
        <input id="source" name="source"
               placeholder="Where did this opportunity come from?">

        <label for="category">Category</label>
        <input id="category" name="category"
               placeholder="Example: Software, Clothing, Service">

        <label for="target_customer">Target Customer</label>
        <input id="target_customer" name="target_customer"
               placeholder="Who needs this?">

        <label for="expected_value">Expected Value</label>
        <input id="expected_value" name="expected_value"
               type="number" step="0.01"
               placeholder="Optional estimated value">

        <label for="required_skills">Required Skills</label>
        <input id="required_skills" name="required_skills"
               placeholder="Skills needed">

        <label for="status">Status</label>
        <input id="status" type="text" value="IDEA" disabled>
        <input type="hidden" name="status" value="IDEA">
        <small>
            New opportunities always enter the Factory at IDEA.
            Status changes happen through the controlled workflow.
        </small>

        <label for="owner">Owner</label>
        <input id="owner" name="owner" value="MMK">

        <label for="notes">Notes</label>
        <textarea id="notes" name="notes"
                  placeholder="Additional notes"></textarea>

        <button type="submit">SAVE OPPORTUNITY</button>

    </form>

    <a class="back" href="/dashboard">← Back to Dashboard</a>

</main>

</body>
</html>
"""


def opportunity_page():
    if request.method == "POST":
        expected_value = request.form.get("expected_value", "").strip()

        value = None
        if expected_value:
            value = float(expected_value)

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO opportunities (
                opportunity_id,
                title,
                description,
                source,
                category,
                target_customer,
                expected_value,
                required_skills,
                status,
                owner,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["opportunity_id"].strip(),
                request.form["title"].strip(),
                request.form.get("description", "").strip(),
                request.form.get("source", "").strip(),
                request.form.get("category", "").strip(),
                request.form.get("target_customer", "").strip(),
                value,
                request.form.get("required_skills", "").strip(),
                "IDEA",
                request.form.get("owner", "MMK").strip() or "MMK",
                request.form.get("notes", "").strip(),
            ),
        )

        opportunity_row = connection.execute(
            "SELECT id FROM opportunities WHERE opportunity_id = ?",
            (request.form["opportunity_id"].strip(),),
        ).fetchone()

        audit_event(
            connection,
            f"OPP-CREATE-{request.form['opportunity_id'].strip()}",
            "OPPORTUNITY",
            opportunity_row["id"],
            "OPPORTUNITY_CREATED",
            actor=request.form.get("owner", "MMK").strip() or "MMK",
            reason="New opportunity entered Factory workflow at IDEA.",
        )

        connection.commit()
        connection.close()

        return redirect("/dashboard")

    return render_template_string(OPPORTUNITY_HTML)
