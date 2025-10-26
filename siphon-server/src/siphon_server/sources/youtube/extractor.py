from siphon_api.interfaces import ExtractorStrategy
from siphon_api.models import SourceInfo, ContentData
from typing import override


class YouTubeExtractor(ExtractorStrategy):
    @override
    def extract(self, source: SourceInfo) -> ContentData:
        video_id = source.metadata["video_id"]

        # Get transcript and metadata via infrastructure
        transcript, metadata = self.client.get_transcript(video_id)

        return ContentData(
            source_type=source.source_type, text=transcript, metadata=metadata
        )
