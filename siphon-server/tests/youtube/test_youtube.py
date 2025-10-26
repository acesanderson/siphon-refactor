import pytest
from siphon_api.enums import SourceType
from siphon_api.models import SourceInfo, ContentData
from siphon_server.sources.youtube.parser import YouTubeParser
from siphon_server.sources.youtube.extractor import YouTubeExtractor
from siphon_server.sources.youtube.enricher import YouTubeEnricher


# === PARSER TESTS ===
@pytest.mark.parser
class TestYouTubeParser:
    @pytest.fixture
    def parser(self):
        return YouTubeParser()

    @pytest.fixture
    def youtube_url(self):
        return "https://www.youtube.com/watch?v=6ctoS84iFCw"

    def test_can_handle_valid_source(self, parser, youtube_url):
        assert parser.can_handle("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert parser.can_handle("https://youtu.be/dQw4w9WgXcQ")
        assert parser.can_handle(youtube_url)

    def test_can_handle_invalid_source(self, parser):
        assert not parser.can_handle("https://vimeo.com/123456789")
        assert not parser.can_handle("ftp://youtube.com/video")
        assert not parser.can_handle("https://example.com")

    def test_parse_extracts_identifier(self, parser):
        source_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        source_info = parser.parse(source_url)
        assert source_info.metadata["video_id"] == "dQw4w9WgXcQ"

    def test_parse_creates_correct_uri(self, parser):
        source_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        source_info = parser.parse(source_url)
        source_info.uri = f"youtube:///{source_info.metadata['video_id']}"


# === EXTRACTOR TESTS ===
@pytest.mark.extractor
class TestYouTubeExtractor:
    @pytest.fixture
    def parser(self):
        return YouTubeParser()

    @pytest.fixture
    def extractor(self):
        return YouTubeExtractor()

    @pytest.fixture
    def sample_source(self, parser):
        source_info = parser.parse("https://www.youtube.com/watch?v=6ctoS84iFCw")
        return source_info

    def test_extract_returns_content_data(self, extractor, sample_source):
        content_data = extractor.extract(sample_source)
        assert isinstance(content_data, ContentData)

    def test_extract_populates_text(self, extractor, sample_source):
        content_data = extractor.extract(sample_source)
        assert content_data.text is not None
        assert len(content_data.text) > 0
        assert isinstance(content_data.text, str)

    def test_extract_includes_metadata(self, extractor, sample_source):
        content_data = extractor.extract(sample_source)
        assert "title" in content_data.metadata
        assert len(content_data.metadata["title"]) > 0
        assert "description" in content_data.metadata
        assert len(content_data.metadata["description"]) > 0
        assert "channel" in content_data.metadata
        assert len(content_data.metadata["channel"]) > 0


# === ENRICHER TESTS ===
@pytest.mark.enricher
class TestYouTubeEnricher:
    @pytest.fixture
    def enricher(self):
        # TODO: Mock LLM client
        return YouTubeEnricher(llm=None)

    @pytest.fixture
    def sample_content(self):
        # TODO: Create realistic sample ContentData
        return ContentData(
            source_type=SourceType.YOUTUBE,
            text="Sample content text here...",
            metadata={"title": "Sample Title"},
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
class TestYouTubePipeline:
    def test_end_to_end_processing(self):
        """Full pipeline: parse → extract → enrich"""
        # TODO: Implement full pipeline test
        pytest.skip("TODO: Implement after all components work")
