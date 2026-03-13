"""OpenBB Core App Abstract Model Tagged."""

from pydantic import BaseModel, Field
from uuid_extensions import uuid7str


class Tagged(BaseModel):
    """Model for Tagged."""

    id: str = Field(default_factory=uuid7str)
