from pathlib import Path
import json
import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "app"),
)

from generate_qr import generate_qr as create_qr


def test_qr_generation(tmp_path, monkeypatch):
    import generate_qr

    monkeypatch.setattr(generate_qr, "OUTPUT_DIR", tmp_path)

    result = create_qr(
        "http://127.0.0.1:8060/menu/demo",
        "test-menu",
    )

    assert result.exists()
    assert result.suffix == ".png"
    assert result.stat().st_size > 0


def test_create_menu_with_custom_base_url(tmp_path, monkeypatch):
    import create_menu

    menu_dir = tmp_path / "menus"
    config_file = tmp_path / "menus.json"
    qr_dir = tmp_path / "qr"

    monkeypatch.setattr(create_menu, "MENU_DIR", menu_dir)
    monkeypatch.setattr(create_menu, "CONFIG_FILE", config_file)
    monkeypatch.setattr(create_menu, "QR_DIR", qr_dir)

    monkeypatch.setattr(
        create_menu,
        "generate_qr",
        lambda url, name: qr_dir / f"{name}.png",
    )

    source_pdf = tmp_path / "source.pdf"
    source_pdf.write_bytes(b"%PDF-test-menu")

    result = create_menu.create_menu(
        "Test Cafe",
        "test-cafe",
        source_pdf,
        "https://example.com",
    )

    assert result["business_name"] == "Test Cafe"
    assert result["slug"] == "test-cafe"
    assert result["url"] == "https://example.com/menu/test-cafe"
    assert result["pdf"] == menu_dir / "test-cafe.pdf"
    assert result["qr"] == qr_dir / "MMK-test-cafe.png"

    assert (menu_dir / "test-cafe.pdf").exists()

    saved_menus = json.loads(config_file.read_text(encoding="utf-8"))

    assert saved_menus["test-cafe"]["business_name"] == "Test Cafe"
    assert saved_menus["test-cafe"]["pdf"] == "test-cafe.pdf"
