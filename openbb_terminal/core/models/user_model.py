from pydantic.dataclasses import dataclass

from openbb_terminal.core.models.base_model import BaseModel
from openbb_terminal.core.models.preferences_model import PreferencesModel


@dataclass(config=dict(validate_assignment=True, frozen=True))
class UserModel(BaseModel):
    """Data model for user."""

    preferences: PreferencesModel
