"""
Fixture and asset path resolver for Siphon test suites and examples.

This module provides centralized access to test asset files (audio samples, PDFs, markdown documents) by resolving them from a base directory specified via the `BC` environment variable. It validates the existence of each asset at import time, ensuring that test code and example scripts fail fast if required fixture files are missing or misconfigured. The module is duplicated across siphon-api, siphon-server, and siphon-client packages to maintain self-contained test environments while reducing cross-package dependencies.

Usage:
```python
from siphon_server.example import EXAMPLE_MP3, EXAMPLE_PDF
# Assets are guaranteed to exist; use them directly in tests or demos
audio_content = AudioExtractor().extract(EXAMPLE_MP3)
```
"""

from pathlib import Path
import os

ASSETS_DIR = Path(os.getenv("BC")) / "siphon" / "assets"
EXAMPLE_MP3 = ASSETS_DIR / "example.mp3"
EXAMPLE_WAV = ASSETS_DIR / "example.wav"
EXAMPLE_PDF = ASSETS_DIR / "basic-text.pdf"
EXAMPLE_BIG_PDF = ASSETS_DIR / "large-doc.pdf"
EXAMPLE_MARKDOWN = ASSETS_DIR / "example.md"
EXAMPLE_CSV = ASSETS_DIR / "example.csv"
EXAMPLE_HTML = ASSETS_DIR / "example.html"
EXAMPLE_TOML = ASSETS_DIR / "example.toml"
EXAMPLE_TXT = ASSETS_DIR / "example.txt"
EXAMPLE_YAML = ASSETS_DIR / "example.yaml"

EXAMPLES = {
    "mp3": EXAMPLE_MP3,
    "wav": EXAMPLE_WAV,
    "pdf": EXAMPLE_PDF,
    "big_pdf": EXAMPLE_BIG_PDF,
    "markdown": EXAMPLE_MARKDOWN,
    "csv": EXAMPLE_CSV,
    "html": EXAMPLE_HTML,
    "toml": EXAMPLE_TOML,
    "txt": EXAMPLE_TXT,
    "yaml": EXAMPLE_YAML,
}

for path in EXAMPLES.values():
    assert path.exists(), f"Required test asset not found: {path}"
