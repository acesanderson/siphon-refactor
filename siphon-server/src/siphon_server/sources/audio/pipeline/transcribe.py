from __future__ import annotations

import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

TRANSCRIPTION_SERVICE_URL = "http://172.16.0.2:9090"


def transcribe(wav_file: Path) -> list[dict]:
    """
    Transcribe audio via the external whisper service.

    Returns a normalized list of chunks: [{text: str, start: float, end: float}]
    """
    if not wav_file.exists():
        raise FileNotFoundError(f"Audio file not found: {wav_file}")
    logger.debug(f"[TRANSCRIBE] Calling whisper service for: {wav_file}")

    try:
        with open(wav_file, "rb") as f:
            files_payload = {
                "file": (wav_file.name, f, "audio/wav"),
                "response_format": ("", "verbose_json"),
            }
            with httpx.Client(timeout=600.0) as client:
                response = client.post(
                    f"{TRANSCRIPTION_SERVICE_URL}/inference", files=files_payload
                )
        response.raise_for_status()
        data = response.json()
        return data["segments"]
    except httpx.RequestError as e:
        raise RuntimeError(f"Failed to connect to whisper service: {e}")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Whisper service failed: {e.response.text}")
