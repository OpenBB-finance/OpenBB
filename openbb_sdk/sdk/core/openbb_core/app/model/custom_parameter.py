from typing import Optional

from pydantic import BaseModel


class OpenBBCustomParameter(BaseModel):
    """Custom parameter for OpenBB."""

    description: Optional[str] = None

    class Config:
        frozen = True
