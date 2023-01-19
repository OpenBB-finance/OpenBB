# Will something like this for the logging
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    token_type: str = ""
    token: str = ""
    email: str = ""
    uuid: str = ""
