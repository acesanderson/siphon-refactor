from typing import Protocol
from siphon_api.models import SourceInfo, ContentData, EnrichedData


class ParserStrategy(Protocol):
    """
    Interface for source parsing strategies
    """

    def can_handle(self, source: str) -> bool: ...
    def parse(self, source: str) -> SourceInfo: ...


class ExtractorStrategy(Protocol):
    """
    Interface for content extraction strategies
    """

    def extract(self, source: SourceInfo) -> ContentData: ...


class EnricherStrategy(Protocol):
    """
    Interface for content enrichment strategies.
    (summarization approaches will differ for different content types)
    """

    def enrich(self, content: ContentData) -> EnrichedData: ...
