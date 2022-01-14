"""Rich Module"""
__docformat__ = "numpy"

import sys

from rich import panel
from rich.console import Console, Theme
from gamestonk_terminal import feature_flags as gtff

# https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
# https://rich.readthedocs.io/en/latest/highlighting.html#custom-highlighters

CUSTOM_THEME = Theme(
    {
        # information provided to the user
        "info": "thistle1",
        # triggers a command
        "cmds": "light_sky_blue1",
        # configurable parameter
        "param": "gold3",
        # goes into a new menu
        "menu": "rgb(175,0,255)",
        # data sources,
        "src": "rgb(245,245,30)",
        # print help,
        "help": "green",
        # unavailable command/parameter
        "unvl": "dim",
    }
)


class NoConsole:
    """Create a dummy rich console to wrap the console print"""

    def print(self, *args, **kwargs):
        print(*args, **kwargs)


def no_panel(renderable, *args, **kwargs):  # pylint: disable=unused-argument
    return renderable


def build_console():
    if gtff.ENABLE_RICH:
        new_console = Console(theme=CUSTOM_THEME, highlight=False, soft_wrap=True)
    else:
        new_console = NoConsole()
        panel.Panel = no_panel

    return new_console


def disable_rich():
    sys.modules[__name__].console = NoConsole()
    sys.modules[__name__].panel.Panel = no_panel


console = build_console()
