import argparse
import random
from pathlib import Path
from typing import Union
from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None

# Define scaling algorithms
SCALING_ALGORITHMS = {
    "down_up": Image.BICUBIC,
    "linear": Image.BILINEAR,
    "cubic_mitchell": Image.HAMMING,
    "lanczos": Image.LANCZOS,
    "gauss": Image.BOX,
    "box": Image.BOX,
}

# Define blur algorithms
BLUR_ALGORITHMS = {
    "average": ImageFilter.BLUR,
    "gaussian": ImageFilter.GaussianBlur,
    "anisotropic": ImageFilter.SMOOTH,
}


def add_random_noise(image: Image.Image, intensity: float) -> Image.Image:
    """Adds random noise to an image."""
    noise = Image.effect_noise(image.size, intensity)
    noise_image = Image.blend(image, noise, 0.5)
    return noise_image


def apply_random_blur(image: Image.Image, blur_type: str) -> Image.Image:
    """Applies random blur to an image."""
    if blur_type == "gaussian":
        radius = random.uniform(0.5, 2.0)  # Random Gaussian blur radius
        return image.filter(ImageFilter.GaussianBlur(radius))
    else:
        return image.filter(BLUR_ALGORITHMS[blur_type])


def process_image(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    scale: float,
    scaling_algo: str,
    blur: bool,
    blur_type: str,
    noise: bool,
    noise_intensity: float,
    save_as_jpeg: bool = False,
    jpeg_quality_range: tuple[int, int] = (75, 95),
) -> None:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"The path {input_path} does not exist.")
        return

    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

    if input_path.is_file() and input_path.suffix.lower() in image_extensions:
        print(f"Processing file: {input_path}")
        with Image.open(input_path) as img:
            # Apply scaling
            selected_scaling_algo = (
                scaling_algo
                if scaling_algo
                else random.choice(list(SCALING_ALGORITHMS.keys()))
            )
            scaled_width = int(img.width * scale)
            scaled_height = int(img.height * scale)
            img = img.resize(
                (scaled_width, scaled_height),
                SCALING_ALGORITHMS[selected_scaling_algo],
            )
            print(f"Applied scaling using {selected_scaling_algo} algorithm.")

            # Optionally apply blur
            if blur:
                selected_blur_type = (
                    blur_type
                    if blur_type
                    else random.choice(list(BLUR_ALGORITHMS.keys()))
                )
                img = apply_random_blur(img, selected_blur_type)
                print(f"Applied blur using {selected_blur_type} algorithm.")

            # Optionally add noise
            if noise:
                img = add_random_noise(img, noise_intensity)

            # Save the processed image
            if save_as_jpeg:
                # Convert to RGB mode if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")
                quality = random.randint(*jpeg_quality_range)
                output_path = output_dir / f"{input_path.stem}.jpg"
                img.save(output_path, format="JPEG", quality=quality)
                print(
                    f"Saved processed image as JPEG with quality {quality}: {output_path}"
                )
            else:
                output_path = output_dir / f"{input_path.stem}.png"
                img.save(output_path, format="PNG")
                print(f"Saved processed image to: {output_path}")

    elif input_path.is_dir():
        for image_path in input_path.rglob("*"):
            if image_path.suffix.lower() in image_extensions:
                process_image(
                    image_path,
                    output_dir,
                    scale,
                    scaling_algo,
                    blur,
                    blur_type,
                    noise,
                    noise_intensity,
                    save_as_jpeg,
                    jpeg_quality_range,
                )
    else:
        print(
            f"The path {input_path} is neither a supported image file nor a directory."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Process images with scaling, blur, noise, and format options."
    )
    parser.add_argument(
        "input_path", type=str, help="Path to an image file or a directory."
    )
    parser.add_argument(
        "output_dir", type=str, help="Directory to save processed images."
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=0.25,
        help="Scaling factor to resize images (default: 0.25).",
    )
    parser.add_argument(
        "--scaling-algo",
        type=str,
        choices=SCALING_ALGORITHMS.keys(),
        help="Algorithm to use for scaling. If not specified, one will be chosen randomly.",
    )
    parser.add_argument(
        "--blur",
        action="store_true",
        help="Apply random blur to the image (default: True).",
    )
    parser.add_argument(
        "--blur-type",
        type=str,
        choices=BLUR_ALGORITHMS.keys(),
        help="Type of blur to apply. If not specified, one will be chosen randomly.",
    )
    parser.add_argument(
        "--noise",
        action="store_true",
        help="Add random noise to the image.",
    )
    parser.add_argument(
        "--noise-intensity",
        type=float,
        default=10.0,
        help="Intensity of random noise to add (default: 10.0).",
    )
    parser.add_argument(
        "--save-as-jpeg",
        action="store_true",
        help="Save the processed image as JPEG instead of PNG.",
    )
    parser.add_argument(
        "--jpeg-quality-range",
        type=int,
        nargs=2,
        default=[75, 95],
        metavar=("MIN", "MAX"),
        help="Range of JPEG quality values (default: 75 95).",
    )
    args = parser.parse_args()

    process_image(
        args.input_path,
        args.output_dir,
        args.scale,
        args.scaling_algo,
        args.blur,
        args.blur_type,
        args.noise,
        args.noise_intensity,
        args.save_as_jpeg,
        tuple(args.jpeg_quality_range),
    )


if __name__ == "__main__":
    main()
