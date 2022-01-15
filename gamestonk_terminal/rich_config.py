"""Rich Module"""
__docformat__ = "numpy"

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

RICH_TAGS = [
    "[menu]",
    "[/menu]",
    "[cmds]",
    "[/cmds]",
    "[info]",
    "[/info]",
    "[param]",
    "[/param]",
    "[src]",
    "[/src]",
    "[help]",
    "[/help]",
]


def no_panel(renderable, *args, **kwargs):  # pylint: disable=unused-argument
    return renderable


class ConsoleAndPanel:
    """Create a rich console to wrap the console print with a Panel"""

    def __init__(self):
        self.console = Console(theme=CUSTOM_THEME, highlight=False, soft_wrap=True)

    @staticmethod
    def filter_rich_tags(text):
        for val in RICH_TAGS:
            text = text.replace(val, "")

        return text

    def print(self, *args, **kwargs):
        if kwargs and "text" in list(kwargs) and "menu" in list(kwargs):
            if gtff.ENABLE_RICH:
                if gtff.ENABLE_RICH_PANEL:
                    self.console.print(
                        panel.Panel(
                            kwargs["text"],
                            title=kwargs["menu"],
                            subtitle_align="right",
                            subtitle="Gamestonk Terminal",
                        )
                    )
                else:
                    self.console.print(kwargs["text"])
            else:
                print(self.filter_rich_tags(kwargs["text"]))
        else:
            if gtff.ENABLE_RICH:
                self.console.print(*args, **kwargs)
            else:
                print(*args, **kwargs)


console = ConsoleAndPanel()


def disable_rich():
    gtff.ENABLE_RICH = False
