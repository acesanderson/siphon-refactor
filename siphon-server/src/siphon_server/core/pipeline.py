from siphon_api.models import ProcessedContent, SourceInfo, ContentData, EnrichedData
from siphon_api.interfaces import ParserStrategy, ExtractorStrategy
from siphon_api.enums import SourceType
from siphon_server.cache import CacheService
from siphon_server.enrichment import ContentEnricher
import time


class SourceParser:
    """Step 1: Parse source string → SourceInfo"""

    def __init__(self, strategies: list[ParserStrategy]):
        self.strategies = strategies

    def execute(self, source: str) -> SourceInfo:
        for strategy in self.strategies:
            if strategy.can_handle(source):
                return strategy.parse(source)
        raise ValueError(f"No parser found for source: {source}")


class ContentExtractor:
    """Step 2: SourceInfo → ContentData"""

    def __init__(self, extractors: dict[SourceType, ExtractorStrategy]):
        self.extractors = extractors

    def execute(self, source: SourceInfo) -> ContentData:
        extractor = self.extractors.get(source.source_type)
        if not extractor:
            raise ValueError(f"No extractor for {source.source_type}")
        return extractor.extract(source)


class SiphonPipeline:
    """
    Main orchestrator - the aggregate root.
    Explicit pipeline: source → parse → extract → enrich → result
    """

    def __init__(
        self,
        parser: SourceParser,
        extractor: ContentExtractor,
        enricher: ContentEnricher,
        cache: CacheService | None = None,
    ):
        self.parser = parser
        self.extractor = extractor
        self.enricher = enricher
        self.cache = cache

    def process(self, source: str, use_cache: bool = True) -> ProcessedContent:
        # Step 1: Parse source
        source_info = self.parser.execute(source)

        # Check cache
        if use_cache and self.cache:
            cached = self.cache.get(source_info.uri)
            if cached:
                return cached

        # Step 2: Extract content
        content_data = self.extractor.execute(source_info)

        # Step 3: Enrich with LLM
        enriched_data = self.enricher.execute(content_data)

        # Step 4: Assemble result
        result = ProcessedContent(
            source=source_info,
            content=content_data,
            enrichment=enriched_data,
            tags=[],
            created_at=int(time.time()),
            updated_at=int(time.time()),
        )

        # Cache
        if use_cache and self.cache:
            self.cache.set(source_info.uri, result)

        return result
