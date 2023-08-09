"""Token response model."""
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str
