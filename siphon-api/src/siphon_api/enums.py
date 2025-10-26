from enum import Enum


class SourceType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    DOC = "doc"
    ARTICLE = "article"
    YOUTUBE = "youtube"
    GITHUB = "github"
    REDDIT = "reddit"
    OBSIDIAN = "obsidian"
    DRIVE = "drive"
    EMAIL = "email"
