from siphon_api.interfaces import ExtractorStrategy
from siphon_api.models import SourceInfo, ContentData
from siphon_api.enums import SourceType
from siphon_api.metadata import FileMetadata
from siphon_api.file_types import MIME_TYPES
from datetime import datetime, timezone
from pathlib import Path
from typing import override


class AudioExtractor(ExtractorStrategy):
    """Extract content from Audio"""

    source_type: SourceType = SourceType.AUDIO

    @override
    def extract(self, source: SourceInfo) -> ContentData:
        if source.source_type != self.source_type:
            raise ValueError(
                f"Cannot extract source of type {source.source_type} with AudioExtractor"
            )
        text = self._extract(source)
        metadata = self._generate_metadata(source)
        return ContentData(source_type=self.source_type, text=text, metadata=metadata)

    def _extract(self, source: SourceInfo) -> str:
        from siphon_server.sources.audio.pipeline.audio_pipeline import retrieve_audio

        path = Path(source.original_source)

        audio_content = retrieve_audio(Path(source.original_source))
        return audio_content

    def _generate_metadata(self, source: SourceInfo) -> dict[str, str]:
        path = Path(source.original_source)
        metadata = FileMetadata(
            file_name=path.name,
            hash=source.hash,
            created_at=self._get_created_at(path),
            last_modified=self._get_last_modified(path),
            file_size=self._get_file_size(path),
            extension=path.suffix.lower(),
            mime_type=self._get_mime_type(path.suffix.lower()),
        )
        return metadata.model_dump()

    def _get_mime_type(self, extension: str) -> str:
        """
        Get MIME type for given extension.
        """
        return MIME_TYPES.get(extension, "application/octet-stream")

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


if __name__ == "__main__":
    from siphon_server.sources.audio.example import EXAMPLE_MP3, EXAMPLE_WAV
    from siphon_server.sources.audio.parser import AudioParser

    parser = AudioParser()
    for example in [EXAMPLE_MP3, EXAMPLE_WAV]:
        if parser.can_handle(str(example)):
            info = parser.parse(str(example))
            print(info.model_dump_json(indent=4))

    extractor = AudioExtractor()
    for example in [EXAMPLE_MP3, EXAMPLE_WAV]:
        if parser.can_handle(str(example)):
            info = parser.parse(str(example))
            try:
                content = extractor.extract(info)
                print(content.model_dump_json(indent=4))
            except NotImplementedError:
                print(f"Extraction not implemented for {info.source_type}")
