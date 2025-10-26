from siphon.ingestion.youtube.download_youtube_transcript import (
    download_youtube_transcript,
)
# from siphon.ingestion.youtube.format_youtube import format_youtube


def retrieve_youtube(url: str) -> tuple[str, dict]:
    """
    Retrieve the YouTube transcript from a given URL.
    Returns a tuple containing the formatted transcript and a metadata dict.
    """
    transcript, metadata = download_youtube_transcript(url)
    if not transcript:
        raise ValueError(f"No transcript found for URL: {url}")
    # formatted_transcript = format_youtube(transcript)
    return transcript, metadata
