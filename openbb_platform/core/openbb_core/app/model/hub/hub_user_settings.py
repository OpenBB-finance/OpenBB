"""Hub user settings model."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HubUserSettings(BaseModel):
    """Hub user settings model."""

    features_settings: Dict[str, Any] = Field(default_factory=dict)
    features_keys: Dict[str, Optional[str]] = Field(default_factory=dict)
    # features_sources: Dict[str, Any]
    # features_terminal_style: Dict[str, Union[str, Dict[str, str]]]

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("features_keys", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, d: dict) -> dict:
        """Convert dict keys to lowercase."""
        return {k.lower(): v for k, v in d.items()}
