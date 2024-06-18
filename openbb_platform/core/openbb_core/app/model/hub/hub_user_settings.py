"""Hub user settings model."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class HubUserSettings(BaseModel):
    """Hub user settings model."""

    features_settings: Dict[str, Any] = Field(default_factory=dict)
    features_keys: Dict[str, Optional[str]] = Field(default_factory=dict)
    # features_sources: Dict[str, Any]
    # features_terminal_style: Dict[str, Union[str, Dict[str, str]]]

    model_config = ConfigDict(validate_assignment=True)
