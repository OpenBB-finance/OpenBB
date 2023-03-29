# IMPORTATION STANDARD
import dataclasses
from pathlib import Path

# IMPORTATION THIRDPARTY
from typing import Optional

import i18n

# IMPORTATION INTERNAL
from openbb_terminal.base_helpers import load_env_files, load_env_vars, strtobool
from openbb_terminal.core.config.paths import I18N_DICT_LOCATION
from openbb_terminal.core.config.paths_helper import init_userdata
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.current_system import (
    get_current_system,
    set_current_system,
)
from openbb_terminal.core.session.current_user import get_current_user

from .helper_classes import TerminalStyle as _TerminalStyle


def start_plot_backend():
    """Starts the plot backend"""
    plots_backend().start(load_env_vars("DEBUG_MODE", strtobool, False))


def change_logging_suppress(new_value: bool):
    """Change the logging suppress value"""
    current_system = get_current_system()
    updated_system = dataclasses.replace(current_system, LOGGING_SUPPRESS=new_value)  # type: ignore
    set_current_system(updated_system)


def setup_i18n(i18n_path: Path = I18N_DICT_LOCATION):
    """Select the terminal translation language."""

    i18n.load_path.append(i18n_path)
    i18n.set("locale", get_current_user().preferences.USE_LANGUAGE)
    i18n.set("filename_format", "{locale}.{format}")


def setup_version():
    """Setup the version of the terminal"""

    def try_get_version_from_dist() -> Optional[str]:
        def check_using_git():
            try:
                __import__("git")
            except ImportError:
                return False
            return True

        if not check_using_git():
            try:
                import pkg_resources  # pylint:disable=import-outside-toplevel

                return pkg_resources.get_distribution("OpenBB").version

            except Exception:
                pass

        return None

    version = try_get_version_from_dist()

    if version:
        current_system = get_current_system()
        updated_system = dataclasses.replace(current_system, VERSION=version)  # type: ignore
        set_current_system(updated_system)


def setup_logging_app_name():
    """
    Setup the logging app name of the terminal

    - if there's a LOGGING_APP_NAME in the environment => use it
    - if "site-packages" in __file__ => use "gst_packaged_pypi" (will override environment variable)
    - if none of the above => use "gst" (which is the default value on the SystemModel)
    """

    if "site-packages" in __file__:
        current_system = get_current_system()
        updated_system = dataclasses.replace(
            current_system, LOGGING_APP_NAME="gst_packaged_pypi"
        )  # type: ignore
        set_current_system(updated_system)


def setup_logging_sub_app(sub_app: str):
    """Setup the logging sub app"""

    current_system = get_current_system()
    updated_system = dataclasses.replace(current_system, LOGGING_SUB_APP=sub_app)  # type: ignore
    set_current_system(updated_system)


def setup_config_terminal():
    """Setup the config terminal"""
    load_env_files()
    init_userdata()
    start_plot_backend()
    setup_i18n()
    setup_version()
    setup_logging_app_name()


# Terminal UX section
current_user = get_current_user()
theme = _TerminalStyle(
    current_user.preferences.MPL_STYLE,
    current_user.preferences.PMF_STYLE,
    current_user.preferences.RICH_STYLE,
)
