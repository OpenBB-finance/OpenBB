from copy import deepcopy
from typing import Any

from openbb_terminal.core.models import Settings
from openbb_terminal.core.session.env_handler import read_env
from openbb_terminal.core.session.utils import load_dict_to_model

__env_dict = read_env()
__current_settings = load_dict_to_model(__env_dict, Settings)


def get_current_settings() -> Settings:
    """Get current user."""
    return deepcopy(__current_settings)


def _set_current_settings(settings: Settings):
    """Set current user."""
    global __current_settings  # pylint: disable=global-statement # noqa
    __current_settings = settings


def set_settings(
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
    settings = get_current_settings()  # this is a copy of the settings in place
    setattr(settings, name, value)
    _set_current_settings(settings)
