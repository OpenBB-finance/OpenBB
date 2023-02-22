from pydantic.dataclasses import dataclass

import openbb_terminal.feature_flags as obbff
# from openbb_terminal.core.models.configurations import (
#     ConfigurationsModel,
#     default_configurations,
# )
# from openbb_terminal.core.models.credentials import (
#     CredentialsModel,
#     default_credentials,
# )
# from openbb_terminal.core.models.preferences import (
#     PreferencesModel,
#     default_preferences,
# )
from openbb_terminal.core.models.profile import ProfileModel, default_profile


@dataclass(config=dict(validate_assignment=True))
class UserModel:
    """Data model for user."""

    profile: ProfileModel
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


default_user = UserModel(  # type: ignore
    profile=default_profile,
    # configurations=default_configurations,
    # preferences=default_preferences,
    # credentials=default_credentials,
)
