"""
WIP:
- basic Drive authentication logic is completed
- need better way to handle secrets
- we need to determine mime types for different Drive document types
- the baseio objects need further parsing to extract text content
- authentication is google API for my personal account; also add service account for enterprise use cases.
"""

from siphon_api.interfaces import ExtractorStrategy
from siphon_api.models import SourceInfo, ContentData
from siphon_api.enums import SourceType
from siphon_api.metadata import DriveMetadata
from typing import override
from functools import lru_cache
import logging
import re

logger = logging.getLogger(__name__)
prefix_and_id_pattern = re.compile(
    r"https://docs\.google\.com/(spreadsheets|document|presentation|forms)/d/([a-zA-Z0-9_-]+)"
)


class DriveExtractor(ExtractorStrategy):
    """Extract content from Drive"""

    source_type: SourceType = SourceType.DRIVE

    @override
    def extract(self, source: SourceInfo) -> ContentData:
        logger.info("Extracting content from Drive...")
        doc_id = self._extract_id_from_url(source.original_source)
        metadata = self._get_metadata(doc_id)
        text = self._download_drive_content(doc_id)
        content_data = ContentData(
            source_type=SourceType.DRIVE,
            text=text,
            metadata=metadata,
        )
        return content_data

    def _extract_id_from_url(self, url: str) -> str:
        match = prefix_and_id_pattern.search(url)
        if not match:
            raise ValueError("Invalid Drive URL format")
        doc_id = match.group(2)
        return doc_id

    @lru_cache(maxsize=128)
    def _get_metadata(self, doc_id: str) -> dict:
        """
        Fetch metadata for the Drive document.
        """
        logger.info(f"Fetching metadata for Drive document ID: {doc_id}")
        from siphon_server.sources.drive.pipeline.drive_metadata import (
            get_metadata_by_id,
        )
        from siphon_server.sources.drive.pipeline.drive_service import get_drive_service

        drive_service = get_drive_service()
        metadata = get_metadata_by_id(doc_id, drive_service)
        return metadata.model_dump()

    @lru_cache(maxsize=128)
    def _download_drive_content(self, doc_id: str, metadata: DriveMetadata) -> str:
        """
        WIP:
        (1) need to determine mime type based on metadata.
        (2) need to properly handle the baseio object returned from drive_get.
        """
        logger.info(f"Downloading content from Drive URL: {url}")
        from siphon_server.sources.drive.pipeline.drive_get import get_document_by_id
        from siphon_server.sources.drive.drive_service import get_drive_service

        # drive_service = get_drive_service()
        # mime_type = ""
        # content = get_document_by_id(drive_service, doc_id, mime_type)
        # return content


if __name__ == "__main__":
    from siphon_server.sources.drive.parser import DriveParser

    example_source = "https://docs.google.com/document/d/1L4rwvx5P33LbPcX2dawSYrE2Z38yXwBBRaPVJakHozU/edit?tab=t.0"
    parser = DriveParser()
    source_info = parser.parse(example_source)

    extractor = DriveExtractor()
    content_data = extractor.extract(source_info)
    print(content_data)
