from headwater_client.client.headwater_client import HeadwaterClient
from siphon_api.api.siphon_request import SiphonRequest
from siphon_api.api.to_siphon_request import create_siphon_request
from siphon_api.models import ProcessedContent
from pathlib import Path
from typing import Literal
import click
import logging
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


@click.command()
@click.argument("source")
@click.option(
    "--return-type",
    "-r",
    type=click.Choice(["s", "c", "d", "t", "m"]),
    default="s",
    help="Type of data to return: [s]ummary, [c]ontent, [d]escription, [t]itle, [m]etadata",
)
def cli(source: str, return_type: Literal["s", "c", "d", "t", "m"]):
    """
    Process a source (file, URL, etc.)
    """
    logger.info(f"Received source: {source}")
    source = parse_source(source)
    request: SiphonRequest = create_siphon_request(source)
    logger.debug("Loading HeadwaterClient")
    client = HeadwaterClient()
    logger.info("Processing request")
    result: ProcessedContent = client.siphon.process(request)
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
        case "s":
            output_string = result.summary
        case "c":
            output_string = result.text
        case "d":
            output_string = result.description
        case "t":
            output_string = result.title
        case "m":
            import json

            output_string = ""
            output_json = json.dumps(result.content.metadata, indent=2)

    # Print output
    if output_string:
        output_string += "\n\n-----------------------------------------"
        output = Markdown(output_string)
        console.print(output)
    if output_json:
        console.print(output_json)


def main():
    cli()


if __name__ == "__main__":
    main()
