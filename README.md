# Siphon

A universal content ingestion pipeline that extracts, processes, and enriches data from any source.

Siphon provides a robust server-side pipeline to handle various content types—such as web articles, YouTube videos, and local documents—and a simple client for interaction. It parses the source, extracts the core content, and uses an LLM to generate a title, description, and summary.

## Quick Start

This guide assumes you have Docker and Docker Compose installed. The quickest way to get Siphon running is by using the provided services.

**1. Run the Server**

First, create a `.env` file in the project root for database credentials:

```bash
# .env
POSTGRES_USERNAME=user
POSTGRES_PASSWORD=yoursecurepassword
```

Then, launch the Siphon server and its PostgreSQL database:

```bash
# This command is hypothetical as no docker-compose.yml was provided.
# It represents the ideal one-click setup.
docker-compose up -d
```

The Siphon API will be available at `http://localhost:8000`.

**2. Install and Use the Client**

Install the client in a virtual environment:

```bash
# From the siphon-client/ directory
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Now, process any source with a single command:

```bash
siphon process "https://www.youtube.com/watch?v=6ctoS84iFCw"
```

## Core Features

Siphon normalizes unstructured data from various sources into a consistent, enriched format.

### Process Web Articles

Extract the main content from a news article or blog post, stripping away ads and boilerplate.

```bash
siphon process "https://blog.sshh.io/p/how-i-use-every-claude-code-feature"
```

**Example Output:**

```text
Title: Mastering Claude: A Developer's Guide to AI-Powered Coding

Description:
A comprehensive guide on leveraging all of Claude's coding-related
features, including prompt engineering, context management, and debugging
strategies to enhance developer productivity.

Summary:
The article provides an in-depth walkthrough of the author's personal
workflow for using Anthropic's Claude AI as a coding assistant. It
covers techniques for providing effective context, such as using terminal
commands like `tree` and `cat` to give the model a clear understanding of
the project structure and relevant files. The author emphasizes an
iterative approach to prompt engineering, starting broad and refining
prompts based on the AI's output. Key use cases demonstrated include
scaffolding new code, refactoring existing logic, writing documentation,
and debugging complex issues. The guide serves as a practical handbook
for developers looking to integrate Claude more deeply into their daily
coding tasks to improve efficiency and code quality.
```

### Transcribe and Summarize YouTube Videos

Provide a YouTube URL to get a full transcript, summary, and key metadata.

```bash
siphon process "https://www.youtube.com/watch?v=37f0ALZg-XI"
```

### Ingest Local Documents

Process local files like PDFs, Word documents, and text files. Siphon extracts the text content and enriches it just like any online source.

```bash
siphon process "/path/to/your/research-paper.pdf"
```

## How It Works

Siphon operates on a client-server model. The `siphon-server` contains all the complex logic, while the `siphon-client` acts as a lightweight interface for sending sources to the server.

The server's core is a three-stage pipeline:

1.  **Parse**: A `Parser` identifies the source type (e.g., YouTube, Article, Doc) from the input string (a URL or file path) and normalizes it into a canonical URI.
2.  **Extract**: An `Extractor` takes the parsed source information, fetches the raw content (e.g., downloads the article text, gets the video transcript), and extracts key metadata.
3.  **Enrich**: An `Enricher` sends the extracted text to a Large Language Model (LLM) to generate a clean title, a concise one-sentence description, and a detailed summary.

The architecture is designed to be extensible. Adding a new source type (e.g., a GitHub repository) only requires implementing the three `Strategy` interfaces (`Parser`, `Extractor`, `Enricher`) in a new module.

```text
+----------------+      +-------------------------------------------------------------+
|                |      | Siphon Server (FastAPI)                                     |
|  Siphon Client |----->| +---------------------------------------------------------+ |
| (CLI / Python) |      | | Siphon Pipeline                                         | |
|                |      | |                                                         | |
+----------------+      | |  Parse   ->   Extract   ->   Enrich                     | |
|                |      | | (URL/Path)   (Content)      (LLM Summary)               | |
|                |      | |                                                         | |
|                |      | +------------------^------------------------------------+ |
|                |      |                    | (Pluggable Source Modules)         | |
|                |      | +------------------+------------------+------------------+ |
|                |      | |     Article      |      YouTube     |       Doc        | |
|                |      | +------------------+------------------+------------------+ |
+----------------+      +---------------------------------|---------------------------+
                                                  |
                                                  v
                                      +---------------------+
                                      |     PostgreSQL      |
                                      | (with pgvector)     |
                                      +---------------------+
```

## Installation and Setup

### Prerequisites

*   Python 3.10+
*   PostgreSQL 14+ (the `pgvector` extension is recommended)
*   Access to an LLM provider compatible with the `conduit` library.

### Server Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/siphon.git
    cd siphon/siphon-server
    ```

2.  **Set Environment Variables**
    Create a `.env` file in the `siphon-server` directory. The application requires database credentials and may require API keys for external services.
    ```bash
    # .env
    POSTGRES_USERNAME=user
    POSTGRES_PASSWORD=yoursecurepassword

    # Required for youtube-transcript-api to avoid rate-limiting
    WEBSHARE_USERNAME=your_webshare_user
    WEBSHARE_PASS=your_webshare_pass
    ```

3.  **Install Dependencies**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt # Assuming a requirements.txt exists
    ```

4.  **Initialize the Database**
    Run the setup script to create the necessary tables in your PostgreSQL database.
    ```bash
    python -m siphon_server.database.postgres.setup
    ```

5.  **Run the Server**
    ```bash
    uvicorn siphon_server.server.app:app --host 0.0.0.0 --port 8000
    ```

### Client Setup

1.  **Navigate to the Client Directory**
    ```bash
    cd ../siphon-client
    ```

2.  **Install the Client**
    It is recommended to install the client in a separate virtual environment.
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```

## Usage

### Command-Line Interface (CLI)

The CLI is the primary way to interact with Siphon.

| Command             | Description                                                               |
| ------------------- | ------------------------------------------------------------------------- |
| `siphon process`    | Process a new source. Accepts a URL or a local file path.                 |
| `siphon query`      | Query content already stored in the database.                             |

**`process` Options**

| Option        | Description                                       |
| ------------- | ------------------------------------------------- |
| `--no-cache`  | Force reprocessing and ignore any cached results. |
| `--server`    | Specify the Siphon server URL. Defaults to `http://localhost:8000`. |

### Python Client

The `SiphonClient` can be used directly in Python scripts for programmatic access.

```python
from siphon_client.client import SiphonClient

# Initialize the client
client = SiphonClient(base_url="http://localhost:8000")

# Process a web article
article_url = "https://example.blog/my-latest-post"
try:
    processed_article = client.process(article_url)
    print(f"Title: {processed_article.title}")
    print(f"Summary: {processed_article.summary}")

except Exception as e:
    print(f"An error occurred: {e}")

# Process a local file
local_pdf = "/path/to/document.pdf"
try:
    processed_pdf = client.process(local_pdf, use_cache=False)
    print(f"Title: {processed_pdf.title}")

except Exception as e:
    print(f"An error occurred: {e}")

```
