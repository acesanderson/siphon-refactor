"""
From module creator:

    *This code uses an undocumented part of the YouTube API, which is called by the YouTube web-client.
    So there is no guarantee that it won't stop working tomorrow, if they change how things work. I will
    however do my best to make things working again as soon as possible if that happens. So if it stops
    working, let me know!*

"""

from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import sys
import re
import logging

logger = logging.getLogger(__name__)

video_id = "5xb6uWLtCsI"
example = "https://www.youtube.com/watch?v=VctsqOo8wsc&t=628s"


def validate_video_id(input):
    """
    Validates that user has entered a valid YouTube Video ID, or a valid YouTube URL.
    """
    if re.match(r"^[a-zA-Z0-9_-]{11}$", input):
        return input
    elif re.match(
        r"^https?:\/\/(www\.)?youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})", input
    ):
        return re.match(
            r"^https?:\/\/(www\.)?youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})", input
        ).group(2)
    # also match for urls that have "live" instead of the standard "watch" https://www.youtube.com/live/OOdtmCMSOo4
    elif re.match(
        r"^https?:\/\/(www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})", input
    ):
        return re.match(
            r"^https?:\/\/(www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})", input
        ).group(2)
    else:
        raise ValueError("Invalid YouTube URL or Video ID")


def _download_youtube_transcript(self, video_id: str) -> str:
    """
    Feed this either a youtube link or a youtube video id, and it will return the transcript of the video.
    Returns a tuple of the transcript and metadata.
    """
    logger.info(f"Input video_id: {video_id}")
    logger.info(f"Validated video_id: {video_id}")
    logger.info(f"Type of video_id: {type(video_id)}")
    logger.info("Getting metadata from GitHub api...")
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(video_id, download=False)
        metadata = {
            # Online metadata (standard fields)
            "url": info.get("webpage_url"),
            "domain": "youtube.com",
            "title": info.get("title"),
            "published_date": info.get("upload_date")
            if info.get("upload_date")
            else None,
            # Youtube-specific
            "video_id": info.get("id"),
            "channel": info.get("channel"),
            "duration": info.get("duration"),
            "view_count": info.get("view_count"),
            "description": info.get("description"),
            "tags": info.get("tags"),
            "like_count": info.get("like_count"),
            "comment_count": info.get("comment_count"),
        }
    logger.info(f"Metadata: {metadata}")
    logger.info("Downloading transcript...")
    # this is the latest logic from the youtube-transcript-api package (v1.2.2)
    ytt_api = YouTubeTranscriptApi()
    fetched_transcript = ytt_api.fetch(video_id)
    t = fetched_transcript.to_raw_data()
    assert isinstance(t, list), "Transcript should be a list"
    script = " ".join([line["text"] for line in t])
    assert len(script) > 0, "Transcript should not be empty"
    return script, metadata


if __name__ == "__main__":
    video_id = "5xb6uWLtCsI"
    # video_id = "dQw4w9WgXcQ"
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    print(download_youtube_transcript(video_id))
