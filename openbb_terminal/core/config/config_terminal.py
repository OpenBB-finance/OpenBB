"""Configuration for the terminal."""

import copy
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, TypeVar

import i18n

from openbb_terminal.core.config.paths import I18N_DICT_LOCATION
from openbb_terminal.core.session.env_handler import load_env_files

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure

# ruff: noqa:PLW0603

OpenBBFigureT = TypeVar("OpenBBFigureT", bound="OpenBBFigure")
HOLD: bool = False
COMMAND_ON_CHART: bool = True
current_figure: Optional[OpenBBFigureT] = None  # type: ignore
new_axis: bool = True
legends: List = []
last_legend = ""


# pylint: disable=global-statement
def set_last_legend(leg: str):
    """Set the last legend."""
    global last_legend
    last_legend = copy.deepcopy(leg)


def reset_legend() -> None:
    """Reset the legend."""
    global legends
    legends = []


def get_legends() -> list:
    """Get the legends."""
    return legends


def set_same_axis() -> None:
    """Set the same axis."""
    global new_axis
    new_axis = False


def set_new_axis() -> None:
    """Set the new axis."""
    global new_axis
    new_axis = True


def make_new_axis() -> bool:
    """Make a new axis."""
    return new_axis


def get_current_figure() -> Optional["OpenBBFigure"]:
    """Get the current figure."""
    return current_figure


def set_current_figure(fig: Optional[OpenBBFigureT] = None):
    """Set the current figure."""
    # pylint: disable=global-statement
    global current_figure
    current_figure = fig


def setup_i18n(i18n_path: Path = I18N_DICT_LOCATION, lang: str = "en"):
    """Select the terminal translation language."""
    i18n.load_path.append(i18n_path)
    i18n.set("locale", lang)
    i18n.set("filename_format", "{locale}.{format}")


def setup_config_terminal():
    """Set up the config terminal."""
    load_env_files()

    # this should be only be imported after loading the env files
    # so that the settings are loaded correctly
    # pylint: disable=import-outside-toplevel
    from openbb_terminal.core.session.current_settings import get_current_settings

    lang = get_current_settings().USE_LANGUAGE

    setup_i18n(lang=lang)
