from flask import request, redirect, url_for

from database import get_connection
from workspace_manager import create_project_workspace


def project_page():
    if request.method == "POST":
        project_id = request.form["project_id"].strip()
        name = request.form["name"].strip()
        owner = request.form["owner"].strip() or "MMK"
        project_type = request.form["project_type"].strip()
        description = request.form["description"].strip()
        status = request.form["status"].strip()
        current_version = request.form["current_version"].strip() or "0.1.0"
        opportunity_id = request.form["opportunity_id"].strip()
        product_id = request.form["product_id"].strip()
        service_id = request.form["service_id"].strip()
        notes = request.form["notes"].strip()

        connection = get_connection()

        opportunity_db_id = None
        product_db_id = None
        service_db_id = None

        if opportunity_id:
            row = connection.execute(
                "SELECT id FROM opportunities WHERE opportunity_id = ?",
                (opportunity_id,),
            ).fetchone()

            if not row:
                connection.close()
                return "Opportunity not found", 400

            opportunity_db_id = row["id"]

        if product_id:
            row = connection.execute(
                "SELECT id FROM products WHERE product_id = ?",
                (product_id,),
            ).fetchone()

            if not row:
                connection.close()
                return "Product not found", 400

            product_db_id = row["id"]

        if service_id:
            row = connection.execute(
                "SELECT id FROM services WHERE service_id = ?",
                (service_id,),
            ).fetchone()

            if not row:
                connection.close()
                return "Service not found", 400

            service_db_id = row["id"]

        connection.execute(
            """
            INSERT INTO projects (
                project_id,
                name,
                owner,
                project_type,
                description,
                status,
                current_version,
                opportunity_id,
                product_id,
                service_id,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                name,
                owner,
                project_type,
                description,
                status,
                current_version,
                opportunity_db_id,
                product_db_id,
                service_db_id,
                notes,
            ),
        )

        connection.commit()

        try:
            workspace_path = create_project_workspace(project_id)
        except Exception as error:
            connection.close()
            return f"Project saved, but workspace creation failed: {error}", 500

        connection.close()

        return redirect(url_for("dashboard"))

    return """
    <!doctype html>
    <html>
    <head>
        <title>New Project - MMK</title>
    </head>
    <body>
        <h1>MMK PROJECT SYSTEM</h1>
        <p>Create a new project.</p>

        <form method="post">

            <label>Project ID</label><br>
            <input name="project_id" placeholder="PRJ-0001" required><br><br>

            <label>Project Name</label><br>
            <input name="name" placeholder="MMK Beauty Business System" required><br><br>

            <label>Owner</label><br>
            <input name="owner" value="MMK"><br><br>

            <label>Project Type</label><br>
            <select name="project_type">
                <option value="WEBSITE">Website</option>
                <option value="SOFTWARE">Software</option>
                <option value="APP">App</option>
                <option value="GAME">Game</option>
                <option value="ANIMATION">Animation / Film</option>
                <option value="DESIGN">Design / Art</option>
                <option value="DOCUMENT">Digital Document</option>
                <option value="SERVICE_SYSTEM">Service System</option>
                <option value="OTHER">Other</option>
            </select><br><br>

            <label>Description</label><br>
            <textarea name="description" rows="5" cols="40"></textarea><br><br>

            <label>Status</label><br>
            <select name="status">
                <option value="IDEA">IDEA</option>
                <option value="PLANNING">PLANNING</option>
                <option value="BUILDING">BUILDING</option>
                <option value="TESTING">TESTING</option>
                <option value="REVIEW">REVIEW</option>
                <option value="READY">READY</option>
                <option value="RELEASED">RELEASED</option>
                <option value="ARCHIVED">ARCHIVED</option>
            </select><br><br>

            <label>Current Version</label><br>
            <input name="current_version" value="0.1.0"><br><br>

            <label>Opportunity ID (optional)</label><br>
            <input name="opportunity_id" placeholder="OPP-0001"><br><br>

            <label>Product ID (optional)</label><br>
            <input name="product_id" placeholder="PRD-0001"><br><br>

            <label>Service ID (optional)</label><br>
            <input name="service_id" placeholder="SRV-0001"><br><br>

            <label>Notes</label><br>
            <textarea name="notes" rows="4" cols="40"></textarea><br><br>

            <button type="submit">CREATE PROJECT</button>

        </form>

        <br>
        <a href="/dashboard">Back to Dashboard</a>
    </body>
    </html>
    """
