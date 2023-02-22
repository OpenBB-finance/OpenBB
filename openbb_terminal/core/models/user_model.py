from pydantic.dataclasses import dataclass

import openbb_terminal.feature_flags as obbff
# from openbb_terminal.core.models.user_configurations import ConfigurationsModel
# from openbb_terminal.core.models.user_credentials import CredentialsModel
# from openbb_terminal.core.models.user_preferences import PreferencesModel
from openbb_terminal.core.models.user_profile import ProfileModel


@dataclass(config=dict(validate_assignment=True))
class UserModel:
    """Data model for user."""

    profile: ProfileModel = ProfileModel()
    # configurations: ConfigurationsModel
    # preferences: PreferencesModel
    # credentials: CredentialsModel

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
    def reset_flair():
        """Clear user info."""
        # This is a temporary solution until we implement PreferencesModel.
        obbff.USE_FLAIR = ":openbb"
