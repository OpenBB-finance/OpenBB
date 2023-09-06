"""Access Token Model."""
from datetime import datetime

from openbb_core.app.model.abstract.tagged import Tagged
from pydantic import Field


class AccessToken(Tagged):
    """Turn into a JWT Token."""

    sub: str = Field(description="Subject of the token, here : `UserSettings.id`")
    exp: datetime = Field(description="Expiration datetime of the `access_token`.")

    class Config:
        """Pydantic Config."""

        validate_assignment = True
