from typing import Literal

from pydantic.dataclasses import dataclass

from openbb_terminal.core.models import BaseModel


@dataclass(config=dict(validate_assignment=True, frozen=True))
class SystemModel(BaseModel):
    """Data model for system variables and configurations."""

    # System version
    VERSION = "3.0.0rc1"

    # Logging section
    LOGGING_APP_NAME: str = "gst"
    LOGGING_AWS_ACCESS_KEY_ID: str = "REPLACE_ME"
    LOGGING_AWS_SECRET_ACCESS_KEY: str = "REPLACE_ME"
    LOGGING_COMMIT_HASH: str = "REPLACE_ME"
    LOGGING_FREQUENCY: Literal["D", "H", "M", "S"] = "H"
    LOGGING_HANDLERS: Literal["stdout", "stderr", "noop", "file"] = "file"
    LOGGING_ROLLING_CLOCK: bool = False
    LOGGING_VERBOSITY: int = 20
    LOGGING_SUB_APP: str = "terminal"
    LOGGING_SUPPRESS: bool = False

    def __repr__(self) -> str:  # pylint: disable=useless-super-delegation
        return super().__repr__()
