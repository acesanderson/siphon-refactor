from siphon_api.interfaces import EnricherStrategy
from siphon_api.models import ContentData, EnrichedData
from siphon_api.enums import SourceType
from typing import override


class DocEnricher(EnricherStrategy):
    """
    Enrich Doc content with LLM
    """
    
    def __init__(self, llm=None):
        # TODO: Inject LLM client
        self.llm = llm
    
    @override
    def enrich(self, content: ContentData) -> EnrichedData:
        # TODO: Implement source-specific enrichment
        raise NotImplementedError
