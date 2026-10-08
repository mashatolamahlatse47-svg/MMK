from pathlib import Path
import json
import sys
from PIL import Image


SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}


def inspect_image(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    if path.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Unsupported image type: {path.suffix}")

    with Image.open(path) as image:
        report = {
            "filename": path.name,
            "format": image.format,
            "mode": image.mode,
            "width": image.width,
            "height": image.height,
            "pixels": image.width * image.height,
            "has_alpha": "A" in image.getbands(),
        }

        if "A" in image.getbands():
            alpha = image.getchannel("A")
            histogram = alpha.histogram()

            transparent = histogram[0]
            opaque = histogram[255]
            partial = sum(histogram[1:255])
            total = image.width * image.height

            report["transparent_pixels"] = transparent
            report["opaque_pixels"] = opaque
            report["partial_alpha_pixels"] = partial
            report["transparent_percent"] = round(
                (transparent / total) * 100, 2
            )
            report["opaque_percent"] = round(
                (opaque / total) * 100, 2
            )
            report["partial_alpha_percent"] = round(
                (partial / total) * 100, 2
            )

            if transparent > 0:
                report["transparency_status"] = "REAL_TRANSPARENCY_PRESENT"
            else:
                report["transparency_status"] = "NO_TRANSPARENT_PIXELS"
        else:
            report["transparent_pixels"] = 0
            report["opaque_pixels"] = image.width * image.height
            report["partial_alpha_pixels"] = 0
            report["transparent_percent"] = 0.0
            report["opaque_percent"] = 100.0
            report["partial_alpha_percent"] = 0.0
            report["transparency_status"] = "NO_ALPHA_CHANNEL"

    return report


def prepare_png(source_path, output_path):
    source_path = Path(source_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(source_path) as image:
        rgba = image.convert("RGBA")
        rgba.save(output_path, "PNG")

    return output_path


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools_image_engine.py <image>")
        raise SystemExit(1)

    source = Path(sys.argv[1])
    report = inspect_image(source)

    print(json.dumps(report, indent=2))

    output = Path("exports") / f"{source.stem}-MMK-ready.png"
    prepare_png(source, output)

    print(f"\nPrepared PNG: {output}")


if __name__ == "__main__":
    main()
