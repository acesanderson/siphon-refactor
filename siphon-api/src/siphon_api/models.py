from pydantic import BaseModel, Field
from siphon_api.enums import SourceType
from typing import Any


class SourceInfo(BaseModel):
    """
    Parsed source metadata. Replaces all URI subclasses.
    """

    source_type: SourceType
    uri: str  # Canonical identifier (e.g., "youtube:///dQw4w9WgXcQ")
    original_source: str  # User input (e.g., "https://youtube.com/watch?v=dQw4w9WgXcQ")
    hash: str | None = None


class ContentData(BaseModel):
    """
    Extracted content. Replaces all Context subclasses.
    """

    source_type: SourceType
    text: str  # The actual content (transcript, article text, file contents)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EnrichedData(BaseModel):
    """
    AI-generated enrichments. Replaces all SyntheticData subclasses.
    """

    source_type: SourceType
    title: str = ""
    description: str = ""
    summary: str = ""
    topics: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)


class ProcessedContent(BaseModel):
    """
    Final aggregate - main output of Siphon pipeline.
    """

    source: SourceInfo
    content: ContentData
    enrichment: EnrichedData
    tags: list[str] = Field(default_factory=list)
    created_at: int
    updated_at: int

    # Convenience properties
    @property
    def uri(self) -> str:
        return self.source.uri

    @property
    def title(self) -> str:
        return self.enrichment.title

    @property
    def text(self) -> str:
        return self.content.text

    @property
    def summary(self) -> str:
        return self.enrichment.summary
