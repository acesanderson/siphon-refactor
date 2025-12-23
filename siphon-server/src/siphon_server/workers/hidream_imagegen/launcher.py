import subprocess
import time
import httpx
import logging
from contextlib import contextmanager
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent.resolve()
HEALTH_CHECK_URL = "http://localhost:8003/health"
MAX_WAIT_SEC = 450  # HiDream is 17B params; give it time to load


@contextmanager
def manage_hidream_sidecar():
    if not (SCRIPT_DIR / "docker-compose.yml").exists():
        raise FileNotFoundError(f"docker-compose.yml not found in {SCRIPT_DIR}")

    logger.info("Starting HiDream sidecar...")
    subprocess.run(
        ["docker-compose", "up", "--build", "-d"],
        cwd=SCRIPT_DIR,
        check=True,
        capture_output=True,
    )

    try:
        start_time = time.time()
        is_healthy = False
        with httpx.Client(timeout=2.0) as client:
            while time.time() - start_time < MAX_WAIT_SEC:
                try:
                    if client.get(HEALTH_CHECK_URL).status_code == 200:
                        logger.info("HiDream Sidecar is healthy.")
                        is_healthy = True
                        break
                except httpx.ConnectError:
                    pass
                time.sleep(2)

        if not is_healthy:
            raise TimeoutError("HiDream failed to start.")
        yield
    finally:
        logger.info("Shutting down HiDream sidecar...")
        subprocess.run(
            ["docker-compose", "down"], cwd=SCRIPT_DIR, check=True, capture_output=True
        )
