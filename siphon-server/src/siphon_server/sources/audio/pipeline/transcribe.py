from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

TRANSCRIPTION_SERVICE_URL = "http://172.16.0.2:9090"

# whisper.cpp works reliably with chunks up to ~30 minutes.
# Files longer than this risk "failed to decode/encode" errors.
CHUNK_DURATION_SEC = 30 * 60  # 30 minutes


def _get_wav_duration_sec(wav_path: Path) -> float:
    """Get WAV duration in seconds using ffprobe."""
    ffprobe = shutil.which("ffprobe") or "/usr/bin/ffprobe"
    result = subprocess.run(
        [
            ffprobe,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(wav_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def _split_wav(wav_path: Path, chunk_duration_sec: int) -> list[Path]:
    """Split a WAV file into chunks of chunk_duration_sec seconds.

    Returns a list of temporary WAV file paths. Caller is responsible for cleanup.
    """
    ffmpeg = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
    duration = _get_wav_duration_sec(wav_path)
    chunks = []
    start = 0.0

    while start < duration:
        chunk = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        chunk.close()
        subprocess.run(
            [
                ffmpeg,
                "-i", str(wav_path),
                "-ss", str(start),
                "-t", str(chunk_duration_sec),
                "-ar", "16000",
                "-ac", "1",
                "-y",
                chunk.name,
            ],
            capture_output=True,
            check=True,
        )
        chunks.append(Path(chunk.name))
        start += chunk_duration_sec
        logger.debug(f"[TRANSCRIBE] Created chunk: {chunk.name} (start={start - chunk_duration_sec:.1f}s)")

    return chunks


def _transcribe_chunk(wav_file: Path) -> list[dict]:
    """Send a single WAV chunk to the whisper service and return segments."""
    with open(wav_file, "rb") as f:
        files_payload = {
            "file": (wav_file.name, f, "audio/wav"),
            "response_format": ("", "verbose_json"),
        }
        with httpx.Client(timeout=1200.0) as client:
            response = client.post(
                f"{TRANSCRIPTION_SERVICE_URL}/inference", files=files_payload
            )
    response.raise_for_status()
    return response.json()["segments"]


def _merge_segments(all_segments: list[list[dict]], chunk_duration_sec: int) -> list[dict]:
    """Merge segments from multiple chunks, adjusting timestamps."""
    merged = []
    for i, segments in enumerate(all_segments):
        offset = i * chunk_duration_sec
        for seg in segments:
            merged.append({
                "text": seg["text"],
                "start": seg["start"] + offset,
                "end": seg["end"] + offset,
            })
    return merged


def transcribe(wav_file: Path) -> list[dict]:
    """
    Transcribe audio via the external whisper service.

    For long files (>30 min), splits into chunks to avoid whisper.cpp
    decode/encode failures on massive inputs.

    Returns a normalized list of chunks: [{text: str, start: float, end: float}]
    """
    if not wav_file.exists():
        raise FileNotFoundError(f"Audio file not found: {wav_file}")
    logger.debug(f"[TRANSCRIBE] Calling whisper service for: {wav_file}")

    try:
        duration = _get_wav_duration_sec(wav_file)
        logger.info(f"[TRANSCRIBE] Audio duration: {duration:.1f}s ({duration / 60:.1f} min)")

        if duration <= CHUNK_DURATION_SEC:
            # Short file — send directly
            logger.debug("[TRANSCRIBE] Short file, sending directly to whisper")
            segments = _transcribe_chunk(wav_file)
            return segments

        # Long file — split into chunks
        logger.info(f"[TRANSCRIBE] Splitting into {duration / CHUNK_DURATION_SEC:.0f} chunks of {CHUNK_DURATION_SEC}s each")
        chunk_paths = _split_wav(wav_file, CHUNK_DURATION_SEC)
        try:
            all_segments = []
            for i, chunk_path in enumerate(chunk_paths):
                logger.info(f"[TRANSCRIBE] Transcribing chunk {i + 1}/{len(chunk_paths)}: {chunk_path.name}")
                segments = _transcribe_chunk(chunk_path)
                all_segments.append(segments)
                logger.info(f"[TRANSCRIBE] Chunk {i + 1} done: {len(segments)} segments")

            merged = _merge_segments(all_segments, CHUNK_DURATION_SEC)
            logger.info(f"[TRANSCRIBE] Merged {len(merged)} total segments")
            return merged
        finally:
            # Clean up temp chunk files
            for chunk_path in chunk_paths:
                chunk_path.unlink(missing_ok=True)
                logger.debug(f"[TRANSCRIBE] Cleaned up chunk: {chunk_path}")

    except httpx.RequestError as e:
        raise RuntimeError(f"Failed to connect to whisper service: {e}")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Whisper service failed: {e.response.text}")
