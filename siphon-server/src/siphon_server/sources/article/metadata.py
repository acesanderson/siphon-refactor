from pydantic import BaseModel


class ArticleMetadata(BaseModel):
    """
    Data model for article metadata, tolerant of Trafilatura's variable output.
    """

    # Httpx response
    source_url: str
    final_url: str
    status_code: int
    content_type: str

    # Readabilipy metadata
    title: str
    byline: str | None = None
    dir: str | None = None
    lang: str | None = None
    length: int | None = None
    siteName: str | None = None
