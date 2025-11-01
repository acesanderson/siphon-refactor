import pytest
from siphon_api.enums import SourceType
from siphon_api.models import SourceInfo, ContentData
from siphon_server.sources.article.parser import ArticleParser
from siphon_server.sources.article.extractor import ArticleExtractor
from siphon_server.sources.article.enricher import ArticleEnricher


# === PARSER TESTS ===
@pytest.mark.parser
class TestArticleParser:
    @pytest.fixture
    def parser(self):
        return ArticleParser()
    
    def test_can_handle_valid_source(self, parser):
        # TODO: Add valid source example
        pytest.skip("TODO: Implement can_handle test")
    
    def test_can_handle_invalid_source(self, parser):
        assert not parser.can_handle("https://example.com")
    
    def test_parse_extracts_identifier(self, parser):
        # TODO: Add parsing test
        pytest.skip("TODO: Implement parse test")
    
    def test_parse_creates_correct_uri(self, parser):
        # TODO: Verify URI format is "article:///{identifier}"
        pytest.skip("TODO: Implement URI format test")


# === EXTRACTOR TESTS ===
@pytest.mark.extractor
class TestArticleExtractor:
    @pytest.fixture
    def extractor(self):
        # TODO: Mock client dependency
        return ArticleExtractor(client=None)
    
    @pytest.fixture
    def sample_source(self):
        # TODO: Create realistic sample SourceInfo
        return SourceInfo(
            source_type=SourceType.ARTICLE,
            uri="article:///sample_id",
            original_source="TODO: original URL",
            metadata={"identifier": "sample_id"}
        )
    
    def test_extract_returns_content_data(self, extractor, sample_source):
        # TODO: Implement extraction test
        pytest.skip("TODO: Implement extract test")
    
    def test_extract_populates_text(self, extractor, sample_source):
        # TODO: Verify text field is populated
        pytest.skip("TODO: Verify text extraction")
    
    def test_extract_includes_metadata(self, extractor, sample_source):
        # TODO: Verify metadata is captured
        pytest.skip("TODO: Verify metadata extraction")


# === ENRICHER TESTS ===
@pytest.mark.enricher
class TestArticleEnricher:
    @pytest.fixture
    def enricher(self):
        # TODO: Mock LLM client
        return ArticleEnricher(llm=None)
    
    @pytest.fixture
    def sample_content(self):
        # TODO: Create realistic sample ContentData
        return ContentData(
            source_type=SourceType.ARTICLE,
            text="Sample content text here...",
            metadata={"title": "Sample Title"}
        )
    
    def test_enrich_generates_summary(self, enricher, sample_content):
        # TODO: Implement enrichment test
        pytest.skip("TODO: Implement enrich test")
    
    def test_enrich_extracts_topics(self, enricher, sample_content):
        # TODO: Verify topics extraction
        pytest.skip("TODO: Verify topics")
    
    def test_enrich_extracts_entities(self, enricher, sample_content):
        # TODO: Verify entities extraction
        pytest.skip("TODO: Verify entities")


# === INTEGRATION TEST ===
@pytest.mark.integration
class TestArticlePipeline:
    def test_end_to_end_processing(self):
        """Full pipeline: parse → extract → enrich"""
        # TODO: Implement full pipeline test
        pytest.skip("TODO: Implement after all components work")
