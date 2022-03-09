"""Rich Module"""
__docformat__ = "numpy"

from rich import panel
from rich.console import Console, Theme
from gamestonk_terminal import config_terminal as cfg

# https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
# https://rich.readthedocs.io/en/latest/highlighting.html#custom-highlighters

CUSTOM_THEME = Theme(cfg.theme.console_style)

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


ENABLE_RICH = True

ENABLE_RICH_PANEL = True


def no_panel(renderable, *args, **kwargs):  # pylint: disable=unused-argument
    return renderable


class ConsoleAndPanel:
    """Create a rich console to wrap the console print with a Panel"""

    def __init__(self):
        self.console = Console(theme=CUSTOM_THEME, highlight=False, soft_wrap=True)

    def capture(self):
        return self.console.capture()

    @staticmethod
    def filter_rich_tags(text):
        for val in RICH_TAGS:
            text = text.replace(val, "")

        return text

    def print(self, *args, **kwargs):
        if kwargs and "text" in list(kwargs) and "menu" in list(kwargs):
            if ENABLE_RICH:
                if ENABLE_RICH_PANEL:
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
            if ENABLE_RICH:
                self.console.print(*args, **kwargs)
            else:
                print(*args, **kwargs)


console = ConsoleAndPanel()


def disable_rich():
    ENABLE_RICH = False  # noqa: F841
