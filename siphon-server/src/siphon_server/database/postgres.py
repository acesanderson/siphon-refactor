from dbclients.clients.postgres import get_postgres_client
from siphon_api.models import ProcessedContent
import json


def init_table():
    """Create the processed_content cache table if it doesn't exist."""
    with get_postgres_client("context_db")() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_content (
                uri TEXT PRIMARY KEY,
                data JSONB NOT NULL,
                created_at BIGINT NOT NULL,
                updated_at BIGINT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_processed_content_uri ON processed_content(uri);
        """)
        conn.commit()
        cursor.close()


def set(content: ProcessedContent):
    """Cache a ProcessedContent object, upserting by URI."""
    with get_postgres_client("context_db")() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO processed_content (uri, data, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (uri) DO UPDATE SET
                data = EXCLUDED.data,
                updated_at = EXCLUDED.updated_at
        """,
            (
                content.source.uri,
                json.dumps(content.model_dump()),  # This handles ALL nesting
                content.created_at,
                content.updated_at,
            ),
        )
        conn.commit()
        cursor.close()


def get(uri: str) -> ProcessedContent | None:
    """Retrieve cached ProcessedContent by URI."""
    with get_postgres_client("context_db")() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM processed_content WHERE uri = %s", (uri,))
        row = cursor.fetchone()
        cursor.close()
        return ProcessedContent(**json.loads(row[0])) if row else None
