from headwater_client.client.headwater_client import HeadwaterClient
from siphon_api.api.to_siphon_request import create_siphon_request
from pathlib import Path
import click
import logging
import os

# Set up logging
log_level = int(os.getenv("PYTHON_LOG_LEVEL", "1"))  # Default to WARNING
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
def cli(source: str):
    """
    Process a source (file, URL, etc.)
    """
    logger.info(f"Received source: {source}")
    source = parse_source(source)
    request = create_siphon_request(source)
    logger.debug("Loading HeadwaterClient")
    client = HeadwaterClient()
    logger.info("Processing request")
    result = client.siphon.process(request)
    logger.info("Processing complete")
    click.echo(result)


def main():
    cli()


if __name__ == "__main__":
    main()
