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

logger = logging.getLogger(__name__)
# Set up cache
CACHE = ConduitCache(name="siphon")
ModelAsync.conduit_cache = CACHE
# Constants
PROMPTS_DIR = Path(__file__).parent / "prompts"
PREFERRED_MODEL = "haiku"
VERBOSITY = Verbosity.COMPLETE


class AudioEnricher(EnricherStrategy):
    """
    Enrich Audio content with LLM
    """

    source_type: SourceType = SourceType.AUDIO

    def __init__(self):
        if content.source_type != self.source_type:
            raise ValueError(
                f"AudioEnricher can only enrich content of type {self.source_type}, got {content.source_type} instead."
            )
        from conduit.prompt.prompt_loader import PromptLoader

        # Load prompts packaged with this module
        self.prompt_loader = PromptLoader(
            base_dir=PROMPTS_DIR,
        )
        print(f"Loaded prompts: {self.prompt_loader.keys}")

    @override
    def enrich(self, content: ContentData) -> EnrichedData:
        """
        Enrich audio transcript content with LLM-generated metadata.

            Generates a semantic description, summary, and title for audio content by rendering
            audio-specific prompts through a language model. Uses async batch processing for
            description and summary, then synchronously generates a title from the description.

            Args:
                content: ContentData containing transcript text and file metadata to enrich.

            Returns:
                EnrichedData with generated title, description, summary, and empty topics/entities lists.

            Raises:
                AssertionError: If LLM responses are not of type Response or if title generation fails.
        """
        logger.info("Enriching Doc content with specialized prompts")
        description_prompt = self.prompt_loader["audio_description"]
        summary_prompt = self.prompt_loader["audio_summary"]
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
    from siphon_server.sources.audio.example import EXAMPLE_MP3, EXAMPLE_WAV
    from siphon_server.sources.audio.parser import AudioParser
    from siphon_server.sources.audio.extractor import AudioExtractor

    parser = AudioParser()
    for example in [EXAMPLE_MP3, EXAMPLE_WAV]:
        if parser.can_handle(str(example)):
            info = parser.parse(str(example))
            print(info.model_dump_json(indent=4))

    extractor = AudioExtractor()
    for example in [EXAMPLE_MP3, EXAMPLE_WAV]:
        if parser.can_handle(str(example)):
            info = parser.parse(str(example))
            try:
                content = extractor.extract(info)
                print(content.model_dump_json(indent=4))
            except NotImplementedError:
                print(f"Extraction not implemented for {info.source_type}")

    enricher = AudioEnricher()
    for example in [EXAMPLE_MP3, EXAMPLE_WAV]:
        if parser.can_handle(str(example)):
            info = parser.parse(str(example))
            try:
                content = extractor.extract(info)
                enriched = enricher.enrich(content)
                print(enriched.model_dump_json(indent=4))
            except NotImplementedError:
                print(f"Enrichment not implemented for {info.source_type}")
