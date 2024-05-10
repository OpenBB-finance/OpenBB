"""Configuration for the CLI."""

import copy
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, TypeVar

from openbb_cli.config.constants import ENV_FILE_SETTINGS, SETTINGS_DIRECTORY

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


def bootstrap():
    """Setup pre-launch configurations for the CLI."""
    SETTINGS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    Path(ENV_FILE_SETTINGS).touch(exist_ok=True)
