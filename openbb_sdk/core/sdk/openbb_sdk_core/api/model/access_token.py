from datetime import datetime

from openbb_sdk_core.app.model.abstract.tagged import Tagged
from pydantic import Field


class AccessToken(Tagged):
    """This will be turn into a JWT Token"""

    sub: str = Field(description="Subject of the token, here : `UserSettings.id`")
    exp: datetime = Field(description="Expiration datetime of the `access_token`.")

    class Config:
        validate_assignment = True
