from siphon_api.interfaces import ParserStrategy
from siphon_api.models import SourceInfo
from siphon_api.enums import SourceType
from typing import override
import re


class YouTubeParser(ParserStrategy):
    """YouTube bounded context - parsing logic"""

    @override
    def can_handle(self, source: str) -> bool:
        patterns = [
            r"youtube\.com/watch\?v=",
            r"youtu\.be/",
        ]
        return any(re.search(p, source) for p in patterns)

    @override
    def parse(self, source: str) -> SourceInfo:
        video_id = self._extract_video_id(source)

        return SourceInfo(
            source_type=SourceType.YOUTUBE,
            uri=f"youtube:///{video_id}",
            original_source=source,
            metadata={"video_id": video_id},
        )

    def _extract_video_id(self, url: str) -> str:
        # Regex to extract video ID
        patterns = [
            r"youtube\.com/watch\?v=([^&]+)",
            r"youtu\.be/([^?]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError(f"Cannot extract video ID from: {url}")
