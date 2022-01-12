"""Rich Module"""
__docformat__ = "numpy"

from rich.console import Console, Theme

# https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
# https://rich.readthedocs.io/en/latest/highlighting.html#custom-highlighters

custom_theme = Theme(
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

# Obviouse setup to make sure it works
# soft_wrap=True is must be on or many tests fail
console = Console(theme=custom_theme, highlight=False, soft_wrap=True)
