from pathlib import Path
import httpx
import logging
from jinja2 import Template
import os
import argparse

# [Keep your NAS_DIR and logging setup same as before]
NAS_DIR = os.getenv("NAS", "/tmp")  # Default for safety
NAS_DIR_PATH = Path(NAS_DIR).resolve()
IMAGES_DIR_PATH = NAS_DIR_PATH / "generated_images"
IMAGES_DIR_PATH.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

# [Keep your existing E-INK system_prompt]
trmnl_prompt = """
SYSTEM PROMPT FOR E-INK–OPTIMIZED IMAGE GENERATION

You are generating images intended for a low-power 800×480 monochrome e-ink display. The display renders only black or white pixels after thresholding, with no grayscale. Your outputs must be optimized to survive 1-bit conversion and dithering without becoming muddy, dark, or losing structure.

Follow these rules:
- Brightness & Tonal Range
- Avoid low-key or dark images.
- Maximize mid-tone and light regions so that major forms remain distinct when converted to pure black & white.
- Avoid strong global darkening or moody lighting.

Contrast & Edge Clarity

- Emphasize clear silhouettes, crisp edges, and well-defined shapes.
- Preserve detail using line-friendly structure rather than noise or texture.
- Avoid heavy shadows and large dense black areas.

Texture & Shading
- Do not use photographic noise, grain, film look, or fine gradients.
- Prefer flat lighting, soft shading, and large regions of clean tone.
- Avoid tiny high-frequency textures that will turn to dithering speckles.

Composition
- Keep the subject uncluttered with intentional negative space.
- Avoid busy backgrounds, fog effects, smoke, or visual clutter.
- Ensure strong figure-ground separation.

Style
- Prefer illustration-like, poster-like, or simplified semi-realistic styles.
- Avoid hyperrealism and complex lighting simulations.
- Avoid deep shadows, backlighting, or high-contrast chiaroscuro.

Output requirements
- Final image should be visually interpretable at 800×480 and remain readable after 1-bit dithering.
- Avoid color-dependent cues; assume all hue information will be discarded.

Goal: Produce a bright, simplified, high-clarity image that retains structure when reduced to 1-bit black and white on an 800×480 e-ink screen.

Now here is the user prompt to generate the image for the e-ink display:
<PROMPT>
{{ prompt }}
</PROMPT>
"""


# Port 8002
ZIMAGE_SERVICE_URL = "http://localhost:8002"


def generate_zimage(
    prompt: str,
    output_file: Path,
    height: int = 1024,
    width: int = 1024,
    steps: int = 9,  # Z-Image Turbo default
    guidance: float = 0.0,  # Z-Image Turbo requirement
    seed: int | None = 42,
) -> Path:
    if not output_file.parent.exists():
        output_file.parent.mkdir(parents=True, exist_ok=True)

    logger.debug(f"[Z-IMAGE] Requesting: '{prompt[:50]}...'")

    payload = {
        "prompt": prompt,
        "height": height,
        "width": width,
        "steps": steps,
        "guidance": guidance,
        "seed": seed,
    }

    try:
        # Timeout can be shorter (60s) because Turbo is incredibly fast
        with httpx.Client(timeout=60.0) as client:
            response = client.post(f"{ZIMAGE_SERVICE_URL}/generate", json=payload)

            if response.status_code != 200:
                raise RuntimeError(f"Z-Image error: {response.text}")

            with open(output_file, "wb") as f:
                f.write(response.content)

            return output_file

    except httpx.ConnectError:
        raise RuntimeError(f"Failed to connect to {ZIMAGE_SERVICE_URL}")
    except Exception as e:
        raise RuntimeError(f"Error during generation: {e}")


def stem_the_prompt_for_filename(prompt: str) -> str:
    """
    Creates a filesystem-safe stem from the prompt for use in filenames.

    Args:
        prompt: The text description for the image.

    Returns:
        str: A sanitized string suitable for filenames.
    """
    import re

    # Lowercase and replace spaces with underscores
    stem = prompt.lower().replace(" ", "_")
    # Remove non-alphanumeric characters except underscores
    stem = re.sub(r"[^a-z0-9_]", "", stem)
    # Truncate to a reasonable length
    return stem[:50]


def generate_raw_zimage(prompt: str) -> Path:
    output_path = IMAGES_DIR_PATH / f"{stem_the_prompt_for_filename(prompt)}.png"
    result_path = generate_zimage(prompt, output_path)
    return result_path


def generate_trmnl_image(prompt: str) -> Path:
    output_path = IMAGES_DIR_PATH / f"{stem_the_prompt_for_filename(prompt)}.png"
    complete_prompt = str(Template(trmnl_prompt).render(prompt=prompt))
    result_path = generate_zimage(complete_prompt, output_path)
    return result_path


def main():
    parser = argparse.ArgumentParser(description="Generate images using Z-Image Turbo.")
    parser.add_argument(
        "prompt", type=str, help="The text prompt for image generation."
    )
    parser.add_argument(
        "--trmnl",
        "-t",
        action="store_true",
        help="Use the TRMNL prompt template.",
    )
    args = parser.parse_args()
    if args.trmnl:
        prompt = args.prompt
        path = generate_trmnl_image(prompt)
        print(f"Generated image at: {path}")
    else:
        prompt = args.prompt
        path = generate_raw_zimage(prompt)
        print(f"Generated image at: {path}")


if __name__ == "__main__":
    main()
