import argparse
import random
from pathlib import Path
from typing import Union
from PIL import Image
from time import time

Image.MAX_IMAGE_PIXELS = None


def process_image(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    scale_min: float,
    scale_max: float,
    output_width: int,
    output_height: int,
    max_retries: int = 10,
) -> None:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"The path {input_path} does not exist.")
        return

    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

    if input_path.is_file() and input_path.suffix.lower() in image_extensions:
        with Image.open(input_path) as img:
            if img.width < output_width or img.height < output_height:
                return

            valid_scale = False
            retries = 0
            while not valid_scale and retries < max_retries:
                scale_factor = random.uniform(scale_min, scale_max)
                scaled_width = int(img.width * scale_factor)
                scaled_height = int(img.height * scale_factor)
                if scaled_width >= output_width and scaled_height >= output_height:
                    valid_scale = True
                retries += 1

            if not valid_scale:
                print(
                    f"Failed to find a valid scale factor for {input_path} after {max_retries} attempts."
                )
                return

            img = img.resize((scaled_width, scaled_height), Image.LANCZOS)

            # Determine how many tiles can fit in the scaled image
            tiles_across = scaled_width // output_width
            tiles_down = scaled_height // output_height

            if tiles_across > 0 and tiles_down > 0:
                tile_count = 0
                for i in range(tiles_down):
                    for j in range(tiles_across):
                        left = j * output_width
                        top = i * output_height
                        cropped_img = img.crop(
                            (left, top, left + output_width, top + output_height)
                        )
                        timestamp = int(time())
                        output_filename = f"{input_path.stem}_{timestamp}_{tile_count}{input_path.suffix}"
                        output_path = output_dir / output_filename
                        cropped_img.save(output_path, format="PNG")
                        tile_count += 1
                        print(f"Processed and saved: {output_path}")
            else:
                # If no tiles can fit, fallback to a single random crop
                left = random.randint(0, scaled_width - output_width)
                top = random.randint(0, scaled_height - output_height)
                cropped_img = img.crop(
                    (left, top, left + output_width, top + output_height)
                )
                timestamp = int(time())
                output_filename = f"{input_path.stem}_{timestamp}{input_path.suffix}"
                output_path = output_dir / output_filename
                cropped_img.save(output_path)
                print(f"Processed and saved: {output_path}")

    elif input_path.is_dir():
        for image_path in input_path.rglob("*"):
            if image_path.suffix.lower() in image_extensions:
                process_image(
                    image_path,
                    output_dir,
                    scale_min,
                    scale_max,
                    output_width,
                    output_height,
                    max_retries,
                )
    else:
        print(
            f"The path {input_path} is neither a supported image file nor a directory."
        )


def main():
    parser = argparse.ArgumentParser(description="Process images for AI training.")
    parser.add_argument(
        "input_path", type=str, help="Path to an image file or a directory."
    )
    parser.add_argument(
        "output_dir", type=str, help="Directory to save processed images."
    )
    parser.add_argument(
        "--scale-min",
        type=float,
        default=0.01,
        help="Minimum scaling factor (default: 0.2).",
    )
    parser.add_argument(
        "--scale-max",
        type=float,
        default=1.0,
        help="Maximum scaling factor (default: 1.0).",
    )
    parser.add_argument(
        "--output-width",
        type=int,
        default=512,
        help="Width of the output image (default: 512).",
    )
    parser.add_argument(
        "--output-height",
        type=int,
        default=512,
        help="Height of the output image (default: 512).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=100,
        help="Maximum number of retries to find a valid scale factor (default: 10).",
    )
    args = parser.parse_args()

    process_image(
        args.input_path,
        args.output_dir,
        args.scale_min,
        args.scale_max,
        args.output_width,
        args.output_height,
        args.max_retries,
    )


if __name__ == "__main__":
    main()
