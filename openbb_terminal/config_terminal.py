from pathlib import Path
from typing import Optional

import i18n

from openbb_terminal.base_helpers import load_env_files
from openbb_terminal.core.config.paths import I18N_DICT_LOCATION
from openbb_terminal.core.config.paths_helper import init_userdata
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.current_system import (
    get_current_system,
    set_system_variable,
)
from openbb_terminal.core.session.current_user import get_current_user

from .helper_classes import TerminalStyle


def start_plot_backend():
    """Starts the plot backend."""
    plots_backend().start(get_current_system().DEBUG_MODE)


def configure_translation(translation_path: Path = I18N_DICT_LOCATION):
    """
    Sets up the translation language for the terminal.

    Args:
        translation_path (Path): The path to the translation dictionary.
    """
    i18n.load_path.append(translation_path)
    i18n.set("locale", get_current_user().preferences.USE_LANGUAGE)
    i18n.set("filename_format", "{locale}.{format}")


def get_terminal_version() -> Optional[str]:
    """
    Attempts to determine the version of the terminal.

    Returns:
        Optional[str]: The version of the terminal, or None if it could not be determined.
    """
    try:
        import pkg_resources
        return pkg_resources.get_distribution("OpenBB").version
    except Exception:
        return None


def set_terminal_version():
    """Sets the version of the terminal as a system variable."""
    version = get_terminal_version()
    if version:
        set_system_variable("VERSION", version)


def set_logging_app_name():
    """
    Sets up the logging app name for the terminal.

    - If there's a LOGGING_APP_NAME in the environment, use it.
    - If "site-packages" is in the current file's path, use "gst_packaged_pypi".
    - If none of the above conditions are met, use "gst" (the default value on the SystemModel).
    """
    if "site-packages" in __file__:
        set_system_variable("LOGGING_APP_NAME", "gst_packaged_pypi")


def setup_terminal_configuration(is_sdk: bool = False):
    """
    Sets up the terminal configuration.

    Args:
        is_sdk (bool, optional): Whether the terminal is running in SDK mode. Defaults to False.
    """
    load_env_files()
    init_userdata()

    # To avoid starting the plot backend twice
    if is_sdk:
        start_plot_backend()

    configure_translation()
    set_terminal_version()
    set_logging_app_name()


# Terminal UX section
current_user = get_current_user()
terminal_style = TerminalStyle(
    current_user.preferences.MPL_STYLE,
    current_user.preferences.PMF_STYLE,
    current_user.preferences.RICH_STYLE,
)
