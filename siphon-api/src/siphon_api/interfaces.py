from typing import Protocol
from siphon_api.models import SourceInfo, ContentData


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
