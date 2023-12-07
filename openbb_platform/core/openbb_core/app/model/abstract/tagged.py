from pydantic import BaseModel, Field
from uuid_extensions import uuid7str


class Tagged(BaseModel):
    id: str = Field(default_factory=uuid7str, alias="_id")
