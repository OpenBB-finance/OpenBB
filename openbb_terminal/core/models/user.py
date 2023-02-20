from typing import Optional
from pydantic.dataclasses import dataclass

from openbb_terminal.core.models.profile import ProfileModel, default_profile
from openbb_terminal.core.models.configurations import ConfigurationsModel
from openbb_terminal.core.models.credentials import CredentialsModel
from openbb_terminal.core.models.preferences import PreferencesModel

import openbb_terminal.feature_flags as obbff


@dataclass(config=dict(validate_assignment=True))
class UserModel:
    """Data model for user."""

    profile: ProfileModel

    # To be implemented
    configurations: Optional[ConfigurationsModel]
    preferences: Optional[PreferencesModel]
    credentials: Optional[CredentialsModel]

    @staticmethod
    def is_sync_enabled():
        """Check if sync is enabled."""
        return obbff.SYNC_ENABLED

    def update_flair(self, flair: str):
        """Update flair if user has not changed it.

        Parameters
        ----------
        flair : str
            The flair.
        """
        if flair is None:
            MAX_FLAIR_LEN = 20
            setattr(
                obbff,
                "USE_FLAIR",
                "[" + self.profile.username[:MAX_FLAIR_LEN] + "]" + " 🦋",
            )

    @staticmethod
    def clear():
        """Clear user info."""
        obbff.USE_FLAIR = ":openbb"


default_user = UserModel(  # type: ignore
    profile=default_profile,
    configurations=None,
    preferences=None,
    credentials=None,
)
