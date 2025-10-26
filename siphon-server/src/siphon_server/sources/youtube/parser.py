from siphon_api.interfaces import ParserStrategy
from siphon_api.models import SourceInfo
from siphon_api.enums import SourceType
from typing import override


class YouTubeParser(ParserStrategy):
    """Parse YouTube sources"""
    
    @override
    def can_handle(self, source: str) -> bool:
        # TODO: Implement detection logic
        raise NotImplementedError
    
    @override
    def parse(self, source: str) -> SourceInfo:
        # TODO: Extract identifier and metadata
        raise NotImplementedError
