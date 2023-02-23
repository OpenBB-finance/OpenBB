# IMPORTS STANDARD
from copy import deepcopy
from typing import Any, Dict

# IMPORTS THIRDPARTY
from dotenv import dotenv_values

# IMPORTS INTERNAL
import openbb_terminal.feature_flags as obbff
from openbb_terminal.core.config.paths import (
    PACKAGE_ENV_FILE,
    REPOSITORY_ENV_FILE,
    USER_ENV_FILE,
)
from openbb_terminal.core.models.user_credentials import CredentialsModel
from openbb_terminal.core.models.user_model import UserModel
from openbb_terminal.session.hub_model import REGISTER_URL


def __reading_env() -> Dict[str, Any]:
    __env_dict = {
        **dotenv_values(REPOSITORY_ENV_FILE),
        **dotenv_values(PACKAGE_ENV_FILE),
        **dotenv_values(USER_ENV_FILE),
    }
    __env_dict_filtered = {
        k[len("OPENBBB_") - 1 :]: v for k, v in __env_dict.items() if k.startswith("OPENBB_")
    }

    return __env_dict_filtered

__credentials = CredentialsModel(**__reading_env())
__local_user = UserModel(credentials=__credentials)  # type:ignore
__current_user = None


def init_user():
    """Initialize user."""
    global __current_user  # pylint: disable=global-statement
    __current_user = __local_user


def get_current_user() -> UserModel:
    """Get current user."""
    return deepcopy(__current_user)


def set_current_user(user: UserModel):
    """Set current user."""
    global __current_user  # pylint: disable=global-statement
    __current_user = user


def is_guest() -> bool:
    """Check if user is guest.

    Returns
    -------
    bool
        True if user is guest, False otherwise.
    """
    return not bool(__current_user.profile.token)

# Helpers


def reset_flair(user: UserModel):
    """Clear user info."""
    # Use PreferencesModel when it is implemented.
    obbff.USE_FLAIR = ":openbb"


def update_flair(flair: str):
    """Update flair if user has not changed it.

    Parameters
    ----------
    flair : str
        The flair.
    """
    # Use PreferencesModel when it is implemented.
    if flair is None:
        MAX_FLAIR_LEN = 20
        setattr(
            obbff,
            "USE_FLAIR",
            "[" + get_current_user().profile.username[:MAX_FLAIR_LEN] + "]" + " 🦋",
        )
