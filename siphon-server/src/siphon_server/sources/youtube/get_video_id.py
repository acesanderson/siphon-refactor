import re


def get_video_id(source: str) -> str:
    # Extract video ID from URL
    video_id = None
    youtube_regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"  # Matches v=VIDEO_ID or /VIDEO_ID
    short_youtube_regex = r"youtu\.be\/([0-9A-Za-z_-]{11})"

    match = re.search(youtube_regex, source)
    if match:
        video_id = match.group(1)
    else:
        match = re.search(short_youtube_regex, source)
        if match:
            video_id = match.group(1)

    if not video_id:
        raise ValueError("Invalid YouTube URL")

    return video_id
