import platform
import sys
from typing import Literal

from pydantic.dataclasses import dataclass

from openbb_terminal.core.models import BaseModel

# pylint: disable=too-many-instance-attributes


@dataclass(config=dict(validate_assignment=True, frozen=True))
class SystemModel(BaseModel):
    """Data model for system variables and configurations."""

    # System section
    OS: str = str(platform.system())
    PYTHON_VERSION: str = str(platform.python_version())

    # OpenBB section
    VERSION = "3.0.0rc1"
    PACKAGED: bool = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

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
