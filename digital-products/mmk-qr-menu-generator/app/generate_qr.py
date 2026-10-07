from pathlib import Path
import sys

import qrcode


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "static" / "qr"


def generate_qr(menu_url: str, output_name: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"{output_name}.png"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )

    qr.add_data(menu_url)
    qr.make(fit=True)

    image = qr.make_image()
    image.save(output_path)

    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python app/generate_qr.py "
            "<menu_url> <output_name>"
        )
        raise SystemExit(1)

    path = generate_qr(sys.argv[1], sys.argv[2])
    print(f"QR generated: {path}")
