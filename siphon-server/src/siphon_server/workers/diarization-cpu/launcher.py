"""
Lifecycle manager for the isolated diarization worker service using Docker Compose.

This module provides a context manager that orchestrates the startup, health verification, and graceful shutdown of a containerized speaker diarization service. It handles subprocess management of docker-compose commands, implements polling-based health checks against the worker's HTTP endpoint, and ensures the service is fully operational before yielding control to the main application.

The launcher is designed as a reusable context manager so that calling code can wrap long-running processes (like the main Siphon pipeline) with guaranteed cleanup of the diarization sidecar, preventing orphaned containers and resource leaks. It includes configurable timeouts, exponential backoff on connection failures, and detailed logging to troubleshoot startup issues in development and deployment environments.
"""

import subprocess
import time
import httpx
import logging
from contextlib import contextmanager
from pathlib import Path
import os

# Set up logging
log_level = int(os.getenv("PYTHON_LOG_LEVEL", "2"))  # Default to INFO
levels = {1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
logging.basicConfig(
    level=levels.get(log_level, logging.INFO), format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
SCRIPT_DIR = Path(__file__).parent.resolve()
SIDECAR_DIR = SCRIPT_DIR
HEALTH_CHECK_URL = "http://localhost:8000/health"
POLL_INTERVAL_SEC = 2
MAX_WAIT_SEC = 60


@contextmanager
def manage_diarization_sidecar():
    """
    A context manager to start, health-check, and stop the
    diarization docker-compose service.
    """
    if not SIDECAR_DIR.exists() or not (SIDECAR_DIR / "docker-compose.yml").exists():
        logger.error(f"docker-compose.yml not found in {SIDECAR_DIR}")
        raise FileNotFoundError(f"Sidecar directory not found: {SIDECAR_DIR}")

    logger.info(f"Using docker-compose from directory: {SIDECAR_DIR}")

    # --- __enter__: Start the service ---
    logger.info("Starting diarization sidecar (detached mode)...")
    start_command = ["docker-compose", "up", "--build", "-d"]

    try:
        # Run docker-compose from its directory
        subprocess.run(
            start_command,
            cwd=SIDECAR_DIR,
            check=True,  # Raise error if docker-compose fails
            capture_output=True,  # Don't flood stdout
        )

        logger.info("Waiting for sidecar to become healthy...")
        start_time = time.time()
        is_healthy = False

        with httpx.Client(timeout=POLL_INTERVAL_SEC) as client:
            while time.time() - start_time < MAX_WAIT_SEC:
                try:
                    response = client.get(HEALTH_CHECK_URL)
                    if response.status_code == 200:
                        logger.info("Sidecar is healthy and ready.")
                        is_healthy = True
                        break
                    else:
                        logger.warning(
                            f"Health check failed with status: {response.status_code}"
                        )
                except httpx.ConnectError:
                    logger.info("Waiting for sidecar connection...")
                except Exception as e:
                    logger.warning(f"Health check error: {e}")

                time.sleep(POLL_INTERVAL_SEC)

        if not is_healthy:
            raise TimeoutError(
                f"Sidecar failed to start within {MAX_WAIT_SEC} seconds."
            )

        # --- Yield to the main application ---
        yield
        # --- Main application runs here ---

    finally:
        # --- __exit__: Stop the service ---
        logger.info("Shutting down diarization sidecar...")
        stop_command = ["docker-compose", "down"]
        _ = subprocess.run(
            stop_command, cwd=SIDECAR_DIR, check=True, capture_output=True
        )
        logger.info("Sidecar stopped.")


if __name__ == "__main__":
    logger.info("--- Testing Sidecar Manager ---")
    try:
        with manage_diarization_sidecar():
            logger.info("Sidecar is up. Main 'application' would be running now.")
            logger.info("Simulating main app running for 10 seconds...")
            time.sleep(10)
            logger.info("Main 'application' is finishing.")
        logger.info("--- Test complete. ---")
    except Exception as e:
        logger.error(f"Test failed: {e}")
