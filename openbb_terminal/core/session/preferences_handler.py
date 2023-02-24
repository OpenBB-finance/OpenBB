# IMPORTS STANDARD
from pathlib import Path
from typing import Union
import dataclasses

# IMPORTS THIRDPARTY
from dotenv import set_key

# IMPORTS INTERNAL
from openbb_terminal.core.config.paths import SETTINGS_ENV_FILE
from openbb_terminal.core.session.current_user import (
    get_current_user,
    is_local,
    set_current_user,
)
from openbb_terminal.core.session.hub_model import patch_user_configs


def set_preference(name: str, value: Union[bool, Path, str], force: bool = False):
    """Set preference

    Parameters
    ----------
    name : str
        Preference name
    value : Union[bool, Path, str]
        Preference value
    force : bool
        Force sending to cloud
    """

    current_user = get_current_user()
    sync_enabled = current_user.preferences.SYNC_ENABLED
    local_user = is_local()

    if local_user:
        set_key(str(SETTINGS_ENV_FILE), name, str(value))

    # Remove "OPENBB_" prefix from env_var
    if name.startswith("OPENBB_"):
        name = name[7:]

    # Set preference in current user
    updated_preferences = dataclasses.replace(current_user.preferences, **{name: value})
    updated_user = dataclasses.replace(current_user, preferences=updated_preferences)
    set_current_user(updated_user)

    # Send preference to cloud
    if not sync_enabled and sync_enabled or force:
        patch_user_configs(
            key=name,
            value=str(value),
            type_="settings",
            auth_header=current_user.profile.get_auth_header(),
        )
