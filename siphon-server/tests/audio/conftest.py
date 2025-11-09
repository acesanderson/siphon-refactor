import pytest

@pytest.fixture
def sample_audio_url():
    """Reusable test URL for Audio"""
    # TODO: Add realistic example URL
    return "https://example.com/audio/sample"


@pytest.fixture
def mock_audio_client():
    """Mock client for Audio API"""
    # TODO: Implement mock client
    class MockAudioClient:
        def fetch(self, identifier):
            return {"content": "mock content", "metadata": {}}
    
    return MockAudioClient()


@pytest.fixture
def mock_llm():
    """Mock LLM for enrichment tests"""
    # TODO: Implement LLM mock with canned responses
    class MockLLM:
        def generate(self, prompt):
            return "Mock summary"
    
    return MockLLM()
