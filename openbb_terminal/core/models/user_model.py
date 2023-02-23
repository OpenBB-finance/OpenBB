from pydantic.dataclasses import dataclass

from openbb_terminal.core.models.user_credentials import CredentialsModel
from openbb_terminal.core.models.user_profile import ProfileModel

# from openbb_terminal.core.models.user_configurations import ConfigurationsModel
from openbb_terminal.core.models.user_preferences import PreferencesModel


@dataclass(config=dict(validate_assignment=True))
class UserModel:
    """Data model for user."""

    # configurations: ConfigurationsModel
    profile: ProfileModel
    credentials: CredentialsModel
    preferences: PreferencesModel
