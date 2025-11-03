"""
Models for diarization sidecar.
"""

from pydantic import BaseModel


class DiarizationSegment(BaseModel):
    """
    A Pydantic model for a single speaker segment.
    """

    start: float
    end: float
    speaker: str


class DiarizationResponse(BaseModel):
    """
    The standardized response model our worker will send.
    """

    segments: list[DiarizationSegment]

    def itertracks(self, yield_label: bool = True):
        """
        This is an 'adapter method'. It gives this Pydantic model
        the same .itertracks() interface that the original
        'pyannote' object has.

        This lets us slot our new API client directly into our
        existing code with zero changes to the logic.
        """

        # A simple mock class to match the 'turn' object's interface
        class MockSegment:
            def __init__(self, start, end):
                self.start = start
                self.end = end

        if not yield_label:
            for seg in self.segments:
                yield MockSegment(seg.start, seg.end)
            return

        for seg in self.segments:
            # Yields in the format: (segment, _, speaker)
            yield (MockSegment(seg.start, seg.end), None, seg.speaker)
