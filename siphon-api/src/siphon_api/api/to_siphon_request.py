from siphon_api.api.siphon_request import SiphonFile, SiphonRequest
from siphon_api.enums import SourceOrigin
from siphon_api.file_types import get_mime_type
from urllib.parse import urlparse
from pathlib import Path
import hashlib
import base64


def determine_origin(source: str) -> SourceOrigin:
    if Path(source).is_absolute() and Path(source).exists():
        return SourceOrigin.FILE_PATH
    else:
        parsed = urlparse(source)
        if parsed.scheme in {"http", "https"} or parsed.netloc:
            return SourceOrigin.URL
    raise ValueError("Source must be either a valid absolute file path or a valid URL.")


def create_siphon_request_from_file(file_path: Path) -> SiphonRequest:
    """
    Create a SiphonRequest object from a file path.
    Needs to be (1) an absolute path and (2) a valid file.
    """
    data = file_path.read_bytes()
    checksum = hashlib.sha256(data).hexdigest()
    mime_type = get_mime_type(file_path.name)
    extension = file_path.suffix.lower()

    siphon_file = SiphonFile(
        data=base64.b64encode(data).decode(),
        checksum=checksum,
        mime_type=mime_type or "application/octet-stream",
        extension=extension,
    )

    return SiphonRequest(
        source=str(file_path.resolve()),
        origin=SourceOrigin.FILE_PATH,
        file=siphon_file,
    )


def create_siphon_request_from_url(url: str) -> SiphonRequest:
    """
    Create a SiphonRequest object from a URL.
    """
    return SiphonRequest(
        source=url,
        origin=SourceOrigin.URL,
        file=None,
    )


def create_siphon_request(source: str) -> SiphonRequest:
    """
    Create a SiphonRequest object from either a file path or a URL.
    """
    origin = determine_origin(source)
    match origin:
        case SourceOrigin.FILE_PATH:
            return create_siphon_request_from_file(Path(source))
        case SourceOrigin.URL:
            return create_siphon_request_from_url(source)
