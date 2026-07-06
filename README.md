# Siphon

Siphon is a unified document and media ingestion engine with hybrid semantic search capabilities. It parses, extracts, and enriches unstructured content from diverse sources—including PDFs, web articles, raw audio, video, YouTube, GitHub repositories, and Obsidian vaults—and stores them as vector-enabled, highly structured records in a PostgreSQL database.

## Quick Start

Siphon is organized as a Python monorepo managed with `uv`.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourorg/siphon.git
   cd siphon
   ```

2. Synchronize workspace dependencies:
   ```bash
   uv sync
   ```

3. Configure required environment variables:
   ```bash
   export POSTGRES_USERNAME="your_user"
   export POSTGRES_PASSWORD="your_password"
   export HUGGINGFACEHUB_API_TOKEN="your_hf_token"
   ```

4. Initialize the PostgreSQL schema and indexes:
   ```bash
   python -m siphon_server.database.postgres.setup
   ```

### Programmatic Usage

Execute the core ingestion pipeline programmatically using Python async tasks:

```python
import asyncio
from siphon_server.core.pipeline import SiphonPipeline
from siphon_api.enums import ActionType

async def main():
    pipeline = SiphonPipeline()
    
    # Process, enrich, and persist a source document to PostgreSQL
    result = await pipeline.process(
        source="https://arxiv.org/abs/2301.07041",
        action=ActionType.GULP,
        use_cache=False
    )
    
    print(f"Title: {result.enrichment.title}")
    print(f"Summary:\n{result.enrichment.summary}")

if __name__ == "__main__":
    asyncio.run(main())
```

### CLI Usage

Ingest and semantically query content directly from the command line:

```bash
# Gulp a YouTube video (downloads metadata, retrieves transcripts, enriches, and stores)
siphon gulp "https://www.youtube.com/watch?v=OkEGJ5G3foU"

# Query the database using Hybrid RRF (BM25 Lexical + Cosine Semantic Search)
siphon query "AI engineering tutorial" --mode hybrid
```

---

## Core Value Demonstration

Siphon handles complex real-world media extraction and enrichment pipeline issues, such as rate-limiting bypasses, GPU-accelerated speaker diarization, visual asset descriptions, and hybrid indexing. 

Below is a demonstration of processing heterogeneous data streams:

```bash
# 1. Sync an entire Obsidian vault with client-side mtime change detection
siphon sync --vault ~/my-obsidian-vault --concurrency 10

# 2. Extract content from a heavy PDF containing charts and tables using Docling + OCR
siphon gulp /path/to/annual_report.pdf --return-type json

# 3. Query across all processed sources with HyDE (Hypothetical Document Embeddings) enabled
siphon query "Q3 revenue projections and visual charts description" --type doc --mode hybrid

# 4. Recall last query index to display or open source references
siphon query --get 1 --return-type s
```

---

## Architecture Overview

Siphon decouples processing into client commands, API exchange structures, and high-performance server processing pipelines.

```
                  ┌──────────────────────────────┐
                  │          CLI Client          │
                  └──────────────┬───────────────┘
                                 │ SiphonRequest
                                 ▼
                  ┌──────────────────────────────┐
                  │     Siphon Server Pipeline   │
                  └──────────────┬───────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Parsers     │     │   Extractors    │     │    Enrichers    │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ URL/Path Norm   │     │ Docling, VLM,   │     │ Routing         │
│ UUID Generation │     │ Whisper,        │     │ Summarizer,     │
│ Schema Route    │     │ Trafilatura     │     │ HyDE Descriptor │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │ ProcessedContent
                                 ▼
                  ┌──────────────────────────────┐
                  │    PostgreSQL (pgvector)     │
                  ├──────────────────────────────┤
                  │ Lexical computed tsvector    │
                  │ Cosine HNSW Vector (768-dim) │
                  └──────────────────────────────┘
```

### 1. Ingestion Pipeline Phases
*   **Parse**: Analyzes URL/Path parameters, strips tracking strings, and resolves them to canonical custom URI formats (e.g., `doc:///docx/hash`, `youtube:///id`).
*   **Extract**: Executes source-specific content converters. PDFs and Doc files undergo layout tree recovery, table reconstruction, OCR validation, and vision-model-assisted chart/diagram descriptions. Audio and video files utilize GPU sidecars running Whisper and PyAnnote for transcription and diarization.
*   **Enrich**: Translates raw text inputs into dual semantic outputs: a structured Markdown summary and a dense, retrieval-optimized description mapped to answer-voice patterns (HyDE).
*   **Store**: Writes outputs to the database. Updates clear pre-calculated embeddings and resets existing vector indices to ensure data parity.

---

## Installation & Setup

### System Prerequisites
*   **Python**: Version 3.12 or 3.13.
*   **Database**: PostgreSQL 16+ with the `pgvector` extension installed.
*   **System Binaries**: `ffmpeg` (required for audio and video extraction).
*   **GPU Sidecars (Optional)**: Docker/Docker Compose for local execution of speech-to-text, speaker diarization, or local diffusion services.

### Configuration
Configure Siphon via environment variables or by creating a configuration file at `~/.config/siphon/config.toml`.

| Environment Variable | Description | Default |
| :--- | :--- | :--- |
| `POSTGRES_USERNAME` | Username for database access | None (Required) |
| `POSTGRES_PASSWORD` | Password for database access | None (Required) |
| `HUGGINGFACEHUB_API_TOKEN` | API Token for Hugging Face (PyAnnote weights) | None (Required) |
| `YOUTUBE_API_KEY2` | Google Cloud API key for YouTube Data client | None |
| `SIPHON_DEFAULT_MODEL` | Default LLM model for text completion and summarization | `gemma4:latest` |
| `SIPHON_DOCLING_VLM_URL` | Endpoint of the Vision-Language Model service | `http://localhost:11434/v1/chat/completions` |

---

## Basic Usage

The `siphon` command is organized into functional groups.

### Core CLI Commands

| Command | Arguments | Options | Description |
| :--- | :--- | :--- | :--- |
| `gulp` | `[SOURCE]` | `-r [st/u/c/m/t/d/s/id/json]` | Fully ingests, enriches, and stores a source document. Returns specified fields. |
| `parse` | `[SOURCE]` | `-r [u/st]` | Validates a source string and returns its canonical Siphon URI. |
| `extract` | `[SOURCE]` | `-r [c/m/to]`, `--diarize` | Extracts raw transcript/text without database storage. |
| `enrich` | `[SOURCE]` | `-r [s/d/t]` | Enriches raw inputs into summary/description metrics without storage. |
| `query` | `[QUERY]` | `--type`, `--mode`, `--limit`, `--get`, `--open` | Executes semantic or lexical hybrid search over ingested entries. |
| `results` | None | `--history`, `--get [ID]`, `--limit` | Reviews CLI search query history and re-loads matching document arrays. |
| `sync` | None | `--vault [PATH]`, `--dry-run`, `--install-hook` | Walk, delta-evaluate, and bulk-ingest an Obsidian Markdown vault. |
| `traverse` | `[NODE]` | `--depth`, `--backlinks` | Explores the internal wikilink reference graph starting at a defined URI node. |
| `inspect` | `[URI]` | `--json` | Retrieves pipeline metrics, tracing records, and prompt tokens for debugging. |

### Querying the Database

Query the stored knowledge base using various retrieval modes:

```bash
# Semantic Vector-Only Search
siphon query "adversarial attacks on large language models" --mode semantic --limit 5

# Lexical BM25 FTS-Only Search
siphon query "RoutingSummarizer" --mode fts

# Hybrid RRF Fusion with Date Filters
siphon query "machine learning guidelines" --mode hybrid --date ">2024-06-01"
```

If the results are shown as a table, use the index number with `--get` to retrieve full elements:

```bash
# Fetch the full summary of result #2 from the last search
siphon query --get 2 -r s
```
