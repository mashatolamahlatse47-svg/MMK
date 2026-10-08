from pathlib import Path
import sys
from PIL import Image


def remove_simple_background(source_path, output_path, tolerance=18):
    source_path = Path(source_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(source_path) as image:
        image = image.convert("RGBA")

        pixels = image.load()
        width, height = image.size

        corners = [
            pixels[0, 0],
            pixels[width - 1, 0],
            pixels[0, height - 1],
            pixels[width - 1, height - 1],
        ]

        background = tuple(
            sum(pixel[channel] for pixel in corners) // len(corners)
            for channel in range(3)
        )

        changed = 0

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]

                distance = (
                    abs(r - background[0])
                    + abs(g - background[1])
                    + abs(b - background[2])
                )

                if distance <= tolerance:
                    pixels[x, y] = (r, g, b, 0)
                    changed += 1

        image.save(output_path, "PNG")

    return changed


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python background_remover.py "
            "<input-image> <output-image>"
        )
        raise SystemExit(1)

    source = Path(sys.argv[1])
    output = Path(sys.argv[2])

    changed = remove_simple_background(source, output)

    print(f"Background pixels made transparent: {changed}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
