from siphon_server.config import settings
from siphon_api.models import ContentData
from conduit.sync import Model

PREFERRED_MODEL = settings.default_model


def count_tokens(content: ContentData) -> int:
    model = Model(PREFERRED_MODEL)
    text = content.text
    tokens = model.tokenize(text)
    return len(tokens)


if __name__ == "__main__":
    from siphon_api.enums import SourceType

    sample_content = ContentData(
        source_type=SourceType.DOC,
        text="This is a sample text to count tokens.",
        metadata={},
    )
    token_count = count_tokens(sample_content)
    print(f"Token count: {token_count}")
