"""Rich Module"""
__docformat__ = "numpy"

from rich.console import Console, Theme

custom_theme = Theme({"context": "red", "function": "blue", "noticker": "dim"})

t_console = Console(theme=custom_theme)
