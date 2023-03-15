# IMPORTS STANDARD
from copy import deepcopy

# IMPORTS INTERNAL
from openbb_terminal.core.models import SystemModel
from openbb_terminal.core.session.env_handler import load_env_to_model, reading_env

__env_dict = reading_env()
__system = load_env_to_model(__env_dict, SystemModel)


def get_current_system() -> SystemModel:
    """Get current system."""
    return deepcopy(__system)


def set_current_system(system: SystemModel):
    """Set current system."""
    global __system  # pylint: disable=global-statement
    __system = system
