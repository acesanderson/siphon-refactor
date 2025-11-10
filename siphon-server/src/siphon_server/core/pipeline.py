from siphon_api.models import ProcessedContent, SourceInfo, ContentData, EnrichedData
from siphon_api.interfaces import (
    ParserStrategy,
    ExtractorStrategy,
    EnricherStrategy,
)

from siphon_server.database.postgres.repository import ContentRepository
from siphon_server.sources.registry import load_registry, generate_registry
from siphon_api.enums import SourceType
import time

import logging

logger = logging.getLogger(__name__)

generate_registry()  # We will remove this in production

REGISTRY: list[str] = load_registry()
REPOSITORY = ContentRepository()


class SourceParser:
    """
    Step 1: Parse source string → SourceInfo
    """

    def __init__(self):
        logger.debug("Initializing SourceParser and loading parsers.")
        self.parsers: list[ParserStrategy] = self._find_parser()

    def _find_parser(self) -> list[ParserStrategy]:
        """
        Cycle through all registered source types and dynamically load their parsers.
        """

        logger.debug("Finding parsers for registered source types.")

        def _load_parser(source_type: str) -> ParserStrategy | None:
            module = __import__(
                f"siphon_server.sources.{source_type.lower()}.parser",
                fromlist=[""],
            )
            parser_class_name = source_type + "Parser"
            parser_class = getattr(module, parser_class_name, None)
            return parser_class

        parsers: list[ParserStrategy] = []
        for source_type in REGISTRY:
            parser = _load_parser(SourceType[source_type.upper()])
            if parser:
                logger.info(f"Loaded parser for source type: {source_type}")
                parsers.append(parser)
        return parsers

    def execute(self, source: str) -> SourceInfo:
        logger.debug(f"Executing SourceParser for source: {source}")
        for parser in self.parsers:
            parser_obj = parser()
            if parser_obj.can_handle(source=source):
                logger.info(f"Using parser {parser.__name__} for source: {source}")
                return parser_obj.parse(source=source)
        raise ValueError(f"No parser found for source: {source}")


class ContentExtractor:
    """
    Step 2: SourceInfo → ContentData
    """

    def __init__(self):
        logger.debug("Initializing ContentExtractor and loading extractors.")
        self.extractors: list[ExtractorStrategy] = self._find_extractor()

    def _find_extractor(self) -> list[ExtractorStrategy]:
        """
        Cycle through all registered source types and dynamically load their extractors.
        """
        logger.debug("Finding extractors for registered source types.")

        def _load_extractor(source_type: str) -> ExtractorStrategy | None:
            module = __import__(
                f"siphon_server.sources.{source_type.lower()}.extractor",
                fromlist=[""],
            )
            extractor_class_name = source_type + "Extractor"
            extractor_class = getattr(module, extractor_class_name, None)
            return extractor_class

        extractors: list[ExtractorStrategy] = []
        for source_type in REGISTRY:
            extractor = _load_extractor(SourceType[source_type.upper()])
            if extractor:
                logger.info(f"Loaded extractor for source type: {source_type}")
                extractors.append(extractor)
        return extractors

    def execute(self, source_info: SourceInfo) -> ContentData:
        logger.debug(
            f"Executing ContentExtractor for source type: {source_info.source_type}"
        )
        source_type = source_info.source_type
        for extractor in self.extractors:
            if extractor.source_type == source_type:
                logger.info(
                    "Using extractor {extractor.__name__} for source type: {source_type}"
                )
                extractor_obj = extractor()
                return extractor_obj.extract(source=source_info)


class ContentEnricher:
    """
    Step 3: ContentData → EnrichedData
    """

    def __init__(self):
        logger.debug("Initializing ContentEnricher and loading enrichers.")
        self.enrichers: list[EnricherStrategy] = self._find_enricher()

    def _find_enricher(self):
        logger.debug("Finding enrichers for registered source types.")

        def _load_enricher(source_type: str) -> EnricherStrategy | None:
            module = __import__(
                f"siphon_server.sources.{source_type.lower()}.enricher",
                fromlist=[""],
            )
            enricher_class_name = source_type + "Enricher"
            enricher_class = getattr(module, enricher_class_name, None)
            return enricher_class

        enrichers: list[EnricherStrategy] = []
        for source_type in REGISTRY:
            enricher = _load_enricher(SourceType[source_type.upper()])
            if enricher:
                logger.info(f"Loaded enricher for source type: {source_type}")
                enrichers.append(enricher)
        return enrichers

    def execute(self, content_data: ContentData) -> EnrichedData:
        logger.debug("Executing ContentEnricher.")
        source_type = content_data.source_type
        for enricher in self.enrichers:
            if enricher.source_type == source_type:
                logger.info(
                    "Using enricher {enricher.__name__} for source type: {source_type}"
                )
                enricher_obj = enricher()
                return enricher_obj.enrich(content=content_data)


class SiphonPipeline:
    """
    Main orchestrator - the aggregate root.
    Explicit pipeline: source → parse → extract → enrich → result
    """

    def __init__(
        self,
    ):
        logger.debug("Initializing SiphonPipeline.")
        self.parser = SourceParser()
        self.extractor = ContentExtractor()
        self.enricher = ContentEnricher()
        # self.cache = SiphonCache()

    def process(self, source: str, use_cache: bool = True) -> ProcessedContent:
        # Step 1: Parse source
        source_info = self.parser.execute(source)
        logger.info(f"Parsed source info: {source_info}")

        # Check repository
        if REPOSITORY.exists(source_info.uri):
            logger.info(
                f"Content already exists in repository for URI: {source_info.uri}"
            )
            existing_content = REPOSITORY.get(source_info.uri)
            if existing_content:
                return existing_content

        # Step 2: Extract content
        content_data = self.extractor.execute(source_info)
        logger.info(f"Extracted content data: {content_data}")

        # Step 3: Enrich with LLM
        enriched_data = self.enricher.execute(content_data)
        logger.info(f"Enriched data: {enriched_data}")

        # Step 4: Assemble result
        result = ProcessedContent(
            source=source_info,
            content=content_data,
            enrichment=enriched_data,
            tags=[],
            created_at=int(time.time()),
            updated_at=int(time.time()),
        )
        logger.info(f"Processed content assembled.")

        # Store in repository
        REPOSITORY.set(result)
        logger.info(
            f"Processed content stored in repository for URI: {source_info.uri}"
        )

        return result


if __name__ == "__main__":
    from siphon_server.example import EXAMPLES

    examples = [EXAMPLES["pdf"], EXAMPLES["mp3"], EXAMPLES["wav"]]

    for index, source in enumerate(examples):
        print(f"\n--- Processing Example {index + 1} ---")
        pipeline = SiphonPipeline()
        processed_content = pipeline.process(str(source))
        print(f"Processed content for source: {source}")
        print(processed_content)
