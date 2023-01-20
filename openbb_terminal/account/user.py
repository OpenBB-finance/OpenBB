# Will something like this for the logging
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class User:
    token_type: str = ""
    token: str = ""
    email: str = ""
    uuid: str = ""
    configs: Optional[dict] = None
