import pytest

@pytest.fixture
def sample_drive_url():
    """Reusable test URL for Drive"""
    # TODO: Add realistic example URL
    return "https://example.com/drive/sample"


@pytest.fixture
def mock_drive_client():
    """Mock client for Drive API"""
    # TODO: Implement mock client
    class MockDriveClient:
        def fetch(self, identifier):
            return {"content": "mock content", "metadata": {}}
    
    return MockDriveClient()


@pytest.fixture
def mock_llm():
    """Mock LLM for enrichment tests"""
    # TODO: Implement LLM mock with canned responses
    class MockLLM:
        def generate(self, prompt):
            return "Mock summary"
    
    return MockLLM()
