import os
import torch
from pathlib import Path
from pyannote.audio import Pipeline
from pyannote.core import Annotation


def run_diarization(audio_file: Path) -> Annotation:
    """
    Perform speaker diarization on the given audio file.
    This is the pure, isolated logic.
    """
    torch.set_num_threads(8)

    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    assert hf_token is not None, (
        "HUGGINGFACEHUB_API_TOKEN environment variable is not set."
    )

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token,
    )

    diarization_result = pipeline(str(audio_file))
    return diarization_result
