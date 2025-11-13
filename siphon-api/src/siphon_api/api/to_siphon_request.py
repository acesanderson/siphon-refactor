from siphon_api.api.siphon_request import SiphonFile, SiphonRequest, SiphonRequestParams
from siphon_api.enums import SourceOrigin
from urllib.parse import urlparse
from pathlib import Path
import hashlib
import logging

logger = logging.getLogger(__name__)


def determine_origin(source: str) -> SourceOrigin:
    logger.debug(f"Determining origin for source: {source}")
    if Path(source).is_absolute() and Path(source).exists():
        return SourceOrigin.FILE_PATH
    else:
        parsed = urlparse(source)
        if parsed.scheme in {"http", "https"} or parsed.netloc:
            return SourceOrigin.URL
    raise ValueError("Source must be either a valid absolute file path or a valid URL.")


def create_siphon_request_from_file(
    file_path: Path, request_params: SiphonRequestParams
) -> SiphonRequest:
    """
    Create a SiphonRequest object from a file path.
    Needs to be (1) an absolute path and (2) a valid file.
    """
    logger.debug(f"Creating SiphonRequest from file: {file_path}")
    data = file_path.read_bytes()
    checksum = hashlib.sha256(data).hexdigest()
    extension = file_path.suffix.lower()

    siphon_file = SiphonFile(
        data=data,
        checksum=checksum,
        extension=extension,
    )

    return SiphonRequest(
        source=str(file_path.resolve()),
        params=request_params,
        origin=SourceOrigin.FILE_PATH,
        file=siphon_file,
    )


def create_siphon_request_from_url(
    url: str, request_params: SiphonRequestParams
) -> SiphonRequest:
    """
    Create a SiphonRequest object from a URL.
    """
    logger.debug(f"Creating SiphonRequest from URL: {url}")
    return SiphonRequest(
        source=url,
        params=request_params,
        origin=SourceOrigin.URL,
        file=None,
    )


def create_siphon_request(
    source: str | Path, request_params: SiphonRequestParams
) -> SiphonRequest:
    """
    Create a SiphonRequest object from either a file path or a URL.
    """
    # Convert Path to str if necessary
    if isinstance(source, Path):
        source = str(source)
    logger.info(f"Creating SiphonRequest for source: {source}")
    origin = determine_origin(source)
    match origin:
        case SourceOrigin.FILE_PATH:
            return create_siphon_request_from_file(Path(source), request_params)
        case SourceOrigin.URL:
            return create_siphon_request_from_url(source, request_params)
