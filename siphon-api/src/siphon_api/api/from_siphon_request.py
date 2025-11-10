"""
Temporary file lifecycle manager for server-side content processing in the Siphon ingestion pipeline.

The `ensure_temp_file` function validates that the SiphonRequest contains file data, writes the raw bytes (already decoded by Pydantic validation), and manages both successful cleanup and error handling. This abstraction decouples content type handlers from HTTP multipart payload management, allowing parsers and extractors to assume native file paths without conditional branching for transport formats.

Usage:
```python
from siphon_server.server.temp_file import ensure_temp_file

request = create_siphon_request(file_path="/path/to/document.pdf")
with ensure_temp_file(request) as temp_path:
    content = extractor.extract(temp_path)  # Temp file guaranteed to exist
    # Automatic cleanup on context exit
```
"""

from siphon_api.api.siphon_request import SiphonRequest
from contextlib import contextmanager
from pathlib import Path
import tempfile
import logging

logger = logging.getLogger(__name__)


@contextmanager
def ensure_temp_file(request: SiphonRequest):
    """
    Context manager to rehydrate a SiphonFile from a SiphonRequest
    into a temporary file, yielding its path and deleting it on exit.
    """
    if request.file is None:
        raise ValueError("SiphonRequest must include a file to rehydrate.")

    suffix = request.file.extension or ""
    temp_file = None
    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp_path = Path(temp_file.name)

        # Write the raw bytes (already decoded by Pydantic model)
        temp_file.write(request.file.data)
        temp_file.flush()
        logger.debug(f"[TEMP] Rehydrated file written to {temp_path}")

        yield temp_path

    finally:
        if temp_file:
            try:
                temp_file.close()
                temp_path.unlink(missing_ok=True)
                logger.debug(f"[TEMP] Deleted temp file: {temp_path}")
            except Exception as e:
                logger.warning(f"[TEMP] Failed to delete temp file {temp_path}: {e}")


if __name__ == "__main__":
    from siphon_api.example import EXAMPLES
    from siphon_api.api.siphon_request import SiphonRequest, SiphonFile
    from siphon_api.file_types import get_mime_type
    from siphon_api.enums import SourceOrigin
    import hashlib

    for index, example_source in enumerate(EXAMPLES.values()):
        print(f"\n=== Testing example {index + 1}: {example_source} ===")
        # Create a SiphonFile, generating the binary data from disk
        with open(example_source, "rb") as f:
            data = f.read()
        checksum = hashlib.sha256(data).hexdigest()
        mime_type = get_mime_type(file_path=str(example_source))
        extension = Path(example_source).suffix
        siphon_file = SiphonFile(
            mime_type=mime_type,
            extension=extension,
            checksum=checksum,
            data=data,
        )
        source = example_source
        siphon_origin = SourceOrigin.FILE_PATH
        request = SiphonRequest(
            file=siphon_file, source=str(source), origin=siphon_origin
        )
        # Now test the temp file context manager
        print("Original file: ", example_source)
        print("Testing ensure_temp_file context manager...")
        with ensure_temp_file(request) as temp_path:
            print(f"Temp file created at: {temp_path}")
            with open(temp_path, "rb") as f:
                rehydrated_data = f.read()
            assert rehydrated_data == data
            print("Rehydrated data matches original data.")
            # Print contents of the temp file (with "r")
            with open(temp_path, "r", encoding="utf-8", errors="ignore") as f:
                contents = f.read(100)  # Read first 100 characters
                print("Contents of temp file (first 100 chars):")
                print(contents)
