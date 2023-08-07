import json
import os
import platform as pl  # I do this so that the import doesn't conflict with the variable name
from functools import partial
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import field_validator, model_validator, ConfigDict, Field

from openbb_core.app.constants import (
    HOME_DIRECTORY,
    OPENBB_DIRECTORY,
    SYSTEM_SETTINGS_PATH,
    USER_SETTINGS_PATH,
)
from openbb_core.app.logs.utils.system_utils import get_branch, get_commit_hash
from openbb_core.app.model.abstract.tagged import Tagged

FrozenField = partial(Field, allow_mutation=False)


class SystemSettings(Tagged):
    # System section
    os: str = FrozenField(default=str(pl.system()))
    python_version: str = FrozenField(default=str(pl.python_version()))
    platform: str = FrozenField(default=str(pl.platform()))

    # OpenBB section
    # TODO: Get the version of the SDK from somewhere that's not pyproject.toml
    version: str = FrozenField(default="4.0.0dev")
    home_directory: str = FrozenField(default=str(HOME_DIRECTORY))
    openbb_directory: str = FrozenField(default=str(OPENBB_DIRECTORY))
    user_settings_path: str = FrozenField(default=str(USER_SETTINGS_PATH))
    system_settings_path: str = FrozenField(default=str(SYSTEM_SETTINGS_PATH))

    # Logging section
    logging_app_name: str = FrozenField(default="gst")
    logging_commit_hash: Optional[str] = FrozenField(default=None)
    logging_branch: Optional[str] = FrozenField(default=None)
    logging_frequency: Literal["D", "H", "M", "S"] = FrozenField(default="H")
    logging_handlers: List[str] = FrozenField(default_factory=lambda: ["file"])
    logging_rolling_clock: bool = FrozenField(default=False)
    logging_verbosity: int = FrozenField(default=20)
    logging_sub_app: str = FrozenField(default="sdk")
    logging_suppress: bool = FrozenField(default=False)
    log_collect: bool = FrozenField(default=True)

    # Others
    test_mode: bool = False
    debug_mode: bool = False
    headless: bool = False
    run_in_isolation: bool = FrozenField(
        default=False,
        description="Whether or not to run each command in total isolation.",
    )
    dbms_uri: Optional[str] = FrozenField(
        default=None,
        description="Connection URI like : `mongodb://root:example@localhost:27017/`",
    )
    model_config = ConfigDict(validate_assignment=True)

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

    # TODO: Allow setting debug mode from environment variable
    # @root_validator(allow_reuse=True)
    # @classmethod
    # def validate_debug_mode(cls, values):
    #     dm = os.getenv("DEBUG_MODE", "").lower() in ["true", "1"]
    #     values["debug_mode"] = bool(values["debug_mode"] or dm)
    #     return values

    @model_validator(mode="before")
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

    @model_validator(mode="before")
    @classmethod
    def validate_posthog_handler(cls, values):
        if (
            not any([values["test_mode"], values["logging_suppress"]])
            and values["log_collect"]
            and "posthog" not in values["logging_handlers"]
        ):
            values["logging_handlers"].append("posthog")

        return values

    @field_validator("logging_handlers")
    @classmethod
    @classmethod
    def validate_logging_handlers(cls, v):
        for value in v:
            if value not in ["stdout", "stderr", "noop", "file", "posthog"]:
                raise ValueError("Invalid logging handler")
        return v

    @field_validator("logging_commit_hash")
    @classmethod
    @classmethod
    def validate_commit_hash(cls, v):
        return v or get_commit_hash()

    @model_validator(mode="before")
    @classmethod
    def validate_branch(cls, values):
        branch = values["logging_branch"]
        commit_hash = values["logging_commit_hash"]

        if not branch and commit_hash:
            values["logging_branch"] = get_branch(commit_hash)

        return values
