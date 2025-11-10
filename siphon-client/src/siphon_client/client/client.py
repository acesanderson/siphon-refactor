import httpx
from siphon_api.models import ProcessedContent
from typing import Literal


class SiphonClient:
    """
    Thin HTTP client - all processing happens server-side.
    This class is just a convenient wrapper around HTTP calls.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 300.0,  # 5 min for heavy processing
    ):
        self.base_url = base_url
        self.client = httpx.Client(timeout=timeout)

    def process(
        self, source: str, use_cache: bool = True, model: str = "gpt-4o"
    ) -> ProcessedContent:
        """
        Main method - send source to server, get ProcessedContent back.
        """
        response = self.client.post(
            f"{self.base_url}/api/v2/process",
            json={
                "source": source,
                "use_cache": use_cache,
                "model": model,
            },
        )
        response.raise_for_status()
        return ProcessedContent.model_validate(response.json())

    def get_cached(self, uri: str) -> ProcessedContent | None:
        """Fetch from server cache"""
        response = self.client.get(f"{self.base_url}/api/v2/cache/{uri}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return ProcessedContent.model_validate(response.json())

    def query(
        self,
        source_type: str | None = None,
        tags: list[str] | None = None,
        since: str | None = None,
        limit: int = 100,
    ) -> list[ProcessedContent]:
        """Query for content matching criteria"""
        params = {
            "source_type": source_type,
            "tags": tags,
            "since": since,
            "limit": limit,
        }
        response = self.client.get(
            f"{self.base_url}/api/v2/query",
            params={k: v for k, v in params.items() if v is not None},
        )
        response.raise_for_status()
        return [ProcessedContent.model_validate(item) for item in response.json()]
