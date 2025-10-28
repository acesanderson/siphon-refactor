from typing import Protocol
from siphon_api.models import SourceInfo, ContentData, EnrichedData
from siphon_api.enums import SourceType


class ParserStrategy(Protocol):
    """
    Interface for source parsing strategies
    """

    source_type: SourceType

    @staticmethod
    def can_handle(source: str) -> bool: ...

    @staticmethod
    def parse(self, source: str) -> SourceInfo: ...


class ExtractorStrategy(Protocol):
    """
    Interface for content extraction strategies
    """

    source_type: SourceType

    def extract(self, source: SourceInfo) -> ContentData: ...


class EnricherStrategy(Protocol):
    """
    Interface for content enrichment strategies.
    (summarization approaches will differ for different content types)
    """

    source_type: SourceType

    def enrich(self, content: ContentData) -> EnrichedData: ...
