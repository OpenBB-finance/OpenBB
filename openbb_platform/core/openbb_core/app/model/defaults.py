"""Defaults model."""

from typing import Dict, List, Optional
from warnings import warn

from pydantic import BaseModel, ConfigDict, Field, model_validator

from openbb_core.app.model.abstract.warning import OpenBBWarning


class Defaults(BaseModel):
    """Defaults."""

    model_config = ConfigDict(validate_assignment=True, populate_by_name=True)

    commands: Dict[str, Dict[str, Optional[List[str]]]] = Field(
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
            warn(
                message="'routes' is deprecated. Use 'commands' instead.",
                category=OpenBBWarning,
            )
            key = "routes"

        new_values: Dict[str, Dict[str, Optional[List[str]]]] = {"commands": {}}
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
