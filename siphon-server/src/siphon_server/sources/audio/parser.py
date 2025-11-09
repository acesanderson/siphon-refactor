from siphon_api.interfaces import ParserStrategy
from siphon_api.file_types import EXTENSIONS
from siphon_api.models import SourceInfo
from siphon_api.enums import SourceType
from pathlib import Path
from typing import override
import hashlib


class AudioParser(ParserStrategy):
    """Parse Audio sources"""

    source_type: SourceType = SourceType.AUDIO

    @override
    def can_handle(self, source: str) -> bool:
        try:
            path = Path(source)
            if path.exists():
                return path.suffix.lower() in EXTENSIONS["Audio"]
        except TypeError:
            return False

    @override
    def parse(self, source: str) -> SourceInfo:
        path = Path(source)
        assert path.exists(), f"File does not exist: {source}"
        # Construct our metadata first
        source_info = SourceInfo(
            source_type=self.source_type,
            uri=f"audio:///{self._get_extension(path)}/{self._compute_hash(path)}",
            original_source=source,
            hash=self._compute_hash(path),
        )
        return source_info

    def _get_extension(self, path: Path) -> str:
        return path.suffix.lower().replace(".", "")

    def _compute_hash(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]
