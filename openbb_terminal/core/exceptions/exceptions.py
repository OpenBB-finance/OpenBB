from typing import List
import os
from openbb_terminal.rich_config import console

IGNORE: List[str] = ["OpenBBUserError"]


def handle_exception(exception: Exception) -> None:
    """Handle exceptions

    Parameters
    ----------
    exception : Exception
        Exception to handle

    Returns
    -------
    None
    """

    ignore_exception_list = IGNORE
    exception_name = exception.__class__.__name__

    if exception_name in ignore_exception_list:
        pass
    elif os.environ.get("DEBUG_MODE") == "true":
        raise exception
    elif exception_name == "RequestException":
        console.print(
            "There was an error connecting to the API. Please try again later.",
            style="red",
        )
    elif exception_name == "SSLError":
        console.print(
            "There was an error connecting to the API. "
            + "Please check whether your wifi is blocking this site.",
            style="red",
        )
    else:
        console.print("An unexpected error occurred.", style="red")


def shout(message: str) -> None:
    """Raises an OpenBBUserError

    Parameters
    ----------
    message : str
        Error message

    Returns
    -------
    None
    """
    raise OpenBBUserError(message)


class OpenBBUserError(Exception):
    """OpenBB exception"""

    def __init__(self, message: str):

        if message:
            self.message = "Error: " + message
            console.print(self.message, style="red")
