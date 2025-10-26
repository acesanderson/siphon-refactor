from siphon_api.interfaces import ExtractorStrategy
from siphon_api.models import SourceInfo, ContentData
from siphon_api.enums import SourceType
from typing import override


class YouTubeExtractor(ExtractorStrategy):
    """Extract content from YouTube"""
    
    def __init__(self, client=None):
        # TODO: Inject actual client dependency
        self.client = client
    
    @override
    def extract(self, source: SourceInfo) -> ContentData:
        # TODO: Fetch and extract content
        raise NotImplementedError
