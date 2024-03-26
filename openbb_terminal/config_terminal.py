import copy
from pathlib import Path
from typing import TYPE_CHECKING, Optional, TypeVar

import i18n

from openbb_terminal.base_helpers import load_env_files
from openbb_terminal.core.config.paths import I18N_DICT_LOCATION

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure


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


def setup_i18n(i18n_path: Path = I18N_DICT_LOCATION, lang: str = "en"):
    """Select the terminal translation language."""

    i18n.load_path.append(i18n_path)
    i18n.set("locale", lang)
    i18n.set("filename_format", "{locale}.{format}")


def setup_config_terminal():
    """Setup the config terminal"""
    load_env_files()

    # this should be only be imported after loading the env files
    # so that the settings are loaded correctly
    # pylint: disable=import-outside-toplevel
    from openbb_terminal.core.session.current_settings import get_current_settings

    lang = get_current_settings().USE_LANGUAGE

    setup_i18n(lang=lang)
