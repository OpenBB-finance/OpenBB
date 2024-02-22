from pydantic import BaseModel, Field
from uuid_extensions import uuid7str  # type: ignore


class Tagged(BaseModel):
    id: str = Field(default_factory=uuid7str, alias="_id")
