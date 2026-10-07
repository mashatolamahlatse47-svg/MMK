from pathlib import Path
import json
import re
import shutil
import sys

from generate_qr import generate_qr

BASE_DIR = Path(__file__).resolve().parent.parent
MENU_DIR = BASE_DIR / "menus"
CONFIG_FILE = BASE_DIR / "app" / "menus.json"
QR_DIR = BASE_DIR / "static" / "qr"

DEFAULT_BASE_URL = "http://127.0.0.1:8060"

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_business_name(name):
    name = name.strip()

    if not name:
        raise ValueError("Business name cannot be empty.")

    if len(name) > 100:
        raise ValueError("Business name is too long.")

    return name


def validate_slug(slug):
    slug = slug.strip().lower()

    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError(
            "Slug must use lowercase letters, numbers, and hyphens only."
        )

    return slug


def validate_pdf_source(pdf_source):
    source = Path(pdf_source).expanduser()

    if not source.is_file():
        raise FileNotFoundError(f"PDF not found: {source}")

    if source.suffix.lower() != ".pdf":
        raise ValueError("Menu file must be a PDF.")

    return source


def load_menus():
    if not CONFIG_FILE.exists():
        return {}

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_menus(menus):
    temp_file = CONFIG_FILE.with_suffix(".json.tmp")

    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(menus, file, indent=2)
        file.write("\n")

    temp_file.replace(CONFIG_FILE)


def create_menu(business_name, slug, pdf_source, base_url=DEFAULT_BASE_URL):
    business_name = validate_business_name(business_name)
    slug = validate_slug(slug)
    pdf_source = validate_pdf_source(pdf_source)

    menus = load_menus()

    if slug in menus:
        raise ValueError(f"Slug already exists: {slug}")

    stored_filename = f"{slug}.pdf"
    destination = MENU_DIR / stored_filename

    if destination.exists():
        raise FileExistsError(
            f"Menu PDF already exists: {destination}"
        )

    for existing_slug, config in menus.items():
        if config.get("pdf") == stored_filename:
            raise ValueError(
                f"PDF filename is already registered: {stored_filename}"
            )

    MENU_DIR.mkdir(parents=True, exist_ok=True)
    QR_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copy2(pdf_source, destination)

    menus[slug] = {
        "business_name": business_name,
        "pdf": stored_filename,
    }

    save_menus(menus)

    menu_url = f"{base_url.rstrip('/')}/menu/{slug}"
    qr_name = f"MMK-{slug}"
    qr_path = generate_qr(menu_url, qr_name)

    return {
        "business_name": business_name,
        "slug": slug,
        "pdf": destination,
        "url": menu_url,
        "qr": qr_path,
    }


def main():
    if len(sys.argv) not in (4, 5):
        print(
            "Usage: python app/create_menu.py "
            '"BUSINESS NAME" SLUG MENU.pdf [BASE_URL]'
        )
        raise SystemExit(1)

    business_name = sys.argv[1]
    slug = sys.argv[2]
    pdf_source = sys.argv[3]
    base_url = sys.argv[4] if len(sys.argv) == 5 else DEFAULT_BASE_URL

    try:
        result = create_menu(
            business_name,
            slug,
            pdf_source,
            base_url,
        )
    except (ValueError, FileNotFoundError, FileExistsError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)

    print()
    print("MMK QR MENU CREATED")
    print("====================")
    print(f"Business : {result['business_name']}")
    print(f"Slug     : {result['slug']}")
    print(f"PDF      : {result['pdf']}")
    print(f"Menu URL : {result['url']}")
    print(f"QR Code  : {result['qr']}")


if __name__ == "__main__":
    main()
