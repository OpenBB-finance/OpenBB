import dotenv
from openbb_terminal.base_helpers import load_env_vars, strtobool
from openbb_terminal.core.config.paths import USER_ENV_FILE
from openbb_terminal.rich_config import console

DISABLE_EXTRAS_WARNING = load_env_vars(
    "OPENBB_DISABLE_EXTRAS_WARNING", strtobool, False
)


def extras_warning():
    """Enable/disable warning for missing extras."""

    if DISABLE_EXTRAS_WARNING:
        key_value = "False"
    else:
        key_value = "True"

    dotenv.set_key(str(USER_ENV_FILE), "OPENBB_DISABLE_EXTRAS_WARNING", key_value)
    key_set = dotenv.get_key(str(USER_ENV_FILE), "OPENBB_DISABLE_EXTRAS_WARNING")

    if key_set == "False":
        console.print("Extras warning enabled.")
    elif key_set == "True":
        console.print("Extras warning disabled.")
