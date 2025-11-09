from pathlib import Path
from transformers import pipeline
import torch
import logging

logger = logging.getLogger(__name__)


# Transcript workflow
def transcribe(file_name: str | Path) -> str:
    """
    Use Whisper to retrieve text content + timestamps.
    """
    # Constrain Path to str
    file_name = str(file_name)
    # Initialize the transcription pipeline
    transcriber = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-base",
        # model="openai/whisper-large-v3",
        return_timestamps="sentence",
        device=0,
        torch_dtype=torch.float16,
    )
    logger.info(f"Transcribing file: {file_name}")
    result = transcriber(file_name)
    return result


if __name__ == "__main__":
    from siphon_server.sources.audio.example import EXAMPLE_WAV

    transcript = transcribe(EXAMPLE_WAV)
    print("Transcription Result:")
    print(transcript)
