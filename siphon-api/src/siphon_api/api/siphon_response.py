from pydantic import BaseModel, Field
from siphon_api.enums import SourceType
from siphon_api.models import PipelineClass


class SiphonResponse(BaseModel):
    # Mandatory fields
    status: str = Field(..., description="The status of the siphon operation")
    source_type: SourceType = Field(
        ..., description="The type of source from which content was siphoned"
    )
    payload: PipelineClass = Field(
        ..., description="The main content payload", discriminator="kind"
    )
