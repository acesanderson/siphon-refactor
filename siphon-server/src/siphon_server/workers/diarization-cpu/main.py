from fastapi import FastAPI, UploadFile, HTTPException, File
import tempfile
import os
from pathlib import Path


# Import the core logic
from diarize import run_diarization

# For this demo, we'll redefine the Pydantic models.
# In a real project, you'd install your 'siphon-api'
# package inside the Docker container.
from pydantic import BaseModel


class DiarizationSegment(BaseModel):
    start: float
    end: float
    speaker: str


class DiarizationResponse(BaseModel):
    segments: list[DiarizationSegment]


app = FastAPI(title="Diarization Worker")


@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "healthy", "service": "diarization"}


@app.post("/process", response_model=DiarizationResponse)
async def process_audio_file(file: UploadFile = File(...)):
    """
    This endpoint accepts a WAV file, processes it,
    and returns the speaker segments.
    """
    tmp_path = None
    try:
        # FastAPI's UploadFile must be saved to disk
        # for pyannote to read it.
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(await file.read())
            tmp_path = Path(tmp.name)

        # 2. Run the actual ML logic
        annotation = run_diarization(tmp_path)

        # 3. Convert the 'pyannote' object to our Pydantic model
        segments = []
        for turn, _, speaker in annotation.itertracks(yield_label=True):
            segments.append(
                DiarizationSegment(start=turn.start, end=turn.end, speaker=speaker)
            )
        return DiarizationResponse(segments=segments)

    except Exception as e:
        # Log the error
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 4. Clean up the temp file
        if tmp_path and tmp_path.exists():
            os.unlink(tmp_path)
