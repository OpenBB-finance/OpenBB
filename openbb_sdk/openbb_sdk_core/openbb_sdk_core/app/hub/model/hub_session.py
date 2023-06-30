from pydantic import BaseModel


class HubSession(BaseModel):
    access_token: str
    token_type: str
    user_uuid: str
    email: str
    primary_usage: str
