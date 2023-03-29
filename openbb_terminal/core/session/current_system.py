# IMPORTS STANDARD
from copy import deepcopy

# IMPORTS INTERNAL
from openbb_terminal.core.models import SystemModel
from openbb_terminal.core.session.env_handler import read_env
from openbb_terminal.core.session.utils import load_dict_to_model


def get_current_system() -> SystemModel:
    """Get current system."""
    return deepcopy(__system)


def set_current_system(system: SystemModel):
    """Set current system."""
    global __system  # pylint: disable=global-statement
    __system = system


__env_dict = read_env()
__system = load_dict_to_model(__env_dict, SystemModel)
