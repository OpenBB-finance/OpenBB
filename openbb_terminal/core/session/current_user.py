# IMPORTS STANDARD
import dataclasses
from copy import deepcopy
from typing import Any, Dict, Optional

# IMPORTS INTERNAL
from openbb_terminal.core.models import (
    PreferencesModel,
    UserModel,
)
from openbb_terminal.core.session.env_handler import read_env
from openbb_terminal.core.session.utils import load_dict_to_model

__env_dict = read_env()
__preferences = load_dict_to_model(__env_dict, PreferencesModel)


__local_user = UserModel(  # type: ignore
    preferences=__preferences,  # type: ignore
)
__current_user = __local_user


def get_current_user() -> UserModel:
    """Get current user."""
    return deepcopy(__current_user)


def set_current_user(user: UserModel):
    """Set current user."""
    global __current_user  # pylint: disable=global-statement # noqa
    __current_user = user


def get_env_dict() -> dict:
    """Get env dict."""
    return deepcopy(__env_dict)


def is_local() -> bool:
    """Check if user is guest.

    Returns
    -------
    bool
        True if user is guest, False otherwise.
    """
    # return not bool(__current_user.profile.token)
    return True


def set_default_user():
    """Set default user."""
    env_dict = read_env()
    preferences = load_dict_to_model(env_dict, PreferencesModel)
    default_user = UserModel(preferences=preferences)
    set_current_user(default_user)


def copy_user(
    preferences: Optional[PreferencesModel] = None,
    user: Optional[UserModel] = None,
):
    current_user = user or get_current_user()
    preferences = preferences or current_user.preferences

    user_copy = UserModel(preferences=preferences)

    return user_copy


def set_preference(
    name: str,
    value: Any,
):
    """Set preference

    Parameters
    ----------
    name : str
        Preference name
    value : Any
        Preference value
    """
    current_user = get_current_user()
    updated_preferences = dataclasses.replace(current_user.preferences, **{name: value})  # type: ignore
    updated_user = dataclasses.replace(current_user, preferences=updated_preferences)  # type: ignore
    set_current_user(updated_user)


def set_credential(name: str, value: str):
    """Set credential

    Parameters
    ----------
    name : str
        Credential name
    value : str
        Credential value
    """
    current_user = get_current_user()
    updated_credentials = dataclasses.replace(current_user.credentials, **{name: value})  # type: ignore
    updated_user = dataclasses.replace(current_user, credentials=updated_credentials)  # type: ignore
    set_current_user(updated_user)


def set_sources(choices: Dict):
    """Set sources

    Parameters
    ----------
    choices : Dict
        Sources dict
    """
    current_user = get_current_user()
    updated_sources = dataclasses.replace(current_user.sources, choices=choices)  # type: ignore
    updated_user = dataclasses.replace(current_user, sources=updated_sources)  # type: ignore
    set_current_user(updated_user)
