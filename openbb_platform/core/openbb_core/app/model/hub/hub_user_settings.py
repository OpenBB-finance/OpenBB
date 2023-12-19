# from typing import Dict, List, Union

from openbb_core.app.model.hub.features_keys import FeaturesKeys
from pydantic import BaseModel, ConfigDict, Field


class HubUserSettings(BaseModel):
    # features_settings: Dict[str, str]
    features_keys: FeaturesKeys = Field(default_factory=FeaturesKeys)
    # features_sources: Dict[str, List[str]]
    # features_terminal_style: Dict[str, Union[str, Dict[str, str]]]

    model_config = ConfigDict(validate_assignment=True)
