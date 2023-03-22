# IMPORTS STANDARD
from copy import deepcopy

# IMPORTS INTERNAL
from openbb_terminal.core.models import SystemModel
from openbb_terminal.core.session.system_handler import handle_system, save_system


def get_current_system() -> SystemModel:
    """Get current system."""
    return deepcopy(__system)


def set_current_system(system: SystemModel):
    """Set current system."""
    global __system  # pylint: disable=global-statement
    save_system(system)
    __system = system


__system = handle_system()
