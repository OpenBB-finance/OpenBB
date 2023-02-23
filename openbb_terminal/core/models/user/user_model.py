from pydantic.dataclasses import dataclass

from openbb_terminal.core.models.user.credentials_model import CredentialsModel
from openbb_terminal.core.models.user.profile_model import ProfileModel
from openbb_terminal.core.models.user.preferences_model import PreferencesModel


@dataclass(config=dict(validate_assignment=True))
class UserModel:
    """Data model for user."""

    # configurations: ConfigurationsModel
    profile: ProfileModel
    credentials: CredentialsModel
    preferences: PreferencesModel
