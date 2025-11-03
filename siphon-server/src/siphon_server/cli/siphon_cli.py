"""
NOTE: eventually will make this a thin client (and move to siphon-client library).

Command-line interface for processing diverse content sources into LLM-ready context.

Think of this as `cat` for LLMs. A simple command-line interface to convert files or URLs into
context for LLMs.

This script serves as the primary user-facing entry point for the Siphon system, enabling
users to process files, URLs, and other content sources through the unified extraction and
enrichment pipeline. It orchestrates the SiphonPipeline to automatically detect source type,
extract raw content, and generate AI-enriched summaries, then outputs the result in multiple
formats (raw text, markdown, or specific fields like summary/URI).

The CLI supports flexible workflows including processing new sources with caching, retrieving
previously processed content, and customizing output formatting via command-line flags. It
integrates with the database repository layer to avoid reprocessing duplicate content and
provides configurable logging for debugging pipeline execution.
"""

from siphon_server.core.pipeline import SiphonPipeline
import argparse
import sys
import os
import logging


# Set up logging
log_level = int(os.getenv("PYTHON_LOG_LEVEL", "1"))
levels = {1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
logging.basicConfig(
    level=levels.get(log_level, logging.INFO), format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="siphon file to LLM context")
    parser.add_argument(
        "source", type=str, nargs="?", help="Path to the source (URL, file path, etc.)"
    )
    parser.add_argument(
        "-R",
        "--return_type",
        type=str,
        choices=["c", "s", "u"],
        help="Type of data to return: 'c' (context), 's' (synthetic data), or 'u' (URI). Defaults to 'synthetic_data', i.e. a summary.",
    )
    parser.add_argument(
        "-c",
        "--cache",
        action="store_true",
        default=True,
        help="Use cached content if available. Default is True.",
    )
    parser.add_argument(
        "--raw",
        "-r",
        action="store_true",
        default=False,
        help="Output raw markdown without formatting.",
    )
    parser.add_argument(
        "--last",
        "-l",
        action="store_true",
        help="Load the last processed content from the cache.",
    )
    args = parser.parse_args()
    # Detect if no input; just print help and exit.
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Get ProcessedContent, by various means.
    ## If we just want the last siphon:
    sp = SiphonPipeline()
    if args.last:
        processed_content = sp.get_last_processed_content()
        if not processed_content:
            logger.error("No last processed content found in cache.")
            sys.exit(1)
        if not args.raw:
            output = f"# {processed_content.title}: {processed_content.uri}\n\n{processed_content.summary}"
            from rich.markdown import Markdown
            from rich.console import Console

            console = Console()
            markdown = Markdown(output)
            console.print(markdown)
            sys.exit()
        else:
            print(processed_content.summary)
            sys.exit()
    ## If we want to process a Source:
    if args.source:
        processed_content = sp.process(source=args.source, use_cache=args.cache)
        output = f"# {processed_content.title}: {processed_content.uri}\n\n{processed_content.summary}"
        if args.return_type:
            match args.return_type:
                case "c":
                    output = processed_content.text
                    print(output)
                    sys.exit()
                case "s":
                    output = processed_content.summary
                    print(output)
                    sys.exit()
                case "u":
                    output = processed_content.uri
                    print(output)
                    sys.exit()
                case _:
                    logger.error("Invalid return type specified.")
                    sys.exit(1)
        if not args.raw:
            output = processed_content.summary
            from rich.markdown import Markdown
            from rich.console import Console

            console = Console()
            markdown = Markdown(output)
            console.print(markdown)
            sys.exit()
        elif args.raw:
            print(output)
            sys.exit()


if __name__ == "__main__":
    main()
