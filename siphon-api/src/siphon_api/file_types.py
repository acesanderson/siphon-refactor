"""
File type extensions and MIME types.

Also a utility function to get MIME type from file extension.
"""

EXTENSIONS = {
    "Text": [
        ".csv",
        ".json",
        ".xml",
        ".txt",
        ".md",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".py",
        ".js",
        ".html",
        ".css",
        ".java",
        ".cpp",
        ".c",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".log",
        ".env",
        ".sh",
    ],
    "Doc": [
        ".docx",
        ".pptx",
        ".xlsx",
        ".xls",
        ".pdf",
        ".msg",
        ".html",
        ".rtf",
    ],
    "Audio": [
        ".wav",
        ".mp3",
        ".m4a",
        ".ogg",
        ".flac",
    ],
    "Video": [
        ".mp4",
        ".avi",
        ".mov",
        ".webm",
        ".mkv",
    ],
    "Image": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".svg",
        ".webp",
        ".ico",
    ],
    # "archive": [".zip", ".tar", ".gz", ".rar", ".7z"],
    # "specialized": [".epub", ".mobi"],
}

MIME_TYPES = {
    # Text formats
    ".csv": "text/csv",
    ".json": "application/json",
    ".xml": "application/xml",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".yaml": "text/yaml",
    ".yml": "text/yaml",
    ".toml": "application/toml",
    ".ini": "text/plain",
    ".py": "text/x-python",
    ".js": "text/javascript",
    ".html": "text/html",
    ".css": "text/css",
    ".java": "text/x-java-source",
    ".cpp": "text/x-c++src",
    ".c": "text/x-csrc",
    ".go": "text/x-go",
    ".rs": "text/x-rustsrc",
    ".rb": "text/x-ruby",
    ".php": "text/x-php",
    ".log": "text/plain",
    ".env": "text/plain",
    ".sh": "application/x-sh",
    ".sql": "application/sql",
    ".ts": "text/typescript",
    ".tsx": "text/typescript",
    ".jsx": "text/javascript",
    ".tex": "application/x-tex",
    ".bib": "text/x-bibtex",
    ".rst": "text/x-rst",
    # Document formats
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls": "application/vnd.ms-excel",
    ".pdf": "application/pdf",
    ".msg": "application/vnd.ms-outlook",
    ".rtf": "application/rtf",
    ".odt": "application/vnd.oasis.opendocument.text",
    ".ods": "application/vnd.oasis.opendocument.spreadsheet",
    ".odp": "application/vnd.oasis.opendocument.presentation",
    ".epub": "application/epub+zip",
    ".eml": "message/rfc822",
    # Audio formats
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    # Video formats
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".mkv": "video/x-matroska",
    # Image formats
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    # Archive formats
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
    ".tar.gz": "application/gzip",
    ".tgz": "application/gzip",
    ".rar": "application/vnd.rar",
    ".7z": "application/x-7z-compressed",
    # Data formats
    ".parquet": "application/vnd.apache.parquet",
    ".jsonl": "application/jsonlines",
    ".tsv": "text/tab-separated-values",
    # Notebook
    ".ipynb": "application/x-ipynb+json",
}


def get_mime_type(file_path: str | None = None, extension: str | None = None) -> str:
    """
    Get MIME type from file extension.
    Returns 'application/octet-stream' for unknown extensions.
    """
    if all([file_path is None, extension is None]):
        raise ValueError("Either file_path or extension must be provided.")
    if all([file_path is not None, extension is not None]):
        raise ValueError("Only one of file_path or extension should be provided.")

    import os

    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        # Handle special case for .tar.gz
        if file_path.endswith(".tar.gz"):
            return MIME_TYPES[".tar.gz"]
        return MIME_TYPES.get(ext, "application/octet-stream")
    elif extension:
        ext = extension.lower()
        return MIME_TYPES.get(ext, "application/octet-stream")
