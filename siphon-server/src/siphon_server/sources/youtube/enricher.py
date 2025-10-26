from siphon_api.interfaces import EnricherStrategy
from siphon_api.models import ContentData, EnrichedData
from typing import override


class YouTubeEnricher(EnricherStrategy):
    @override
    def enrich(self, content: ContentData) -> EnrichedData:
        # Implement YouTube-specific enrichment logic here
        ...
