from siphon_api.interfaces import EnricherStrategy
from siphon_api.models import ContentData, EnrichedData
from siphon_api.enums import SourceType
from typing import override, Any
from pathlib import Path
import logging

# Import necessary classes from conduit; consider lazy imports in future.
from conduit.batch import (
    AsyncConduit,
    ModelAsync,
    Response,
    Verbosity,
    ConduitCache,
)

# Set up cache
cache = ConduitCache(name="siphon")
ModelAsync.conduit_cache = cache
# Set up logging
logger = logging.getLogger(__name__)
# Set root logger to silent
logging.getLogger().setLevel(logging.CRITICAL + 10)

# Constants
PROMPTS_DIR = Path(__file__).parent / "prompts"
PREFERRED_MODEL = "haiku"
VERBOSITY = Verbosity.COMPLETE


class ArticleEnricher(EnricherStrategy):
    """
    Enrich Article content with LLM
    """

    source_type: SourceType = SourceType.ARTICLE

    def __init__(self):
        from conduit.prompt.prompt_loader import PromptLoader

        # Load prompts packaged with this module
        self.prompt_loader = PromptLoader(
            base_dir=PROMPTS_DIR,
        )
        print(f"Loaded prompts: {self.prompt_loader.keys}")

    @override
    def enrich(self, content: ContentData) -> EnrichedData:
        logger.info("Enriching Article content")
        input_variables = {"text": content.text, "metadata": content.metadata}
        source_type = SourceType.ARTICLE
        title = content.metadata["title"]
        logger.info(f"Generated title: {title}")
        # Assemble prompt strings
        prompt_strings = []
        description = self._generate_description_prompt(input_variables)
        logger.info(f"Generated description: {description}")
        summary = self._generate_summary_prompt(input_variables)
        logger.info(f"Generated summary: {summary[:100]}...")
        prompt_strings.extend([description, summary])
        # Run the chain
        model = ModelAsync(model="haiku")
        conduit = AsyncConduit(model=model)
        responses = conduit.run(prompt_strings=prompt_strings, verbose=VERBOSITY)
        assert all(isinstance(r, Response) for r in responses), (
            "All responses must be of type Response"
        )
        description = str(responses[0].content)
        summary = str(responses[1].content)
        # Construct enriched data
        enriched_data = EnrichedData(
            source_type=source_type,
            title=title,
            description=description,
            summary=summary,
            topics=[],
            entities=[],
        )
        logger.info("Enrichment complete")
        return enriched_data

    def _generate_title(self, input_variables: dict[str, Any]) -> str:
        title = input_variables["metadata"]["title"]
        return title

    def _generate_description_prompt(self, input_variables: dict[str, Any]) -> str:
        print(self.prompt_loader.keys)
        prompt = self.prompt_loader["article_description"]
        return prompt.render(input_variables)

    def _generate_summary_prompt(self, input_variables: dict[str, Any]) -> str:
        prompt = self.prompt_loader["article_summary"]
        return prompt.render(input_variables)
