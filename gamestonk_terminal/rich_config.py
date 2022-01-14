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
        "info": "rgb(224,131,48)",
        # triggers a command
        "cmds": "rgb(70,156,222)",
        # configurable parameter
        "param": "rgb(247,206,70)",
        # goes into a new menu
        "menu": "rgb(50,115,185)",
        # data sources,
        "src": "rgb(216,90,64)",
        # print help,
        "help": "green",
        # unavailable command/parameter
        "unvl": "grey30",
    }
)


class NoConsole:
    """Create a dummy rich console to wrap the console print"""

    def print(self, *args, **kwargs):
        print(*args, **kwargs)


class ConsoleAndPanel:
    """Create a rich console to wrap the console print with a Panel"""

    def print(self, *args, **kwargs):
        new_console = Console(theme=CUSTOM_THEME, highlight=False, soft_wrap=True)
        if kwargs and "text" in list(kwargs) and "menu" in list(kwargs):
            if gtff.ENABLE_RICH_PANEL:
                new_console.print(
                    panel.Panel(
                        kwargs["text"],
                        title=kwargs["menu"],
                        subtitle_align="right",
                        subtitle="Gamestonk Terminal",
                    )
                )
            else:
                new_console.print(kwargs["text"])
        else:
            new_console.print(*args, **kwargs)


def no_panel(renderable, *args, **kwargs):  # pylint: disable=unused-argument
    return renderable


def build_console():
    if gtff.ENABLE_RICH:
        new_console = ConsoleAndPanel()
    else:
        new_console = NoConsole()
        panel.Panel = no_panel

    return new_console


def disable_rich():
    sys.modules[__name__].console = NoConsole()
    sys.modules[__name__].panel.Panel = no_panel


console = build_console()
