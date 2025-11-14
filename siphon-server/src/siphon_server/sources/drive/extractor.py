from siphon_api.interfaces import ExtractorStrategy
from siphon_api.models import SourceInfo, ContentData
from siphon_api.enums import SourceType
from typing import override
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class DriveExtractor(ExtractorStrategy):
    """Extract content from Drive"""

    source_type: SourceType = SourceType.DRIVE

    @override
    def extract(self, source: SourceInfo) -> ContentData:
        logger.info("Extracting content from Drive...")
        metadata, text = self._download_drive_content(source.original_source)
        content_data = ContentData(
            source_type=SourceType.DRIVE,
            text=text,
            metadata=metadata,
        )
        return content_data

    @lru_cache(maxsize=128)
    def _download_drive_content(self, url: str) -> tuple[dict[str, str], str]:
        # Placeholder implementation
        logger.info(f"Downloading content from Drive URL: {url}")
        metadata = {"title": "Sample Drive Document", "author": "Author Name"}
        text = "This is the extracted text from the Drive document."
        return metadata, text


if __name__ == "__main__":
    from siphon_server.sources.drive.parser import DriveParser

    example_source = "https://docs.google.com/document/d/1L4rwvx5P33LbPcX2dawSYrE2Z38yXwBBRaPVJakHozU/edit?tab=t.0"
    parser = DriveParser()
    source_info = parser.parse(example_source)

    extractor = DriveExtractor()
    content_data = extractor.extract(source_info)
    print(content_data)
