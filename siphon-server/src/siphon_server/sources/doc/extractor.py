from siphon_api.interfaces import ExtractorStrategy
from siphon_api.models import SourceInfo, ContentData
from siphon_api.enums import SourceType
from typing import override


class DocExtractor(ExtractorStrategy):
    """
    Extract content from Doc: i.e. .doc, .docx files.
    """

    source_type: SourceType = SourceType.DOC

    def __init__(self, client=None):
        # TODO: Inject actual client dependency
        self.client = client

    @override
    def extract(self, source: SourceInfo) -> ContentData:
        # TODO: Fetch and extract content
        raise NotImplementedError


"""
from siphon.data.type_definitions.extensions import Extensions
from pathlib import Path


dir_path = Path(__file__).parent
asset_dir = dir_path / "assets"
asset_files = list(asset_dir.glob("*.*"))


# Our functions
def route_file(file_path: Path):
    ext = file_path.suffix.lower()
    for category, exts in Extensions.items():
        if ext in exts:
            return category
    return "unknown"


def convert_markitdown(file_path: Path):
    from markitdown import MarkItDown

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in Extensions["markitdown"]:
        raise ValueError(f"File type not supported for MarkItDown: {file_path.suffix}")
    # Do the conversion
    md = MarkItDown()
    return md.convert(file_path)


def convert_raw(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in Extensions["raw"]:
        raise ValueError(
            f"File type not supported for raw conversion: {file_path.suffix}"
        )
    # Implement raw conversion logic here
    with open(file_path, "r") as f:
        return f.read()


def convert_code(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in Extensions["code"]:
        raise ValueError(
            f"File type not supported for code conversion: {file_path.suffix}"
        )
    # Implement code conversion logic here
    with open(file_path, "r") as f:
        return f.read()


def convert_audio(file_path: Path):
    from siphon.ingestion.audio.retrieve_audio import retrieve_audio

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in Extensions["audio"]:
        raise ValueError(
            f"File type not supported for Whisper conversion: {file_path.suffix}"
        )
    output = retrieve_audio(file_path)
    return output


def convert_video(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in Extensions["video"]:
        raise ValueError(
            f"File type not supported for video conversion: {file_path.suffix}"
        )
    # Implement video conversion logic here
    # Placeholder for actual video conversion implementation
    raise NotImplementedError("Video conversion not implemented yet.")


def convert_image(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in Extensions["image"]:
        raise ValueError(
            f"File type not supported for OCR conversion: {file_path.suffix}"
        )
    from siphon.ingestion.image.retrieve_image import retrieve_image

    output = retrieve_image(file_path)
    return output


def convert_archive(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in Extensions["archive"]:
        raise ValueError(
            f"File type not supported for archive conversion: {file_path.suffix}"
        )
    # Implement archive extraction logic here
    # Placeholder for actual archive extraction implementation
    raise NotImplementedError("Archive extraction not implemented yet.")


def convert_specialized(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in Extensions["specialized"]:
        raise ValueError(
            f"File type not supported for specialized conversion: {file_path.suffix}"
        )
    # Implement specialized file conversion logic here
    # Placeholder for actual specialized file conversion implementation
    raise NotImplementedError("Specialized file conversion not implemented yet.")


def retrieve_file_context(file_path: Path) -> str:
    category = route_file(file_path)
    output = ""
    match category:
        case "markitdown":
            output = convert_markitdown(file_path)
        case "raw":
            output = convert_raw(file_path)
        case "code":
            output = convert_code(file_path)
        case "audio":
            output = convert_audio(file_path)
        case "video":
            output = convert_video(file_path)
        case "image":
            output = convert_image(file_path)
        case "archive":
            output = convert_archive(file_path)
        case "specialized":
            output = convert_specialized(file_path)
        case "unknown":
            raise ValueError(f"Unknown file type for: {file_path}")
        case _:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    if output:
        return output
    else:
        raise ValueError(f"Failed to convert file: {file_path}")
"""
