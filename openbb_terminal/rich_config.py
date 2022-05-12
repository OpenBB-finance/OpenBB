"""Rich Module"""
__docformat__ = "numpy"

import os
from typing import Tuple
from rich import panel
from rich.console import Console, Theme
from rich.text import Text
from rich.color import Color
from openbb_terminal import config_terminal as cfg
from openbb_terminal import feature_flags as obbff


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

USE_COLOR = True


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

    @staticmethod
    def blend_text(
        message: str, color1: Tuple[int, int, int], color2: Tuple[int, int, int]
    ) -> Text:
        """Blend text from one color to another."""
        text = Text(message)
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        dr = r2 - r1
        dg = g2 - g1
        db = b2 - b1
        size = len(text) + 5
        for index in range(size):
            blend = index / size
            color = f"#{int(r1 + dr * blend):02X}{int(g1 + dg * blend):02X}{int(b1 + db * blend):02X}"
            text.stylize(color, index, index + 1)
        return text

    def print(self, *args, **kwargs):
        if kwargs and "text" in list(kwargs) and "menu" in list(kwargs):
            if not os.getenv("TEST_MODE"):
                if obbff.ENABLE_RICH_PANEL:
                    version = self.blend_text(
                        f"OpenBB Terminal v{obbff.VERSION}",
                        Color.parse("#00AAFF").triplet,
                        Color.parse("#E4003A").triplet,
                    )
                    link = " (https://openbb.co)"
                    link_text = Text(link)
                    link_text.stylize("#FCED00", 0, len(link))
                    version += link_text
                    self.console.print(
                        panel.Panel(
                            kwargs["text"],
                            title=kwargs["menu"],
                            subtitle_align="right",
                            subtitle=version,
                        )
                    )

                else:
                    self.console.print(kwargs["text"])
            else:
                print(self.filter_rich_tags(kwargs["text"]))
        else:
            if not os.getenv("TEST_MODE"):
                self.console.print(*args, **kwargs)
            else:
                print(*args, **kwargs)


console = ConsoleAndPanel()
