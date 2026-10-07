from pathlib import Path
import json

from flask import Flask, abort, redirect, send_from_directory

BASE_DIR = Path(__file__).resolve().parent.parent
MENU_DIR = BASE_DIR / "menus"

app = Flask(__name__)

CONFIG_FILE = BASE_DIR / "app" / "menus.json"


def load_menus():
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def home():
    return """
    <h1>MMK QR Menu Generator</h1>
    <p>Digital menu service is running.</p>
    <p>Demo menu: <a href="/menu/demo">/menu/demo</a></p>
    """


@app.route("/menu/<slug>")
def menu(slug):
    menus = load_menus()
    menu_config = menus.get(slug)

    if not menu_config:
        abort(404)

    filename = menu_config["pdf"]
    menu_path = MENU_DIR / filename

    if not menu_path.is_file():
        abort(404)

    return redirect(f"/pdf/{filename}")


@app.route("/pdf/<path:filename>")
def pdf(filename):
    return send_from_directory(
        MENU_DIR,
        filename,
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8060, debug=False)
