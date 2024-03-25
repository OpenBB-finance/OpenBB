from pydantic.dataclasses import dataclass

from openbb_terminal.core.models import BaseModel

# pylint: disable=too-many-instance-attributes


@dataclass(config=dict(validate_assignment=True, frozen=True))
class SystemModel(BaseModel):
    """
    Data model for system variables and configurations.
    """

    # OpenBB section
    VERSION: str = "3.2.5"

    # Others
    TEST_MODE: bool = False
    DEBUG_MODE: bool = False
    DEV_BACKEND: bool = False

    def __repr__(self) -> str:  # pylint: disable=useless-super-delegation
        return super().__repr__()
