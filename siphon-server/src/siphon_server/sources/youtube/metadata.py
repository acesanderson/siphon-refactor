"""
{'url': 'https://www.youtube.com/watch?v=37f0ALZg-XI',
'domain': 'youtube.com',
'title': 'Meta Layoffs 600 AI Employees -- Mark Zuckerberg is Popping AI Bubble',
'published_date': '20251027',
'video_id': '37f0ALZg-XI',
'channel': 'Eli the Computer Guy',
'duration': 1341,
'description': 'Support Content at - https://donorbox.org/etcg\nLinkedIn at - https://www.linkedin.com/in/eli-etherton-a15362211/',
'tags': ['Eli', 'the', 'Computer', 'Guy', 'Repair', 'Networking', 'Tech', 'IT', 'Startup', 'Arduino', 'iot']}
"""

from pydantic import BaseModel, Field


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
