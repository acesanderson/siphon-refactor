from siphon_api.interfaces import ParserStrategy
from siphon_api.models import SourceInfo
from siphon_api.enums import SourceType
from typing import override


class YouTubeParser(ParserStrategy):
    """Parse YouTube sources"""

    @override
    def can_handle(self, source: str) -> bool:
        """
        Needs to be:
        - a url
        - from youtube.com or youtu.be
        """
        return (source.startswith("http://") or source.startswith("https://")) and (
            "youtube.com" in source or "youtu.be" in source
        )

    @override
    def parse(self, source: str) -> SourceInfo:
        """
        Parse YouTube URL into SourceInfo    source_type: SourceType
        uri: str  # Canonical identifier (e.g., "youtube:///dQw4w9WgXcQ")
        original_source: str  # User input (e.g., "https://youtube.com/watch?v=dQw4w9WgXcQ")
        checksum: str | None = None
        metadata: dict[str, Any] = Field(default_factory=dict)
        """
        import re

        # Extract video ID from URL
        video_id = None
        youtube_regex = (
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"  # Matches v=VIDEO_ID or /VIDEO_ID
        )
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

        uri = f"youtube:///{video_id}"
        checksum = None  # YouTube videos don't have a checksum in this context

        return SourceInfo(
            source_type=SourceType.YOUTUBE,
            uri=uri,
            original_source=source,
            checksum=checksum,
            metadata={"video_id": video_id},
        )
