from pydantic import BaseModel


class OpenBBCustomParameter(BaseModel):
    """Custom parameter for OpenBB."""

    description: str
