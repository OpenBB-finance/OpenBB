# IMPORTS STANDARD
from copy import deepcopy

# IMPORTS INTERNAL
from openbb_terminal.core.models.user.credentials_model import CredentialsModel
from openbb_terminal.core.models.user.user_model import UserModel
from openbb_terminal.core.models.user.preferences_model import PreferenceModel
from openbb_terminal.core.models.user.profile_model import ProfileModel
from openbb_terminal.core.session.env_handler import reading_env

__env_dict = reading_env()
__credentials = CredentialsModel(**__env_dict)
__preferences = PreferenceModel(**__env_dict)
__profile = ProfileModel()
__local_user = UserModel(
    credentials=__credentials,
    preferences=__preferences,
    profile=__profile,
)
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
