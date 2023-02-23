# IMPORTS STANDARD
from copy import deepcopy
from typing import Any, Dict

# IMPORTS THIRDPARTY
from dotenv import dotenv_values

# IMPORTS INTERNAL
from openbb_terminal.core.config.paths import (
    PACKAGE_ENV_FILE,
    REPOSITORY_ENV_FILE,
    USER_ENV_FILE,
)
from openbb_terminal.core.models.user_credentials import CredentialsModel
from openbb_terminal.core.models.user_model import UserModel


def __reading_env() -> Dict[str, Any]:
    __env_dict = {
        **dotenv_values(REPOSITORY_ENV_FILE),
        **dotenv_values(PACKAGE_ENV_FILE),
        **dotenv_values(USER_ENV_FILE),
    }
    __env_dict_filtered = {
        k[len("OPENBBB_") - 1 :]: v
        for k, v in __env_dict.items()
        if k.startswith("OPENBB_")
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
