"""
Audio preprocessing utility for normalizing diverse audio formats into WAV for downstream processing.

This module provides a context manager that abstracts away audio format conversion complexity within the Siphon audio pipeline. The `guaranteed_wav_path()` function accepts any supported audio format (MP3, OGG, M4A, FLAC, or WAV) and guarantees a valid WAV file path for consumption by transcription and diarization components. For native WAV files, it yields the original path with no conversion overhead; for other formats, it transparently converts to a temporary WAV file via pydub's AudioSegment and automatically cleans up on context exit.

This design isolates format handling concerns from higher-level audio processing logic, allowing transcription and diarization modules to assume WAV input without conditional branching. The temporary file lifecycle is managed safely through context manager semantics and OS-level file deletion, preventing resource leaks in batch processing scenarios.

Usage:
```python
from pathlib import Path
from siphon_server.sources.audio.preprocess import guaranteed_wav_path

with guaranteed_wav_path(Path("podcast.mp3")) as wav_path:
    transcript = transcribe(wav_path)  # Guaranteed to receive valid WAV path
    # Temp file automatically deleted when exiting context
```
"""

from pathlib import Path
from siphon_api.file_types import EXTENSIONS
import tempfile
from contextlib import contextmanager
from pathlib import Path
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)


@contextmanager
def guaranteed_wav_path(input_path: Path):
    """
    Context manager to guarantee a file path to a WAV file.

    If the input_path is already a .wav, it yields the original path
    and performs no cleanup.

    If the input_path is another format (mp3, ogg, m4a, flac), it
    converts it to a temporary WAV file, yields the path to that
    temp file, and automatically deletes the temp file upon exit.
    """
    suffix = input_path.suffix.lower()
    if suffix not in EXTENSIONS["Audio"]:
        raise ValueError(f"Unsupported audio format: {suffix}")
    elif input_path.suffix.lower() == ".wav":
        logging.debug(f"[PREPROCESS] Input is already a WAV: {input_path}")
        try:
            yield input_path
        finally:
            logger.debug("[PREPROCESS] No cleanup required for original WAV.")
    else:
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=True)
            logger.debug(
                f"[PREPROCESS] Converting {input_path} to temp WAV: {temp_file.name}"
            )

            # Load and export the audio
            audio = AudioSegment.from_file(input_path, format=input_path.suffix[1:])
            audio.export(temp_file.name, format="wav")

            # Yield the path to the newly created temp file
            yield Path(temp_file.name)

        finally:
            if temp_file:
                # Closing the file handle triggers the OS to delete it.
                temp_file.close()
                logger.debug(f"[PREPROCESS] Temp WAV file deleted: {temp_file.name}")
