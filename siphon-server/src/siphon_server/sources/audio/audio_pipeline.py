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
    diarization_result = diarize(wav_file)

    # 4. Combine (local)
    # This works because diarization_result has .itertracks()!
    annotated = combine(diarization_result, transcript)

    # 5. Clean up temp WAV file
    wav_file.unlink()

    return annotated
