# IMPORTS STANDARD
import dataclasses
from pathlib import Path
from typing import Union

# IMPORTS THIRDPARTY
# IMPORTS INTERNAL
from openbb_terminal.core.session.current_user import (
    get_current_user,
    set_current_user,
)
from openbb_terminal.core.session.env_handler import write_to_dotenv


def set_preference(
    name: str,
    value: Union[bool, Path, str],
):
    """Set preference

    Parameters
    ----------
    name : str
        Preference name
    value : Union[bool, Path, str]
        Preference value
    login : bool
        If the preference is set during login
    """

    current_user = get_current_user()

    # Set preference in current user
    updated_preferences = dataclasses.replace(current_user.preferences, **{name: value})
    updated_user = dataclasses.replace(current_user, preferences=updated_preferences)
    set_current_user(updated_user)

    # Set preference in local .env file
    write_to_dotenv(name, str(value))
