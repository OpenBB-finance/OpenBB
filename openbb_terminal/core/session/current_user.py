# IMPORTS STANDARD
from copy import deepcopy
from typing import Optional

# IMPORTS INTERNAL
from openbb_terminal.core.models import (
    CredentialsModel,
    PreferencesModel,
    ProfileModel,
    UserModel,
)
from openbb_terminal.core.session.env_handler import load_env_to_model, reading_env

__env_dict = reading_env()
__credentials = load_env_to_model(__env_dict, CredentialsModel)
__preferences = load_env_to_model(__env_dict, PreferencesModel)


__profile = ProfileModel()
__local_user = UserModel(  # type: ignore
    credentials=__credentials,
    preferences=__preferences,
    profile=__profile,
)
__current_user = __local_user


def get_current_user() -> UserModel:
    """Get current user."""
    return deepcopy(__current_user)


def set_current_user(user: UserModel):
    """Set current user."""
    global __current_user  # pylint: disable=global-statement
    __current_user = user


def is_local() -> bool:
    """Check if user is guest.

    Returns
    -------
    bool
        True if user is guest, False otherwise.
    """
    return not bool(__current_user.profile.token)


def copy_user(
    credentials: Optional[CredentialsModel] = None,
    preferences: Optional[PreferencesModel] = None,
    profile: Optional[ProfileModel] = None,
    user: Optional[UserModel] = None,
):
    current_user = user or get_current_user()
    credentials = credentials or current_user.credentials
    preferences = preferences or current_user.preferences
    profile = profile or current_user.profile

    user_copy = UserModel(  # type: ignore
        credentials=credentials,
        preferences=preferences,
        profile=profile,
    )

    return user_copy
