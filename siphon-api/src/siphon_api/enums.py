from enum import Enum


class SourceType(str, Enum):
    DOC = "Doc"
    YOUTUBE = "YouTube"
    ARTICLE = "Article"
    AUDIO = "Audio"
    # IMAGE = "Image"
    # VIDEO = "Video"
    # TEXT = "Text"
    # GITHUB = "GitHub"
    # REDDIT = "Reddit"
    # OBSIDIAN = "Obsidian"
    # DRIVE = "Drive"
    # EMAIL = "Email"
