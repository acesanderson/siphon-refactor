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
    hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not hf_token:
        raise ValueError("HUGGINGFACEHUB_API_TOKEN not set in worker")

    torch.set_num_threads(8)

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1", use_auth_token=hf_token
    )

    diarization_result = pipeline(str(audio_file))
    return diarization_result
