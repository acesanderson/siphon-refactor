import subprocess
import time
import httpx
import logging
from contextlib import contextmanager
from pathlib import Path
import os

# Set up logging
log_level = int(os.getenv("PYTHON_LOG_LEVEL", "2"))
levels = {1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
logging.basicConfig(
    level=levels.get(log_level, logging.INFO), format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
SCRIPT_DIR = Path(__file__).parent.resolve()
SIDECAR_DIR = SCRIPT_DIR
# IMPORTANT: Distinct port from Flux (8001) and Diarization (8000)
HEALTH_CHECK_URL = "http://localhost:8002/health"
POLL_INTERVAL_SEC = 2
MAX_WAIT_SEC = 300


@contextmanager
def manage_zimage_sidecar():
    if not SIDECAR_DIR.exists() or not (SIDECAR_DIR / "docker-compose.yml").exists():
        logger.error(f"docker-compose.yml not found in {SIDECAR_DIR}")
        raise FileNotFoundError(f"Sidecar directory not found: {SIDECAR_DIR}")

    logger.info(f"Using docker-compose from directory: {SIDECAR_DIR}")

    logger.info("Starting Z-Image sidecar (detached mode)...")
    start_command = ["docker-compose", "up", "--build", "-d"]

    try:
        subprocess.run(
            start_command,
            cwd=SIDECAR_DIR,
            check=True,
            capture_output=True,
        )

        logger.info("Waiting for sidecar to become healthy...")
        start_time = time.time()
        is_healthy = False

        with httpx.Client(timeout=POLL_INTERVAL_SEC) as client:
            while time.time() - start_time < MAX_WAIT_SEC:
                try:
                    response = client.get(HEALTH_CHECK_URL)
                    if response.status_code == 200:
                        logger.info("Z-Image Sidecar is healthy and ready.")
                        is_healthy = True
                        break
                    else:
                        logger.warning(f"Health check status: {response.status_code}")
                except httpx.ConnectError:
                    logger.info("Waiting for sidecar connection...")
                except Exception as e:
                    logger.warning(f"Health check error: {e}")

                time.sleep(POLL_INTERVAL_SEC)

        if not is_healthy:
            raise TimeoutError(
                f"Sidecar failed to start within {MAX_WAIT_SEC} seconds."
            )

        yield

    finally:
        logger.info("Shutting down Z-Image sidecar...")
        stop_command = ["docker-compose", "down"]
        _ = subprocess.run(
            stop_command, cwd=SIDECAR_DIR, check=True, capture_output=True
        )
        logger.info("Sidecar stopped.")
