from siphon_api.models import ProcessedContent
from siphon_server.database.postgres import init_table, get, set
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class SiphonCache:
    def __init__(self):
        logger.debug("Initializing SiphonCache and database table.")
        init_table()

    @lru_cache(maxsize=1024)
    def get(self, uri: str) -> ProcessedContent | None:
        logger.debug(f"Fetching content from cache for URI: {uri}")
        return get(uri)

    def set(self, content: ProcessedContent) -> None:
        logger.debug(f"Storing content in cache for URI: {content.uri}")
        set(content)
