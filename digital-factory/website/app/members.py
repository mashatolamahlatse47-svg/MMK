from flask import request, redirect, render_template_string

from database import get_connection


MEMBER_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MMK - Create Member</title>

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
    <h1>MMK Member System</h1>
    <p>Register a person and their skills in the Factory</p>
</header>

<main>

    <form method="post">

        <label for="member_id">Member ID</label>
        <input
            id="member_id"
            name="member_id"
            placeholder="Example: MBR-0001"
            required
        >

        <label for="name">Member Name</label>
        <input
            id="name"
            name="name"
            placeholder="Member name"
            required
        >

        <label for="skills">Skills</label>
        <textarea
            id="skills"
            name="skills"
            placeholder="Example: Photography, design, customer service"
        ></textarea>

        <label for="training_status">Training Status</label>
        <select id="training_status" name="training_status">
            <option value="NOT_STARTED">NOT STARTED</option>
            <option value="IN_PROGRESS">IN PROGRESS</option>
            <option value="COMPLETED">COMPLETED</option>
        </select>

        <label for="portfolio">Portfolio</label>
        <textarea
            id="portfolio"
            name="portfolio"
            placeholder="Portfolio link or description"
        ></textarea>

        <label for="participation_status">Participation Status</label>
        <select id="participation_status" name="participation_status">
            <option value="ACTIVE">ACTIVE</option>
            <option value="PAUSED">PAUSED</option>
            <option value="INACTIVE">INACTIVE</option>
        </select>

        <button type="submit">SAVE MEMBER</button>

    </form>

    <a class="back" href="/dashboard">← Back to Dashboard</a>

</main>

</body>
</html>
"""


def member_page():
    if request.method == "POST":
        connection = get_connection()

        connection.execute(
            """
            INSERT INTO members (
                member_id,
                name,
                skills,
                training_status,
                portfolio,
                participation_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["member_id"].strip(),
                request.form["name"].strip(),
                request.form.get("skills", "").strip(),
                request.form.get(
                    "training_status",
                    "NOT_STARTED"
                ),
                request.form.get("portfolio", "").strip(),
                request.form.get(
                    "participation_status",
                    "ACTIVE"
                ),
            ),
        )

        connection.commit()
        connection.close()

        return redirect("/dashboard")

    return render_template_string(MEMBER_HTML)
