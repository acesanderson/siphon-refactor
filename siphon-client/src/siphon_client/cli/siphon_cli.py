from headwater_client.client.headwater_client import HeadwaterClient
from siphon_api.api.siphon_request import SiphonRequest, SiphonRequestParams
from siphon_api.api.to_siphon_request import create_siphon_request
from siphon_api.api.siphon_response import SiphonResponse
from siphon_api.models import (
    SourceInfo,
    ContentData,
    EnrichedData,
    ProcessedContent,
    PipelineClass,
)
from pathlib import Path
from typing import Literal
import click
import logging
import json
import os

# Set up logging
log_level = int(os.getenv("PYTHON_LOG_LEVEL", "1"))
levels = {1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
logging.basicConfig(
    level=levels.get(log_level, logging.INFO), format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def parse_source(source: str) -> str:
    try:
        logger.debug(f"Parsing source: {source}")
        path = Path(source)
        if path.exists():
            logger.debug(f"Resolved path: {path.resolve()}")
            return str(path.resolve())
        logger.debug(f"Source is not a file path: {source}")
        return source
    except Exception:
        logger.debug(f"Source is not a file path: {source}")
        return source


@click.group()
def siphon():
    """
    Process, persist, or extract content from various sources.
    """
    ...


@siphon.command()
@click.argument("source")
@click.option(
    "--return-type",
    "-r",
    type=Literal["st", "u", "c", "m", "t", "d", "s", "pc"],
    default="s",
    help="Type to return: [st] source type, [u] URI, [c] content, [m] metadata, [t] title, [d] description, [s] summary, [pc] processed content.",
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable caching for this request",
)
def gulp(
    source: str,
    return_type: Literal["st", "u", "c", "m", "t", "d", "s", "pc"],
    no_cache: bool,
):
    """
    Process a source and persist the results (e.g., DB, embeddings).
    This is also an importable function for programmatic use (if you want a ProcessedContent object).
    """
    logger.info(f"Received source: {source}")
    source = parse_source(source)
    requested_object = ProcessedContent.kind
    params: SiphonRequestParams = SiphonRequestParams(
        action="gulp", return_type=requested_object, use_cache=not no_cache
    )
    request: SiphonRequest = create_siphon_request(
        source=source,
        request_params=params,
    )  # Note the double negative for no_cache
    logger.debug("Loading HeadwaterClient")
    client = HeadwaterClient()
    logger.info("Processing request")
    response: SiphonResponse = client.siphon.process(request)
    payload: PipelineClass = response.payload
    assert isinstance(payload, ProcessedContent), (
        f"Expected ProcessedContent, got {type(payload)}"
    )
    logger.info("Processing complete")
    # Display output based on return_type
    from rich.console import Console
    from rich.markdown import Markdown

    console = Console()
    # Prepare output -- either string or JSON
    output_string = ""
    output_json = ""
    # Route based on return_type
    match return_type:
        case "st":
            output_string = payload.source_type
        case "u":
            output_string = payload.uri
        case "c":
            output_string = payload.text
        case "m":
            output_string = ""
            output_json = json.dumps(payload.metadata, indent=2)
        case "t":
            output_string = payload.title
        case "d":
            output_string = payload.description
        case "s":
            output_string = payload.summary
        case "pc":
            output_json = payload.model_dump_json(indent=2)
    # Print output
    if output_string:
        output_string += "\n\n-----------------------------------------"
        output = Markdown(output_string)
        console.print(output)
    if output_json:
        console.print(output_json)


@siphon.command()
@click.argument("source")
@click.option(
    "--return-type",
    "-r",
    type=Literal["u", "st"],
    default="u",
    help="Type to return: [u] URI, [st] source type.",
)
def parse(source: str, return_type: Literal["u", "st"]):
    """
    Parse a source and return the resolved URI (ephemeral).
    """
    logger.info(f"Received source for parsing: {source}")
    source = parse_source(source)
    requested_object = SourceInfo.kind
    params: SiphonRequestParams = SiphonRequestParams(
        action="parse",
        return_type=requested_object,
    )
    request: SiphonRequest = create_siphon_request(
        source=source,
        request_params=params,
    )
    logger.debug("Loading HeadwaterClient")
    client = HeadwaterClient()
    logger.info("Processing request")
    response: SiphonResponse = client.siphon.process(request)
    payload: PipelineClass = response.payload
    assert isinstance(payload, SourceInfo), f"Expected SourceInfo, got {type(payload)}"
    logger.info("Processing complete")
    # Display output based on return_type
    from rich.console import Console
    from rich.markdown import Markdown

    console = Console()
    match return_type:
        case "u":
            output_string = payload.uri
        case "st":
            output_string = payload.source_type

    output_string += "\n\n-----------------------------------------"
    output = Markdown(output_string)
    console.print(output)


@siphon.command()
@click.argument("source")
@click.option(
    "--return-type",
    "-r",
    type=Literal["c", "m"],
    default="c",
    help="Type to return: [c]ontent, [m]etadata.",
)
def extract(source: str, return_type: Literal["c", "m"]):
    """
    Extract content from a source without persisting (ephemeral).
    """
    logger.info(f"Received source for extraction: {source}")
    source = parse_source(source)
    requested_object = ContentData.kind
    params: SiphonRequestParams = SiphonRequestParams(
        action="extract",
        return_type=requested_object,
    )
    request: SiphonRequest = create_siphon_request(
        source=source,
        request_params=params,
    )
    logger.debug("Loading HeadwaterClient")
    client = HeadwaterClient()
    logger.info("Processing request")
    response: SiphonResponse = client.siphon.process(request)
    payload: PipelineClass = response.payload
    assert isinstance(payload, ContentData), (
        f"Expected ContentData, got {type(payload)}"
    )
    logger.info("Processing complete")
    # Display output based on return_type
    from rich.console import Console
    from rich.markdown import Markdown

    console = Console()
    match return_type:
        case "c":
            output_string = payload.text
            output_string += "\n\n-----------------------------------------"
            output = Markdown(output_string)
            console.print(output)
        case "m":
            output_json = json.dumps(payload.metadata, indent=2)
            console.print(output_json)


@siphon.command()
@click.argument("source")
@click.option(
    "--return-type",
    "-r",
    type=Literal["s", "d", "t"],
    default="s",
    help="Type to return: [s]ummary, [d]escription, [t]itle.",
)
def enrich(source: str, return_type: Literal["s", "d", "t"]):
    """
    Enrich a source without persisting (ephemeral).
    """
    logger.info(f"Received source for enrichment: {source}")
    source = parse_source(source)
    requested_object = EnrichedData.kind
    params: SiphonRequestParams = SiphonRequestParams(
        action="enrich",
        return_type=requested_object,
    )
    request: SiphonRequest = create_siphon_request(
        source=source,
        request_params=params,
    )
    logger.debug("Loading HeadwaterClient")
    client = HeadwaterClient()
    logger.info("Processing request")
    response: SiphonResponse = client.siphon.process(request)
    payload: PipelineClass = response.payload
    assert isinstance(payload, EnrichedData), (
        f"Expected EnrichedData, got {type(payload)}"
    )
    logger.info("Processing complete")
    # Display output based on return_type
    from rich.console import Console
    from rich.markdown import Markdown

    console = Console()
    match return_type:
        case "s":
            output_string = payload.summary
        case "d":
            output_string = payload.description
        case "t":
            output_string = payload.title

    output_string += "\n\n-----------------------------------------"
    output = Markdown(output_string)
    console.print(output)


def main():
    siphon()


if __name__ == "__main__":
    main()
