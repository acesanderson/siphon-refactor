import pytest

@pytest.fixture
def sample_doc_url():
    """Reusable test URL for Doc"""
    # TODO: Add realistic example URL
    return "https://example.com/doc/sample"


@pytest.fixture
def mock_doc_client():
    """Mock client for Doc API"""
    # TODO: Implement mock client
    class MockDocClient:
        def fetch(self, identifier):
            return {"content": "mock content", "metadata": {}}
    
    return MockDocClient()


@pytest.fixture
def mock_llm():
    """Mock LLM for enrichment tests"""
    # TODO: Implement LLM mock with canned responses
    class MockLLM:
        def generate(self, prompt):
            return "Mock summary"
    
    return MockLLM()
