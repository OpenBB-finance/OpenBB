"""Defaults model."""

from typing import Any
from warnings import warn

from openbb_core.app.model.abstract.warning import OpenBBWarning
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Defaults(BaseModel):
    """Defaults."""

    model_config = ConfigDict(validate_assignment=True, populate_by_name=True)

    commands: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        alias="routes",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    @model_validator(mode="before")
    @classmethod
    def validate_before(cls, values: dict) -> dict:
        """Validate model (before)."""
        key = "commands"
        if "routes" in values:
            if not values.get("routes"):
                del values["routes"]
            show_warnings = values.get("preferences", {}).get("show_warnings")
            if show_warnings is False or show_warnings in ["False", "false"]:
                warn(
                    message="The 'routes' key is deprecated within 'defaults' of 'user_settings.json'."
                    + " Suppress this warning by updating the key to 'commands'.",
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
        """Update current defaults."""
        incoming_commands = incoming.model_dump(exclude_none=True).get("commands", {})
        self.__dict__["commands"].update(incoming_commands)
