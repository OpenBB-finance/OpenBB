# IMPORTS STANDARD
import dataclasses
from copy import deepcopy
from typing import Any

from openbb import obb
from openbb_core.app.model.user_settings import UserSettings

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


def get_platform_user() -> UserSettings:
    """Get platform user."""
    return deepcopy(obb.user)


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
    return not bool(obb.user.profile.hub_session)


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
