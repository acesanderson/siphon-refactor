from enum import Enum


class SourceOrigin(str, Enum):
    URL = "url"
    FILE_PATH = "file_path"


class SourceType(str, Enum):
    DOC = "Doc"
    YOUTUBE = "YouTube"
    ARTICLE = "Article"
    AUDIO = "Audio"
    DRIVE = "Drive"
    # EMAIL = "Email"
    # IMAGE = "Image"
    # VIDEO = "Video"
    # GITHUB = "GitHub"
    # REDDIT = "Reddit"
    # OBSIDIAN = "Obsidian"
    # LLM_CHATS = "LLM_Chats"


class ActionType(str, Enum):
    PARSE = "parse"
    EXTRACT = "extract"
    TOKENIZE = "tokenize"
    ENRICH = "enrich"
    GULP = "gulp"
