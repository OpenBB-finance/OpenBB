"""Rich Module"""
__docformat__ = "numpy"

from rich.console import Console, Theme

custom_theme = Theme({"context": "red", "function": "blue", "noticker": "dim"})

# Obviouse setup to make sure it works
console = Console(theme=custom_theme, style="bold white on blue")
