# IMPORTS STANDARD
import dataclasses
from copy import deepcopy
from typing import Any

# IMPORTS INTERNAL
from openbb_terminal.core.models import Settings
from openbb_terminal.core.session.env_handler import read_env
from openbb_terminal.core.session.utils import load_dict_to_model

__env_dict = read_env()
__current_settings = load_dict_to_model(__env_dict, Settings)


def get_current_settings() -> Settings:
    """Get current user."""
    return deepcopy(__current_settings)


def set_current_settings(settings: Settings):
    """Set current user."""
    global __current_settings  # pylint: disable=global-statement # noqa
    __current_settings = settings


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
    current_settings = get_current_settings()
    updated_settings = dataclasses.replace(current_settings, **{name: value})  # type: ignore
    set_current_settings(updated_settings)
