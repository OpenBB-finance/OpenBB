from pathlib import Path

from pydantic import BaseModel


class Preferences(BaseModel):
    user_data_directory: str = str(Path.home() / "OpenBBUserData")

    class Config:
        validate_assignment = True
