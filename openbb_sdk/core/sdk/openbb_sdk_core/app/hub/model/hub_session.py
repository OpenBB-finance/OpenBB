from pydantic import BaseModel


class HubSession(BaseModel):
    access_token: str
    token_type: str
    user_uuid: str
    email: str
    username: str
    primary_usage: str

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
        )
