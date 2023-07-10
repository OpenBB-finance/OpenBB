# from typing import Dict, List, Union


from openbb_sdk_core.app.hub.model.features_keys import FeaturesKeys
from pydantic import BaseModel


class HubUserSettings(BaseModel):
    # features_settings: Dict[str, str]
    features_keys: FeaturesKeys
    # features_sources: Dict[str, List[str]]
    # features_terminal_style: Dict[str, Union[str, Dict[str, str]]]
