from pydantic import BaseModel


class ArticleMetadata(BaseModel):
    """
    Data model for article metadata, tolerant of Trafilatura's variable output.
    """

    title: str | None = None
    author: str | list[str] | None = None
    hostname: str | None = None
    date: str | int | None = None  # ISO string or timestamp
    raw_text: str | None = None
    fingerprint: str | None = None
    image: str | None = None
    pagetype: str | None = None
    source: str | None = None
    source_hostname: str | None = None
    excerpt: str | None = None
    categories: str | list[str] | None = None
    tags: str | list[str] | None = None
    id: str | None = None
    license: str | None = None
    comments: str | None = None
    language: str | None = None

    def normalize(self) -> "ArticleMetadata":
        """
        Normalize list-valued fields into comma-separated strings
        for consistent downstream representation.
        """

        def _flatten(value) -> str | None:
            return ", ".join(value) if isinstance(value, list) else value

        self.author = _flatten(self.author)
        self.categories = _flatten(self.categories)
        self.tags = _flatten(self.tags)
        return self
