import pytest

@pytest.fixture
def sample_youtube_url():
    """Reusable test URL for YouTube"""
    # TODO: Add realistic example URL
    return "https://example.com/youtube/sample"


@pytest.fixture
def mock_youtube_client():
    """Mock client for YouTube API"""
    # TODO: Implement mock client
    class MockYouTubeClient:
        def fetch(self, identifier):
            return {"content": "mock content", "metadata": {}}
    
    return MockYouTubeClient()


@pytest.fixture
def mock_llm():
    """Mock LLM for enrichment tests"""
    # TODO: Implement LLM mock with canned responses
    class MockLLM:
        def generate(self, prompt):
            return "Mock summary"
    
    return MockLLM()
