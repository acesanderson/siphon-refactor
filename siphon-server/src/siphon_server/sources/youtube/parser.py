from siphon_api.interfaces import ParserStrategy
from siphon_api.models import SourceInfo
from siphon_api.enums import SourceType
from siphon_server.sources.youtube.get_video_id import get_video_id
from typing import override


class YouTubeParser(ParserStrategy):
    """
    Parse YouTube sources
    """

    source_type: SourceType = SourceType.YOUTUBE

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
        hash: str | None = None
        """

        video_id = get_video_id(source)

        uri = f"youtube:///{video_id}"
        hash = None  # YouTube videos don't have a checksum in this context

        return SourceInfo(
            source_type=SourceType.YOUTUBE,
            uri=uri,
            original_source=source,
            hash=hash,
        )
