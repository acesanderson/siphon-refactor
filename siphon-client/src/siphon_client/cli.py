import click
from siphon_client.client import SiphonClient
from siphon_client.display import display_content


@click.group()
def cli():
    """Siphon CLI - Universal content ingestion"""
    pass


@cli.command()
@click.argument("source")
@click.option("--no-cache", is_flag=True, help="Skip cache")
@click.option("--server", default="http://localhost:8000", help="Server URL")
def process(source: str, no_cache: bool, server: str):
    """Process a source (file, URL, etc.)"""
    client = SiphonClient(base_url=server)
    result = client.process(source, use_cache=not no_cache)
    display_content(result)


@cli.command()
@click.option("--source-type", help="Filter by source type")
@click.option("--tags", help="Filter by tags (comma-separated)")
@click.option("--since", help="Filter by date (e.g., 7d, 2024-01-01)")
@click.option("--server", default="http://localhost:8000")
def query(source_type: str, tags: str, since: str, server: str):
    """Query stored content"""
    client = SiphonClient(base_url=server)
    tag_list = tags.split(",") if tags else None
    results = client.query(source_type=source_type, tags=tag_list, since=since)

    for result in results:
        display_content(result)
        click.echo("\n" + "=" * 80 + "\n")


def main():
    cli()


if __name__ == "__main__":
    main()
