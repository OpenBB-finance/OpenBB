import json
import os
import platform as pl  # I do this so that the import doesn't conflict with the variable name
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import Field, root_validator, validator

from openbb_core.app.constants import (
    HOME_DIRECTORY,
    OPENBB_DIRECTORY,
    SYSTEM_SETTINGS_PATH,
    USER_SETTINGS_PATH,
)
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.logs.utils.system_utils import get_branch, get_commit_hash


class SystemSettings(Tagged):
    run_in_isolation: bool = Field(
        default=False,
        description="Whether or not to run each command in total isolation.",
    )
    dbms_uri: Optional[str] = Field(
        default=None,
        description="Connection URI like : `mongodb://root:example@localhost:27017/`",
    )

    # System section
    os: str = str(pl.system())
    python_version: str = str(pl.python_version())
    platform: str = str(pl.platform())

    # OpenBB section
    # TODO: Get the version of the SDK from somewhere that's not pyproject.toml
    version: str = "4.0.0dev"
    home_directory: str = str(HOME_DIRECTORY)
    openbb_directory: str = str(OPENBB_DIRECTORY)
    user_settings_path: str = str(USER_SETTINGS_PATH)
    system_settings_path: str = str(SYSTEM_SETTINGS_PATH)

    # Logging section
    logging_app_name: str = "gst"
    logging_commit_hash: Optional[str] = None
    logging_branch: Optional[str] = None
    logging_frequency: Literal["D", "H", "M", "S"] = "H"
    logging_handlers: List[str] = Field(default_factory=lambda: ["file"])
    logging_rolling_clock: bool = False
    logging_verbosity: int = 20
    logging_sub_app: str = "sdk"
    logging_suppress: bool = False
    log_collect: bool = True

    # Others
    test_mode: bool = False
    debug_mode: bool = False
    headless: bool = False

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
        )

    @staticmethod
    def create_empty_json(path: Path) -> None:
        with open(path, mode="w") as file:
            json.dump({}, file)

    @root_validator(allow_reuse=True)
    @classmethod
    def create_openbb_directory(cls, values):
        obb_dir = values["openbb_directory"]
        user_settings = values["user_settings_path"]
        system_settings = values["system_settings_path"]
        if not os.path.exists(obb_dir):
            os.makedirs(obb_dir)
            cls.create_empty_json(user_settings)
            cls.create_empty_json(system_settings)
        else:
            if not os.path.exists(user_settings):
                cls.create_empty_json(user_settings)
            if not os.path.exists(system_settings):
                cls.create_empty_json(system_settings)
        return values

    @root_validator(allow_reuse=True)
    @classmethod
    def validate_posthog_handler(cls, values):
        if (
            not any([values["test_mode"], values["logging_suppress"]])
            and values["log_collect"]
            and "posthog" not in values["logging_handlers"]
        ):
            values["logging_handlers"].append("posthog")

        return values

    @validator("logging_handlers", allow_reuse=True, always=True)
    @classmethod
    def validate_logging_handlers(cls, v):
        for value in v:
            if value not in ["stdout", "stderr", "noop", "file", "posthog"]:
                raise ValueError("Invalid logging handler")
        return v

    @validator("logging_commit_hash", allow_reuse=True, always=True)
    @classmethod
    def validate_commit_hash(cls, v):
        return v or get_commit_hash()

    @root_validator(allow_reuse=True)
    @classmethod
    def validate_branch(cls, values):
        branch = values["logging_branch"]
        commit_hash = values["logging_commit_hash"]

        if not branch and commit_hash:
            values["logging_branch"] = get_branch(commit_hash)

        return values
