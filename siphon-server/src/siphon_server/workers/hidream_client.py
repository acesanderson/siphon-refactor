import os
import argparse
import logging
import httpx
from pathlib import Path
from jinja2 import Template

NAS_DIR = os.getenv("NAS", "/tmp")
IMAGES_DIR_PATH = Path(NAS_DIR).resolve() / "generated_images"
IMAGES_DIR_PATH.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
HIDREAM_SERVICE_URL = "http://localhost:8003"

TRMNL_PROMPT = """
SYSTEM PROMPT FOR E-INK–OPTIMIZED IMAGE GENERATION
... [Same rules as your previous files] ...
Now here is the user prompt:
<PROMPT>
{{ prompt }}
</PROMPT>
"""


def generate_hidream(
    prompt: str,
    output_file: Path,
    steps: int = 28,
    guidance: float = 0.0,
    seed: int = 42,
) -> Path:
    payload = {"prompt": prompt, "steps": steps, "guidance": guidance, "seed": seed}

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(f"{HIDREAM_SERVICE_URL}/generate", json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"HiDream error: {response.text}")

            with open(output_file, "wb") as f:
                f.write(response.content)
            return output_file
    except Exception as e:
        raise RuntimeError(f"Generation failed: {e}")


def stem_prompt(prompt: str) -> str:
    import re

    return re.sub(r"[^a-z0-9_]", "", prompt.lower().replace(" ", "_"))[:50]


def generate_raw_hidream(prompt: str) -> Path:
    return generate_hidream(prompt, IMAGES_DIR_PATH / f"hd_{stem_prompt(prompt)}.png")


def generate_trmnl_hidream(prompt: str) -> Path:
    full_prompt = str(Template(TRMNL_PROMPT).render(prompt=prompt))
    return generate_hidream(
        full_prompt, IMAGES_DIR_PATH / f"hd_trmnl_{stem_prompt(prompt)}.png"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--trmnl", "-t", action="store_true")
    args = parser.parse_args()

    path = (
        generate_trmnl_hidream(args.prompt)
        if args.trmnl
        else generate_raw_hidream(args.prompt)
    )
    print(f"Generated at: {path}")


if __name__ == "__main__":
    main()
