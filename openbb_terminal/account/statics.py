from enum import Enum
from dataclasses import dataclass

BASE_URL = "http://127.0.0.1:8000/"


class Success(Enum):
    VALID_LOGIN = "[green]\nLogin successful.[/green]"
    REMOTE_LOGOUT = "[green]\nLogged out remotely.[/green]"
    LOCAL_LOGOUT = "[green]\nRemoved login info.[/green]"


class Failure(Enum):
    INVALID_LOGIN = "[red]\nInvalid login.[/red]"
    CONNECTION_ERROR = "[red]\nConnection error.[/red]"
    WRONG_CREDENTIALS = "[red]\nWrong credentials.[/red]"
    UNVERIFIED_EMAIL = "[red]\nUnverified email.[/red]"
    UNKNOWN_ERROR = "[red]\nUnknown error.[/red]"


@dataclass(frozen=True)
class User:
    token_type: str = ""
    token: str = ""
    email: str = ""
    uuid: str = ""
