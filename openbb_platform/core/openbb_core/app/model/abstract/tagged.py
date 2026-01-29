"""OpenBB Core 应用程序抽象模型标记。"""

from pydantic import BaseModel, Field
from uuid_extensions import uuid7str


class Tagged(BaseModel):
    """标记模型。"""

    id: str = Field(default_factory=uuid7str)
