"""
HTTP client for speaker diarization processing via an isolated microservice.

This module provides a thin wrapper around HTTP calls to a containerized speaker diarization worker,
replacing direct local pyannote invocations with network-based requests. The `call_diarization` function
accepts a WAV audio file, uploads it to the diarization service endpoint, and deserializes the JSON
response directly into a `DiarizationResponse` Pydantic model with speaker segment information.

The script is integrated into the audio processing pipeline where it handles speaker identification
as a decoupled CPU-bound service. By routing diarization requests to an isolated Docker container
(managed by the launcher module), the main GPU pipeline remains responsive while expensive speaker
detection computation runs asynchronously. Error handling includes timeout management for long-running
ML tasks and detailed exception translation for connection and service failures.
"""

from pathlib import Path
from siphon_api.audio import DiarizationResponse
import httpx
import logging

logger = logging.getLogger(__name__)

DIARIZATION_SERVICE_URL = "http://localhost:8000"


def diarize(wav_file: Path) -> DiarizationResponse:
    """
    Calls the isolated diarization service via HTTP.
    """
    if not wav_file.exists():
        raise FileNotFoundError(f"Audio file not found: {wav_file}")
    logger.debug(f"[DIARIZE] Calling diarization service for file: {wav_file}")

    try:
        # 1. Open the file to be uploaded
        with open(wav_file, "rb") as f:
            files_payload = {"file": (wav_file.name, f, "audio/wav")}

            # 2. Use httpx to make the request
            # We set a long timeout, as this ML task can take time.
            with httpx.Client(timeout=300.0) as client:
                response = client.post(
                    f"{DIARIZATION_SERVICE_URL}/process", files=files_payload
                )

            # 3. Check for errors from the worker
            response.raise_for_status()

            logger.debug(f"[DIARIZE] Received response: {response.text}")

            return DiarizationResponse(**response.json())

    except httpx.RequestError as e:
        raise RuntimeError(f"Failed to connect to diarization service: {e}")
    except httpx.HTTPStatusError as e:
        # The worker returned a 500 error
        raise RuntimeError(f"Diarization service failed: {e.response.text}")
