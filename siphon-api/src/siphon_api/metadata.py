from pydantic import BaseModel, Field


# YouTube
class YouTubeMetadata(BaseModel):
    url: str | None = Field(default=None, description="The URL of the YouTube video")
    domain: str = Field(
        default="youtube.com", description="The domain of the video platform"
    )
    title: str | None = Field(
        default=None, description="The title of the YouTube video"
    )
    published_date: str | None = Field(
        default=None, description="The upload date of the YouTube video"
    )
    video_id: str | None = Field(
        default=None, description="The unique identifier for the YouTube video"
    )
    channel: str | None = Field(
        default=None, description="The channel that uploaded the YouTube video"
    )
    duration: int | None = Field(
        default=None, description="The duration of the YouTube video in seconds"
    )
    description: str | None = Field(
        default=None, description="The description of the YouTube video"
    )
    tags: list[str] | None = Field(
        default=None, description="The tags associated with the YouTube video"
    )


# Files
class FileMetadata(BaseModel):
    file_name: str | None = Field(default=None, description="The name of the file")
    hash: str | None = Field(default=None, description="The hash of the file")
    created_at: str | None = Field(
        default=None, description="The creation timestamp of the file"
    )
    last_modified: str | None = Field(
        default=None, description="The last modified timestamp of the file"
    )
    file_size: int | None = Field(
        default=None, description="The size of the file in bytes"
    )
    extension: str | None = Field(
        default=None, description="The file extension (e.g., 'txt', 'jpg')"
    )
    mime_type: str | None = Field(default=None, description="The MIME type of the file")
