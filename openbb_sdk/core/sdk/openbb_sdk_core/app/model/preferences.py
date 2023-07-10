from pathlib import Path

from pydantic import BaseModel


class Preferences(BaseModel):
    user_data_directory: str = str(Path.home() / "OpenBBUserData")

    class Config:
        validate_assignment = True

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
        )
