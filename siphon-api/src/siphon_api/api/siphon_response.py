from pydantic import BaseModel, Field
from siphon_api.enums import SourceType
from siphon_api.models import PipelineClass


class SiphonResponse(BaseModel):
    source_type: SourceType = Field(
        ..., description="The type of source from which content was siphoned"
    )
    payload: PipelineClass = Field(
        ..., description="The main content payload", discriminator="kind"
    )
