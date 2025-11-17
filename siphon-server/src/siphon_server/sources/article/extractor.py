from siphon_api.interfaces import ExtractorStrategy
from siphon_api.models import SourceInfo, ContentData
from siphon_api.enums import SourceType
from siphon_api.errors import SiphonExtractorError
from siphon_server.sources.article.metadata import ArticleMetadata
from siphon_server.sources.article.cache import ArticleCache
from typing import override
import logging

logger = logging.getLogger(__name__)
fetch_cache = ArticleCache()

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"


class ArticleExtractor(ExtractorStrategy):
    """
    Extract content from Article.
    Uses Readabilipy under the hood.
    """

    source_type: SourceType = SourceType.ARTICLE

    @override
    def extract(self, source: SourceInfo) -> ContentData:
        logger.info(f"Extracting Article content from {source.original_source}")
        url = source.original_source
        cached: ContentData | None = fetch_cache.get(url)

        if cached:
            logger.debug("Cache hit!")
            return cached
        else:
            article, metadata = self._fetch_url(url)  # Now returns tuple

            if not article or article.strip() == "":
                raise SiphonExtractorError(
                    "Extraction returned None (failed heuristics or filtered by settings)."
                )
            metadata = ArticleMetadata(**metadata).model_dump()
            content_data = ContentData(
                source_type=self.source_type, metadata=metadata, text=article
            )
            fetch_cache.set(url, content_data)
            return content_data

    def _extract_content_from_html(self, html: str) -> tuple[str, dict]:
        """Extract content and metadata from HTML."""
        import readabilipy.simple_json
        import markdownify

        ret = readabilipy.simple_json.simple_json_from_html_string(
            html, use_readability=True
        )
        if not ret["content"]:
            raise SiphonExtractorError("Page failed to be simplified from HTML")

        content = markdownify.markdownify(
            ret["content"],
            heading_style=markdownify.ATX,
        )

        # Extract metadata
        metadata = {
            "title": ret.get("title"),
            "byline": ret.get("byline"),
            "dir": ret.get("dir"),
            "lang": ret.get("lang"),
            "length": ret.get("length"),
            "siteName": ret.get("siteName"),
        }

        # Remove None values
        metadata = {k: v for k, v in metadata.items() if v is not None}

        return content, metadata

    def _fetch_url(
        self,
        url: str,
        user_agent: str = USER_AGENT,
        force_raw: bool = False,
    ) -> tuple[str, dict]:
        """Fetch URL and return content + metadata."""
        import httpx

        with httpx.Client() as client:
            try:
                response = client.get(
                    url,
                    follow_redirects=True,
                    headers={"User-Agent": user_agent},
                    timeout=30,
                )
            except httpx.HTTPError as e:
                raise SiphonExtractorError(f"Failed to fetch {url}: {e}")

            if response.status_code >= 400:
                raise SiphonExtractorError(
                    f"Failed to fetch {url} - status code {response.status_code}"
                )

            page_raw = response.text

        # HTTP metadata
        http_metadata = {
            "source_url": url,
            "final_url": str(response.url),
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type"),
        }

        # Add optional headers if present
        if last_modified := response.headers.get("last-modified"):
            http_metadata["last_modified"] = last_modified

        content_type = response.headers.get("content-type", "")
        is_page_html = (
            "<html" in page_raw[:100] or "text/html" in content_type or not content_type
        )

        if is_page_html and not force_raw:
            content, html_metadata = self._extract_content_from_html(page_raw)
            return content, {**http_metadata, **html_metadata}

        return page_raw, http_metadata
