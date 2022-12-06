from typing import List
import os
from openbb_terminal.rich_config import console

IGNORE_ERROR: List[str] = ["OpenBBUserError"]


def handle_exception(exception=None) -> None:
    """Handle exceptions

    Parameters
    ----------
    exception : Exception
        Exception to handle

    Returns
    -------
    None
    """

    ignore_exception_list = IGNORE_ERROR

    exception_name = exception.__class__.__name__

    if exception_name in ignore_exception_list:
        pass
    elif exception_name == "RequestException":
        console.print(
            "[red]There was an error connecting to the API. Please try again later.\n[/red]"
        )
    elif exception_name == "SSLError":
        console.print(
            "[red]There was an error connecting to the API. Please check whether your wifi is blocking this site.\n[/red]"
        )
    elif os.environ.get("DEBUG_MODE") == "true":
        raise exception
    else:
        console.print("[red]Unexpected error.[/red]")


class OpenBBBaseError(Exception):
    """Base class for other exceptions"""

    def __init__(self, message=None, **kwargs):
        style = kwargs.get("style", "red")

        if message:
            self.message = message
            console.print(self.message, style=style)


class OpenBBUserError(OpenBBBaseError):
    """Raised for users"""
