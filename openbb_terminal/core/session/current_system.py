# IMPORTS STANDARD
import dataclasses
from copy import deepcopy
from typing import Any

# IMPORTS INTERNAL
from openbb_terminal.core.models import SystemModel
from openbb_terminal.core.session.env_handler import read_env
from openbb_terminal.core.session.utils import load_dict_to_model


def get_current_system() -> SystemModel:
    """Get current system."""
    return deepcopy(__system)


def set_current_system(system: SystemModel):
    """Set current system."""
    global __system  # pylint: disable=global-statement# noqa: PLW0603
    __system = system


def set_system_variable(
    name: str,
    value: Any,
):
    """Set system variable

    Parameters
    ----------
    name : str
        Variable name
    value : Any
        Variable value
    """
    current_system = get_current_system()
    updated_system = dataclasses.replace(current_system, **{name: value})  # type: ignore
    set_current_system(updated_system)


__env_dict = read_env()
__system = load_dict_to_model(__env_dict, SystemModel)
