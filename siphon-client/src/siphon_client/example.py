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
assert ASSETS_DIR.exists(), f"Assets directory does not exist: {ASSETS_DIR}"
EXAMPLE_MP3 = ASSETS_DIR / "example.mp3"
assert EXAMPLE_MP3.exists(), f"Example MP3 file does not exist: {EXAMPLE_MP3}"
EXAMPLE_WAV = ASSETS_DIR / "example.wav"
assert EXAMPLE_WAV.exists(), f"Example WAV file does not exist: {EXAMPLE_WAV}"
EXAMPLE_PDF = ASSETS_DIR / "basic-text.pdf"
assert EXAMPLE_PDF.exists(), f"Example PDF file does not exist: {EXAMPLE_PDF}"
EXAMPLE_BIG_PDF = ASSETS_DIR / "large-doc.pdf"
assert EXAMPLE_BIG_PDF.exists(), (
    f"Example big PDF file does not exist: {EXAMPLE_BIG_PDF}"
)
EXAMPLE_MARKDOWN = ASSETS_DIR / "example.md"
assert EXAMPLE_MARKDOWN.exists(), (
    f"Example Markdown file does not exist: {EXAMPLE_MARKDOWN}"
)

EXAMPLES = {
    "mp3": EXAMPLE_MP3,
    "wav": EXAMPLE_WAV,
    "pdf": EXAMPLE_PDF,
    "big_pdf": EXAMPLE_BIG_PDF,
    "markdown": EXAMPLE_MARKDOWN,
}
