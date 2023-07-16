import platform
from typing import List, Literal

from pydantic import Field, root_validator, validator
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
    PLATFORM: str = str(platform.platform())

    # OpenBB section
    VERSION: str = "3.1.0"

    # Logging section
    LOGGING_APP_ID: str = "REPLACE_ME"
    LOGGING_APP_NAME: str = "gst"
    LOGGING_AWS_ACCESS_KEY_ID: str = "REPLACE_ME"
    LOGGING_AWS_SECRET_ACCESS_KEY: str = "REPLACE_ME"
    LOGGING_COMMIT_HASH: str = "REPLACE_ME"
    LOGGING_BRANCH: str = "REPLACE_ME"
    LOGGING_FREQUENCY: Literal["D", "H", "M", "S"] = "H"
    LOGGING_HANDLERS: List[str] = Field(default_factory=lambda: ["file"])
    LOGGING_ROLLING_CLOCK: bool = False
    LOGGING_VERBOSITY: int = 20
    LOGGING_SUB_APP: str = "terminal"
    LOGGING_SUPPRESS: bool = False
    LOGGING_SEND_TO_S3: bool = True
    LOG_COLLECT: bool = True

    # Personalization section
    DISABLE_STREAMLIT_WARNING: bool = False
    DISABLE_FORECASTING_WARNING: bool = False
    DISABLE_OPTIMIZATION_WARNING: bool = False

    # Others
    TEST_MODE: bool = False
    DEBUG_MODE: bool = False
    ENABLE_AUTHENTICATION: bool = True
    HEADLESS: bool = False

    def __repr__(self) -> str:  # pylint: disable=useless-super-delegation
        return super().__repr__()

    @root_validator(allow_reuse=True)
    @classmethod
    def add_additional_handlers(cls, values):
        if (
            not any([values["TEST_MODE"], values["LOGGING_SUPPRESS"]])
            and values["LOG_COLLECT"]
            and "posthog" not in values["LOGGING_HANDLERS"]
        ):
            values["LOGGING_HANDLERS"].append("posthog")

        return values

    @root_validator(allow_reuse=True)
    @classmethod
    def validate_send_to_s3(cls, values):
        if "posthog" in values["LOGGING_HANDLERS"] or values["LOG_COLLECT"] is False:
            values["LOGGING_SEND_TO_S3"] = False
        return values

    @validator("LOGGING_HANDLERS", allow_reuse=True)
    @classmethod
    def validate_logging_handlers(cls, v):
        for value in v:
            if value not in ["stdout", "stderr", "noop", "file", "posthog"]:
                raise ValueError("Invalid logging handler")
        return v
