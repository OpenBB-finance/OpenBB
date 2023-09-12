from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class OpenBBCustomParameter(BaseModel):
    """Custom parameter for OpenBB."""

    description: Optional[str] = Field(
        default=None,
        description="Description of the custom parameter.",
    )
    model_config = ConfigDict(frozen=True, extra="allow", populate_by_name=True)
