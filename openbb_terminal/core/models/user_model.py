from pydantic.dataclasses import dataclass

from openbb_terminal.core.models.base_model import BaseModel
from openbb_terminal.core.models.credentials_model import CredentialsModel
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.models.profile_model import ProfileModel
from openbb_terminal.core.models.sources_model import SourcesModel


@dataclass(config=dict(validate_assignment=True, frozen=True))
class UserModel(BaseModel):
    """Data model for user."""

    profile: ProfileModel
    credentials: CredentialsModel
    preferences: PreferencesModel
    sources: SourcesModel
