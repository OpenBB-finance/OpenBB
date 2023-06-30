from typing import Optional

from pydantic import BaseModel


class HubCredentials(BaseModel):
    sdk_token: Optional[str]
    email: Optional[str]
    password: Optional[str]
