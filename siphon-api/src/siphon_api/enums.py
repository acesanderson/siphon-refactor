from enum import Enum


class SourceOrigin(str, Enum):
    URL = "url"
    FILE_PATH = "file_path"


class SourceType(str, Enum):
    DOC = "Doc"
    YOUTUBE = "YouTube"
    ARTICLE = "Article"
    AUDIO = "Audio"
    # IMAGE = "Image"
    # VIDEO = "Video"
    # GITHUB = "GitHub"
    # REDDIT = "Reddit"
    # OBSIDIAN = "Obsidian"
    # DRIVE = "Drive"
    # EMAIL = "Email"


class ActionType(str, Enum):
    GULP = "gulp"
    PARSE = "parse"
    EXTRACT = "extract"
    ENRICH = "enrich"
