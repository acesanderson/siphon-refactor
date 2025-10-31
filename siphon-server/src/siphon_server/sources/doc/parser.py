from siphon_api.interfaces import ParserStrategy
from siphon_api.models import SourceInfo
from siphon_api.enums import SourceType
from siphon_api.file_types import EXTENSIONS, MIME_TYPES
from siphon_api.metadata import FileMetadata
from pathlib import Path
import hashlib
from datetime import datetime, timezone
from typing import override


class DocParser(ParserStrategy):
    """
    Parse Doc sources.
    These are extensions that can be adapted by Markitdown.
    Text and document files.
    Examples: .doc, .docx, .txt
    """

    source_type: SourceType = SourceType.DOC

    @override
    def can_handle(self, source: str) -> bool:
        try:
            path = Path(source)
            if path.exists():
                return (
                    path.suffix.lower() in EXTENSIONS["Doc"]
                    or path.suffix.lower() in EXTENSIONS["Text"]
                )
        except TypeError:
            return False

    @override
    def parse(self, source: str) -> SourceInfo:
        """
        All of our file-based sources are represented as:
        Doc:///{extension}/{hash}
        """
        path = Path(source)
        assert path.exists(), f"File does not exist: {source}"
        # Construct our metadata first
        metadata = FileMetadata(
            file_name=path.name,
            hash=self._compute_file_hash(path),
            created_at=self._get_created_at(path),
            last_modified=self._get_last_modified(path),
            file_size=self._get_file_size(path),
            extension=self._get_extension(path),
            mime_type=self._get_mime_type(self._get_extension(path)),
        )
        # Construct our SourceInfo and metadata
        source_info = SourceInfo(
            source_type=self.source_type,
            uri=f"doc:///{metadata.extension}/{metadata.hash}",
            original_source=source,
            checksum=metadata.hash,
            metadata=metadata.model_dump(),
        )
        return source_info

    def _get_created_at(self, path: Path) -> str:
        timestamp = path.stat().st_ctime
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.isoformat()

    def _get_last_modified(self, path: Path) -> str:
        """
        Get file last modified timestamp as ISO string.
        """
        timestamp = path.stat().st_mtime
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.isoformat()

    def _get_file_size(self, path: Path) -> int:
        """
        Get file size in bytes.
        """
        return path.stat().st_size

    def _get_extension(self, path: Path) -> str:
        """
        Get file extension in normalized form.
        """
        return path.suffix.lower()

    def _get_mime_type(self, extension: str) -> str:
        """
        Get MIME type for given extension.
        """
        return MIME_TYPES.get(extension, "application/octet-stream")

    def _compute_file_hash(self, path: Path) -> str:
        """
        Compute SHA-256 hash of file content.
        Only need first 16 characters for our purposes.
        """
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]


if __name__ == "__main__":
    parser = DocParser()
    example_file = Path(__file__).parent / "enricher.py"
    assert example_file.exists(), "Example file does not exist"
    assert parser.can_handle(str(example_file)), "Parser cannot handle the example file"
    source_info = parser.parse(str(example_file))
    print(source_info.model_dump_json(indent=2))
