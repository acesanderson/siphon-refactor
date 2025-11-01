import pytest

@pytest.fixture
def sample_article_url():
    """Reusable test URL for Article"""
    # TODO: Add realistic example URL
    return "https://example.com/article/sample"


@pytest.fixture
def mock_article_client():
    """Mock client for Article API"""
    # TODO: Implement mock client
    class MockArticleClient:
        def fetch(self, identifier):
            return {"content": "mock content", "metadata": {}}
    
    return MockArticleClient()


@pytest.fixture
def mock_llm():
    """Mock LLM for enrichment tests"""
    # TODO: Implement LLM mock with canned responses
    class MockLLM:
        def generate(self, prompt):
            return "Mock summary"
    
    return MockLLM()
