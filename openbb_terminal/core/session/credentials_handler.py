# IMPORTS STANDARD
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

LOCAL_KEYS = [
    "RH_USERNAME",
    "RH_PASSWORD",
    "DG_USERNAME",
    "DG_PASSWORD",
    "DG_TOTP_SECRET",
    "OANDA_ACCOUNT_TYPE",
    "OANDA_ACCOUNT",
    "OANDA_TOKEN",
    "API_TRADIER_TOKEN",
    "API_BINANCE_KEY",
    "API_BINANCE_SECRET",
    "API_COINBASE_KEY",
    "API_COINBASE_SECRET",
    "API_COINBASE_PASS_PHRASE",
]


def set_credential(
    name: str,
    value: str,
    persist: bool = False,
    login: bool = False,
):
    """Set credential

    Parameters
    ----------
    name : str
        Credential name
    value : str
        Credential value
    persist : bool
        Force saving to .env file
    login : bool
        If preference set during login
    """

    current_user = get_current_user()
    sync_enabled = current_user.preferences.SYNC_ENABLED
    local_user = is_local()

    if persist and local_user:
        set_key(str(SETTINGS_ENV_FILE), name, str(value))

    # Remove "OPENBB_" prefix from env_var
    if name.startswith("OPENBB_"):
        name = name[7:]

    # Set credential in current user
    updated_credentials = dataclasses.replace(current_user.credentials, **{name: value})
    updated_user = dataclasses.replace(current_user, credentials=updated_credentials)
    set_current_user(updated_user)

    # Send credential to cloud
    if (
        not local_user
        and sync_enabled
        and name not in LOCAL_KEYS
        and (name.startswith("API_") or name.startswith("OPENBB_"))
        and not login
    ):
        patch_user_configs(
            key=name,
            value=str(value),
            type_="keys",
            auth_header=current_user.profile.get_auth_header(),
        )
