from siphon_api.interfaces import ParserStrategy
from siphon_api.models import SourceInfo
from siphon_api.enums import SourceType
from typing import override


class DriveParser(ParserStrategy):
    """Parse Drive sources"""

    source_type: SourceType = SourceType.DRIVE

    @override
    def can_handle(self, source: str) -> bool:
        """
        Either Sheets, Docs, Slides, or Forms URL
        """
        sheets_prefix = "https://docs.google.com/spreadsheets/"
        docs_prefix = "https://docs.google.com/document/"
        slides_prefix = "https://docs.google.com/presentation/"
        forms_prefix = "https://docs.google.com/forms/"
        return (
            source.startswith(sheets_prefix)
            or source.startswith(docs_prefix)
            or source.startswith(slides_prefix)
            or source.startswith(forms_prefix)
        )

    @override
    def parse(self, source: str) -> SourceInfo:
        """
        Parse Drive source URL into SourceInfo.
        URI format: drive:///{document_type}/{document_id}
        """
        # Extract document type and ID from the URL
        if "spreadsheets" in source:
            document_type = "sheets"
            prefix = "https://docs.google.com/spreadsheets/d/"
        elif "document" in source:
            document_type = "docs"
            prefix = "https://docs.google.com/document/d/"
        elif "presentation" in source:
            document_type = "slides"
            prefix = "https://docs.google.com/presentation/d/"
        elif "forms" in source:
            document_type = "forms"
            prefix = "https://docs.google.com/forms/d/"
        else:
            raise ValueError("Unsupported Drive document type")

        # Extract the document ID
        document_id = source.split(prefix)[1].split("/")[0]

        uri = f"drive:///{document_type}/{document_id}"
        hash = None
        return SourceInfo(
            source_type=SourceType.DRIVE,
            uri=uri,
            original_source=source,
            hash=hash,
        )


if __name__ == "__main__":
    example_source = "https://docs.google.com/document/d/1a2b3c4d5e6f7g8h9i0j/edit"
    parser = DriveParser()
    source_info = parser.parse(example_source)
