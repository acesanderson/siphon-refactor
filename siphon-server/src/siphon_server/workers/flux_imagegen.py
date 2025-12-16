"""
HTTP client for FLUX.2 image generation via an isolated microservice.

This module provides a thin wrapper around HTTP calls to a containerized image generation worker,
offloading VRAM-intensive diffusion tasks to a dedicated GPU environment. The `generate_image` function
accepts a text prompt and generation parameters, transmits them to the Flux service endpoint,
and streams the resulting binary PNG data directly to a specified output path.

The script is integrated into the media processing pipeline to handle visual asset creation
as a decoupled GPU-bound service. By routing generation requests to an isolated Docker container
(managed by the launcher module), the main application avoids direct dependency conflicts
with the complex PyTorch/CUDA stack required for the Blackwell architecture.
Error handling includes extended timeout management for diffusion inference and strict
verification of service health.
"""

from pathlib import Path
import httpx
import logging

logger = logging.getLogger(__name__)

# Note: Port 8001 to avoid conflict with the Diarization service (8000)
FLUX_SERVICE_URL = "http://localhost:8001"


def generate_image(
    prompt: str,
    output_file: Path,
    height: int = 1024,
    width: int = 1024,
    steps: int = 40,
    guidance: float = 3.5,
    seed: int | None = 42,
) -> Path:
    """
    Calls the isolated Flux service to generate an image from a prompt.

    Args:
        prompt: The text description for the image.
        output_file: The Path where the resulting PNG should be saved.
        height: Image height in pixels (default 1024).
        width: Image width in pixels (default 1024).
        steps: Inference steps (default 40). Higher = more detail/time.
        guidance: Guidance scale (default 3.5, max 5.0). Higher = more prompt adherence.
        seed: Random seed for reproducibility.

    Returns:
        Path: The absolute path to the saved image file.
    """
    # Ensure output directory exists
    if not output_file.parent.exists():
        output_file.parent.mkdir(parents=True, exist_ok=True)

    logger.debug(
        f"[FLUX] Requesting generation for: '{prompt[:50]}...' -> {output_file}"
    )

    payload = {
        "prompt": prompt,
        "height": height,
        "width": width,
        "steps": steps,
        "guidance": guidance,
        "seed": seed,
    }

    try:
        # We use a significant timeout (300s) because 30B parameter models
        # can take 30-60s to generate an image depending on settings.
        with httpx.Client(timeout=300.0) as client:
            response = client.post(f"{FLUX_SERVICE_URL}/generate", json=payload)

            # 1. Check for errors from the worker (e.g., OOM, 500s)
            if response.status_code != 200:
                # Try to parse detail if available, else use text
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text

                raise RuntimeError(
                    f"Flux service error ({response.status_code}): {error_detail}"
                )

            # 2. Write the binary image content to disk
            # Using binary write mode since we receive raw PNG bytes
            with open(output_file, "wb") as f:
                f.write(response.content)

            logger.info(
                f"[FLUX] Image successfully saved to {output_file} ({len(response.content)} bytes)"
            )
            return output_file

    except httpx.ConnectError:
        raise RuntimeError(
            f"Failed to connect to Flux service at {FLUX_SERVICE_URL}. "
            "Is the 'flux-sidecar' container running?"
        )
    except httpx.TimeoutException:
        raise RuntimeError(
            "Flux service timed out. The model might be reloading or the GPU is overloaded."
        )
    except Exception as e:
        raise RuntimeError(f"Unexpected error during image generation: {e}")


if __name__ == "__main__":
    prompt = "a black and white woodcut in the style of albrecht durer"
    output_path = Path("output/test_flux_image.png")
    result_path = generate_image(prompt, output_path)
    print(f"Image generated at: {result_path}")
