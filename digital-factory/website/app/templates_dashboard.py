import sqlite3

from flask import render_template_string

from database import DATABASE_PATH

DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MMK Digital Factory</title>
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

        header h1 {
            margin: 0 0 6px;
        }

        header p {
            margin: 0;
            opacity: 0.8;
        }

        main {
            padding: 20px;
            max-width: 1100px;
            margin: auto;
        }

        .status {
            background: white;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .online {
            font-weight: bold;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .card h2 {
            margin-top: 0;
            font-size: 18px;
        }

        .number {
            font-size: 32px;
            font-weight: bold;
        }

        footer {
            text-align: center;
            padding: 25px;
            color: #666;
        }
    </style>
</head>

<body>

<header>
    <h1>MMK DIGITAL FACTORY</h1>
    <p>Internal Factory Control Center — v0.1</p>
</header>

<main>

    <div class="status">
        <strong>Factory Engine:</strong>
        <span class="online">ONLINE</span>
    </div>

    <div class="grid">

        <div class="card">
            <h2>Opportunities</h2>
            <div class="number">{{ opportunities }}</div>
        </div>

        <div class="card">
            <h2>Products</h2>
            <div class="number">{{ products }}</div>
        </div>

        <div class="card">
            <h2>Services</h2>
            <div class="number">{{ services }}</div>
        </div>

        <div class="card">
            <h2>Members</h2>
            <div class="number">{{ members }}</div>
        </div>

        <div class="card">
            <h2>Manufacturing Jobs</h2>
            <div class="number">{{ manufacturing_jobs }}</div>
        </div>

        <div class="card">
            <h2>Quality Checks</h2>
            <div class="number">{{ quality_checks }}</div>
        </div>

        <div class="card">
            <h2>Customers</h2>
            <div class="number">{{ customers }}</div>
        </div>

        <div class="card">
            <h2>Training Assets</h2>
            <div class="number">{{ training_assets }}</div>
        </div>

    </div>

</main>

<footer>
    MMK Digital Factory — Internal Build v0.1
</footer>

</body>
</html>
"""


def dashboard():
    connection = sqlite3.connect(DATABASE_PATH)

    counts = {}

    tables = [
        "opportunities",
        "products",
        "services",
        "members",
        "manufacturing_jobs",
        "quality_checks",
        "customers",
        "training_assets",
    ]

    for table in tables:
        counts[table] = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

    connection.close()

    return render_template_string(DASHBOARD_HTML, **counts)
