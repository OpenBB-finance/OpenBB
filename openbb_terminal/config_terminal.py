# IMPORTATION STANDARD
import copy
from pathlib import Path

# IMPORTATION THIRDPARTY
from typing import TYPE_CHECKING, Optional, TypeVar

import i18n

# IMPORTATION INTERNAL
from openbb_terminal.base_helpers import load_env_files
from openbb_terminal.core.config.paths import I18N_DICT_LOCATION
from openbb_terminal.core.config.paths_helper import init_userdata
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.current_system import (
    get_current_system,
    set_system_variable,
)
from openbb_terminal.core.session.current_user import get_current_user

from .helper_classes import TerminalStyle as _TerminalStyle

if TYPE_CHECKING:
    from openbb_terminal import OpenBBFigure


OpenBBFigureT = TypeVar("OpenBBFigureT", bound="OpenBBFigure")
HOLD: bool = False
COMMAND_ON_CHART: bool = True
current_figure: Optional[OpenBBFigureT] = None  # type: ignore
new_axis: bool = True
legends = []
last_legend = ""


# pylint: disable=global-statement
def set_last_legend(leg: str):
    global last_legend
    last_legend = copy.deepcopy(leg)


def get_last_legend() -> str:
    return copy.deepcopy(last_legend)


def append_legend(append_leg: str):
    global legends
    legends.append(append_leg)
    legends = copy.deepcopy(legends)


def reset_legend():
    global legends
    legends = []


def get_legends() -> list:
    return legends


def set_same_axis() -> None:
    global new_axis
    new_axis = False


def set_new_axis() -> None:
    global new_axis
    new_axis = True


def make_new_axis() -> bool:
    return new_axis


def get_current_figure() -> Optional["OpenBBFigure"]:
    return current_figure


def set_current_figure(fig: Optional[OpenBBFigureT] = None):
    # pylint: disable=global-statement
    global current_figure
    current_figure = fig


def start_plot_backend():
    """Starts the plot backend"""
    plots_backend().start(get_current_system().DEBUG_MODE)


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
        set_system_variable("VERSION", version)


def setup_logging_app_name():
    """
    Setup the logging app name of the terminal

    - if there's a LOGGING_APP_NAME in the environment => use it
    - if "site-packages" in __file__ => use "gst_packaged_pypi" (will override environment variable)
    - if none of the above => use "gst" (which is the default value on the SystemModel)
    """

    if "site-packages" in __file__:
        set_system_variable("LOGGING_APP_NAME", "gst_packaged_pypi")


def setup_config_terminal(is_sdk: bool = False):
    """Setup the config terminal"""
    load_env_files()
    init_userdata()
    # To avoid starting plots backend twice
    if is_sdk:
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
