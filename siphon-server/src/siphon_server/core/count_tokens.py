from siphon_server.config import settings
from siphon_api.models import ContentData
from conduit.sync import Model
import json

PREFERRED_MODEL = settings.default_model


def count_tokens(content: ContentData) -> int:
    model = Model(PREFERRED_MODEL)
    metadata = json.dumps(content.metadata)
    text = content.text
    input = metadata + "\n" + text
    tokens = model.tokenize(input)
    return tokens
