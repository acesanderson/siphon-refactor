from siphon_api.interfaces import ParserStrategy
from siphon_api.models import SourceInfo
from siphon_api.enums import SourceType
from siphon_api.file_types import EXTENSIONS
from pathlib import Path
import hashlib
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
        source_info = SourceInfo(
            source_type=self.source_type,
            uri=f"doc:///{self._get_extension}/{self._compute_hash}",
            original_source=source,
            hash=self._compute_hash(path),
        )
        return source_info

    def _get_extension(self, path: Path) -> str:
        """
        Get file extension in normalized form.
        """
        return path.suffix.lower()

    def _compute_hash(self, path: Path) -> str:
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
