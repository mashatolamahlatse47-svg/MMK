from flask import request, redirect, render_template_string

from database import get_connection


PRODUCT_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MMK - Create Product</title>
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
    <h1>MMK Product System</h1>
    <p>Create a product from a Factory opportunity</p>
</header>

<main>

    <form method="post">

        <label for="product_id">Product ID</label>
        <input id="product_id" name="product_id"
               placeholder="Example: PRD-0001" required>

        <label for="name">Product Name</label>
        <input id="name" name="name"
               placeholder="Product name" required>

        <label for="version">Version</label>
        <input id="version" name="version"
               value="0.1.0" required>

        <label for="description">Description</label>
        <textarea id="description" name="description"
                  placeholder="What is this product?"></textarea>

        <label for="opportunity_id">Source Opportunity ID</label>
        <input id="opportunity_id" name="opportunity_id"
               placeholder="Example: OPP-0001">

        <label for="owner">Owner</label>
        <input id="owner" name="owner" value="MMK">

        <label for="manufacturing_status">Manufacturing Status</label>
        <select id="manufacturing_status" name="manufacturing_status">
            <option value="PLANNED">PLANNED</option>
            <option value="IN_PROGRESS">IN PROGRESS</option>
            <option value="CHECK">CHECK</option>
            <option value="TEST">TEST</option>
            <option value="READY">READY</option>
        </select>

        <label for="quality_status">Quality Status</label>
        <select id="quality_status" name="quality_status">
            <option value="PENDING">PENDING</option>
            <option value="IN_REVIEW">IN REVIEW</option>
            <option value="PASSED">PASSED</option>
            <option value="FAILED">FAILED</option>
        </select>

        <label for="pricing">Pricing</label>
        <input id="pricing" name="pricing"
               placeholder="Example: R300 one-time">

        <label for="ip_status">IP Status</label>
        <select id="ip_status" name="ip_status">
            <option value="REVIEW">REVIEW</option>
            <option value="MMK_OWNED">MMK OWNED</option>
            <option value="SHARED">SHARED</option>
            <option value="CLIENT_OWNED">CLIENT OWNED</option>
        </select>

        <label for="release_status">Release Status</label>
        <select id="release_status" name="release_status">
            <option value="INTERNAL">INTERNAL</option>
            <option value="TEST">TEST</option>
            <option value="DEMO">DEMO</option>
            <option value="READY">READY</option>
            <option value="COMMERCIAL">COMMERCIAL</option>
        </select>

        <button type="submit">SAVE PRODUCT</button>

    </form>

    <a class="back" href="/dashboard">← Back to Dashboard</a>

</main>

</body>
</html>
"""


def product_page():
    if request.method == "POST":
        connection = get_connection()

        opportunity_id = request.form.get("opportunity_id", "").strip()

        opportunity_db_id = None

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

        connection.execute(
            """
            INSERT INTO products (
                product_id,
                name,
                version,
                description,
                opportunity_id,
                owner,
                manufacturing_status,
                quality_status,
                pricing,
                ip_status,
                release_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["product_id"].strip(),
                request.form["name"].strip(),
                request.form.get("version", "0.1.0").strip(),
                request.form.get("description", "").strip(),
                opportunity_db_id,
                request.form.get("owner", "MMK").strip() or "MMK",
                request.form.get("manufacturing_status", "PLANNED"),
                request.form.get("quality_status", "PENDING"),
                request.form.get("pricing", "").strip(),
                request.form.get("ip_status", "REVIEW"),
                request.form.get("release_status", "INTERNAL"),
            ),
        )

        connection.commit()
        connection.close()

        return redirect("/dashboard")

    return render_template_string(PRODUCT_HTML)
