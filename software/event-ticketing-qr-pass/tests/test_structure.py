from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_structure():
    required = [
        "app.py",
        "README.md",
        "CUSTOMER-GUIDE.md",
        "SECURITY.md",
        "VERSION",
        "website/index.html",
        "website/style.css",
        "website/app.js",
        "templates/checkin.html",
    ]

    for item in required:
        assert (ROOT / item).exists(), item


def test_app_compiles():
    app_file = ROOT / "app.py"
    compile(
        app_file.read_text(encoding="utf-8"),
        str(app_file),
        "exec",
    )
