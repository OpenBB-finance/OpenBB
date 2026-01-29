"""默认值模型。"""

from typing import Any
from warnings import warn

from openbb_core.app.model.abstract.warning import OpenBBWarning
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Defaults(BaseModel):
    """默认值。"""

    model_config = ConfigDict(validate_assignment=True, populate_by_name=True)

    commands: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        alias="routes",
    )

    def __repr__(self) -> str:
        """返回字符串表示形式。"""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    @model_validator(mode="before")
    @classmethod
    def validate_before(cls, values: dict) -> dict:
        """验证模型（之前）。"""
        key = "commands"
        if "routes" in values:
            if not values.get("routes"):
                del values["routes"]
            show_warnings = values.get("preferences", {}).get("show_warnings")
            if show_warnings is False or show_warnings in ["False", "false"]:
                warn(
                    message="'user_settings.json' 中 'defaults' 内的 'routes' 键已弃用。"
                    + " 通过将键更新为 'commands' 来抑制此警告。",
                    category=OpenBBWarning,
                )
                key = "routes"

        new_values: dict = {"commands": {}}
        for k, v in values.get(key, {}).items():
            clean_k = k.strip("/").replace("/", ".")
            provider = v.get("provider") if v else None
            if isinstance(provider, str):
                v["provider"] = [provider]
            new_values["commands"][clean_k] = v

        return new_values

    def update(self, incoming: "Defaults"):
        """更新当前默认值。"""
        incoming_commands = incoming.model_dump(exclude_none=True).get("commands", {})
        self.__dict__["commands"].update(incoming_commands)
