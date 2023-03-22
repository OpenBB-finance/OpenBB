from pydantic.dataclasses import dataclass

from openbb_terminal.core.models.credentials_model import CredentialsModel
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.models.profile_model import ProfileModel


@dataclass(config=dict(validate_assignment=True, frozen=True))
class UserModel:
    """Data model for user."""

    profile: ProfileModel
    credentials: CredentialsModel
    preferences: PreferencesModel
