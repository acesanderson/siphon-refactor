siphon_server/
├── database/
│   ├── __init__.py
│   │
│   ├── postgres/
│   │   ├── __init__.py
│   │   ├── connection.py       # Engine, SessionLocal, get_db
│   │   ├── models.py            # ProcessedContentORM, EmbeddingORM
│   │   ├── converters.py        # to_orm(), from_orm()
│   │   ├── repository.py        # ContentRepository, EmbeddingRepository
│   │   └── migrations/          # Alembic
│   │       ├── alembic.ini
│   │       ├── env.py
│   │       └── versions/
│   │
│   ├── elasticsearch/
│   │   ├── __init__.py
│   │   ├── client.py            # ES connection, index management
│   │   ├── indexer.py           # Sync from Postgres → ES
│   │   ├── queries.py           # Search query builders
│   │   └── mappings.py          # Index definitions/mappings
│   │
│   ├── neo4j/
│   │   ├── __init__.py
│   │   ├── driver.py            # Neo4j connection
│   │   ├── graph_builder.py    # Construct graph from content
│   │   ├── queries.py           # Cypher queries for graph RAG
│   │   └── schema.py            # Node/relationship definitions
│   │
│   ├── vector/
│   │   ├── __init__.py
│   │   ├── embeddings.py        # Generate embeddings (OpenAI, etc.)
│   │   ├── storage.py           # Interface to pgvector operations
│   │   └── retrieval.py         # Similarity search, reranking
│   │
│   └── sync/
│       ├── __init__.py
│       ├── orchestrator.py      # Coordinate cross-DB syncing
│       ├── postgres_to_es.py    # CDC or batch sync handlers
│       └── postgres_to_neo4j.py # Graph construction triggers
│
├── services/
│   ├── __init__.py
│   ├── cache.py
│   ├── content.py               # Business logic for ProcessedContent
│   ├── enrichment.py
│   ├── extraction.py
│   ├── pipeline.py
│   ├── search.py                # Unified search across Postgres/ES/vector
│   └── graph.py                 # Graph RAG operations
│
├── routers/
│   ├── __init__.py
│   ├── content.py
│   ├── health.py
│   ├── search.py
│   └── graph.py                 # Graph query endpoints
│
├── utils/
│   ├── __init__.py
│   ├── hashing.py
│   ├── logging.py
│   └── timing.py
│
├── __init__.py
├── main.py
├── server.py
└── config.py
