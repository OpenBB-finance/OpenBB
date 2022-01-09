"""Rich Module"""
__docformat__ = "numpy"

from rich.console import Console, Theme

# https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
# https://rich.readthedocs.io/en/latest/highlighting.html#custom-highlighters

custom_theme = Theme(
    {
        # information provided to the user
        "info": "thistle1",
        # goes into a new menu
        "menu": "medium_violet_red",
        # triggers a command
        "cmds": "light_sky_blue1",
        # configurable parameter
        "param": "gold3",
        # unavailable command/parameter
        "unvl": "dim",
    }
)

# Obviouse setup to make sure it works
console = Console(theme=custom_theme, style="white", highlight=False)
