import httpx
import os
from pathlib import Path
from siphon_api.audio import DiarizationResponse
import logging

# Set up logging
log_level = int(os.getenv("PYTHON_LOG_LEVEL", "3"))
levels = {1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
logging.basicConfig(
    level=levels.get(log_level, logging.INFO), format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Get the worker URL from the environment variable set in docker-compose.yml
DIARIZATION_SERVICE_URL = "http://localhost:8000"

# --- Your existing transcribe() and combine() functions ---
# ... (they don't need to change) ...
# ... (your preprocess_audio() also stays the same) ...


def call_diarization(wav_file: Path) -> DiarizationResponse:
    """
    Calls the isolated diarization service via HTTP.

    This function replaces the direct pyannote call.
    """
    if not wav_file.exists():
        raise FileNotFoundError(f"Audio file not found: {wav_file}")

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

            # 4. This is the magic: parse the JSON response
            # directly into our Pydantic object.
            return DiarizationResponse(**response.json())

    except httpx.RequestError as e:
        raise RuntimeError(f"Failed to connect to diarization service: {e}")
    except httpx.HTTPStatusError as e:
        # The worker returned a 500 error
        raise RuntimeError(f"Diarization service failed: {e.response.text}")


def process_audio(mp3_file: Path) -> list[dict]:
    """
    Complete pipeline: MP3 -> Preprocess -> Transcribe + Diarize -> Combine
    """
    logger.info(f"Processing audio file: {mp3_file}")
    # 1. Convert MP3 to WAV (local)
    wav_file = preprocess_audio(mp3_file)

    # 2. Transcribe (GPU, local)
    transcript = transcribe(str(mp3_file))

    # 3. Diarize (CPU, Docker via HTTP)
    # This call is now a network request.
    diarization_result = call_diarization(wav_file)

    # 4. Combine (local)
    # This works because diarization_result has .itertracks()!
    annotated = combine(diarization_result, transcript)

    # 5. Clean up temp WAV file
    wav_file.unlink()

    return annotated


if __name__ == "__main__":
    from siphon_server.sources.audio.example import EXAMPLE_WAV

    diarization_result = call_diarization(EXAMPLE_WAV)
