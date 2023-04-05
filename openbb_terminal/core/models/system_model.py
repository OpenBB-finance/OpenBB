import platform
from typing import Literal

from pydantic.dataclasses import dataclass

from openbb_terminal.core.models import BaseModel

# pylint: disable=too-many-instance-attributes


@dataclass(config=dict(validate_assignment=True, frozen=True))
class SystemModel(BaseModel):
    """
    Data model for system variables and configurations.

    Disclaimer:
        If you need to have a system related variable that is a credential like
        `LOGGING_AWS_ACCESS_KEY_ID` and `LOGGING_AWS_SECRET_ACCESS_KEY`, you need
        refer to the following function
        `openbb_terminal.core.log.generation.settings_logger.log_system`,
        in order to filter it from the logs.
    """

    # System section
    OS: str = str(platform.system())
    PYTHON_VERSION: str = str(platform.python_version())

    # OpenBB section
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
    LOG_COLLECT: bool = True

    # Personalization section
    DISABLE_STREAMLIT_WARNING: bool = False
    DISABLE_FORECASTING_WARNING: bool = False
    DISABLE_OPTIMIZATION_WARNING: bool = False

    # Others
    TEST_MODE: bool = False
    DEBUG_MODE: bool = False
    ENABLE_AUTHENTICATION: bool = True

    def __repr__(self) -> str:  # pylint: disable=useless-super-delegation
        return super().__repr__()
