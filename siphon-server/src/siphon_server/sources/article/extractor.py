from siphon_api.interfaces import ExtractorStrategy
from siphon_api.models import SourceInfo, ContentData
from siphon_api.enums import SourceType
from siphon_server.sources.article.metadata import ArticleMetadata
from siphon_server.sources.article.cache import ArticleCache
from trafilatura import fetch_url
from trafilatura import extract as trafilatura_extract
from typing import override
import json
import logging

logger = logging.getLogger(__name__)
fetch_cache = ArticleCache()


class ArticleExtractor(ExtractorStrategy):
    """
    Extract content from Article.
    Uses Trafilatura under the hood.
    """

    source_type: SourceType = SourceType.ARTICLE

    @override
    def extract(self, source: SourceInfo) -> ContentData:
        logger.info(f"Extracting Article content from {source.original_source}")
        url = source.original_source
        cached: str | None = fetch_cache.get(url)
        if cached:
            logger.debug("Cache hit!")
            article_md = cached
        else:
            logger.debug("Cache miss, fetching content from the web.")
            downloaded = fetch_url(url)

            if not downloaded:
                raise RuntimeError("Download failed (blocked, timed out, or empty).")
            logger.debug("Download successful, extracting content.")
            article_md: str | None = trafilatura_extract(
                downloaded,
                url=url,  # helps resolve relative links & date parsing
                output_format="json",  # "txt", "json", "html", "xml", "xmltei" also available
                with_metadata=True,  # include title, author, date, etc. in the output
                include_links=True,  # keep link targets (works best with XML/MD/JSON)
                include_tables=False,  # often noise for news articles
                include_comments=False,  # comment threads not needed for articles
                favor_precision=True,  # reduce boilerplate; try favor_recall=True if content is missing
            )
            if article_md:
                logger.debug("Extraction successful. Caching fetched article content.")
                fetch_cache.set(url, article_md)

        json_dict: dict[str, str] = json.loads(article_md) if article_md else {}
        text = json_dict.pop("text")
        metadata_obj = ArticleMetadata(**json_dict).normalize()
        metadata = metadata_obj.model_dump()

        if article_md is None:
            raise RuntimeError(
                "Extraction returned None (failed heuristics or filtered by settings)."
            )

        return ContentData(source_type=self.source_type, metadata=metadata, text=text)
