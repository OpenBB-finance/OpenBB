# IMPORT STANDARD
from pathlib import Path

# IMPORT THIRD-PARTY
from pydantic import BaseModel

# IMPORT INTERNAL


class Preferences(BaseModel):
    user_data_directory: str = str(Path.home() / "OpenBBUserData")

    class Config:
        validate_assignment = True
