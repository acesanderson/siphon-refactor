from siphon_api.interfaces import EnricherStrategy
from siphon_api.models import ContentData, EnrichedData
from siphon_api.enums import SourceType
from typing import override, Any
from pathlib import Path
import logging

# Import necessary classes from conduit; consider lazy imports in future.
from conduit.batch import (
    AsyncConduit,
    Prompt,
    ModelAsync,
    Response,
    Verbosity,
    ConduitCache,
)
from conduit.sync import Model

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


class DocEnricher(EnricherStrategy):
    """
    Enrich Doc content with LLM
    """

    source_type: SourceType = SourceType.DOC

    def __init__(self):
        from conduit.prompt.prompt_loader import PromptLoader

        # Load prompts packaged with this module
        self.prompt_loader = PromptLoader(
            base_dir=PROMPTS_DIR,
        )
        print(f"Loaded prompts: {self.prompt_loader.keys}")

    @override
    def enrich(self, content: ContentData) -> EnrichedData:
        logger.info("Routing Doc content based on MIME type")
        mime_type = content.metadata["mime_type"]

        # Route to specialized prompt
        if mime_type.startswith("text/x-"):  # Code
            return self._enrich_code(content)
        elif "spreadsheet" in mime_type or mime_type == "text/csv":
            return self._enrich_data(content)
        elif "presentation" in mime_type:
            return self._enrich_presentation(content)
        else:  # Default: prose documents
            return self._enrich_prose(content)

    def _enrich_code(self, content: ContentData) -> EnrichedData:
        description_prompt = self.prompt_loader["code_description"]
        summary_prompt = self.prompt_loader["code_summary"]
        return self._enrich_with_prompts(content, description_prompt, summary_prompt)

    def _enrich_data(self, content: ContentData) -> EnrichedData:
        description_prompt = self.prompt_loader["data_description"]
        summary_prompt = self.prompt_loader["data_summary"]
        return self._enrich_with_prompts(content, description_prompt, summary_prompt)

    def _enrich_presentation(self, content: ContentData) -> EnrichedData:
        description_prompt = self.prompt_loader["presentation_description"]
        summary_prompt = self.prompt_loader["presentation_summary"]
        return self._enrich_with_prompts(content, description_prompt, summary_prompt)

    def _enrich_prose(self, content: ContentData) -> EnrichedData:
        description_prompt = self.prompt_loader["prose_description"]
        summary_prompt = self.prompt_loader["prose_summary"]
        return self._enrich_with_prompts(content, description_prompt, summary_prompt)

    def _enrich_with_prompts(
        self,
        content: ContentData,
        description_prompt: Prompt,
        summary_prompt: Prompt,
    ) -> EnrichedData:
        logger.info("Enriching Doc content with specialized prompts")
        title_prompt = self.prompt_loader[
            "title"
        ]  # Title prompt is universal; takes description as input variable
        # Start with description and summary
        input_variables = {"text": content.text, "metadata": content.metadata}
        source_type = SourceType.DOC
        # Assemble prompt strings
        prompt_strings = []
        description_prompt_str = description_prompt.render(input_variables)
        logger.info(f"Generated description prompt")
        summary_prompt_str = summary_prompt.render(input_variables)
        logger.info(f"Generated summary prompt")
        prompt_strings.extend([description_prompt_str, summary_prompt_str])
        # Run the chain
        model = ModelAsync(model=PREFERRED_MODEL)
        conduit = AsyncConduit(model=model)
        responses = conduit.run(prompt_strings=prompt_strings, verbose=VERBOSITY)
        assert all(isinstance(r, Response) for r in responses), (
            "All responses must be of type Response"
        )
        description = str(responses[0].content)
        summary = str(responses[1].content)
        # Generate title from description; this is sync.
        title_prompt_str = title_prompt.render({"description": description})
        model_sync = Model(model=PREFERRED_MODEL)
        response = model_sync.query(query_input=title_prompt_str, verbose=VERBOSITY)
        assert isinstance(response, Response), "Title response must be of type Response"
        title = str(response.content)
        logger.info(f"Generated title from description")

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

    def _generate_topics(self, input_variables: dict[str, Any]) -> list[str]: ...

    def _generate_entities(self, input_variables: dict[str, Any]) -> list[str]: ...


if __name__ == "__main__":
    from pathlib import Path

    ASSETS_DIR = Path(__file__).parent.parent.parent.parent.parent / "assets"
    EXAMPLE_PDF = ASSETS_DIR / "basic-text.pdf"

    from siphon_server.sources.doc.parser import DocParser

    parser = DocParser()
    assert EXAMPLE_PDF.exists(), "Example file does not exist"
    assert parser.can_handle(str(EXAMPLE_PDF)), "Parser cannot handle the example file"
    source_info = parser.parse(str(EXAMPLE_PDF))
    print(source_info.model_dump_json(indent=2))

    print("-" * 40)

    from siphon_server.sources.doc.extractor import DocExtractor

    extractor = DocExtractor()
    content_data = extractor.extract(source_info)
    print(content_data.model_dump_json(indent=2))

    print("-" * 40)

    enricher = DocEnricher()
    enriched_data = enricher.enrich(content_data)
    print(enriched_data.model_dump_json(indent=2))
