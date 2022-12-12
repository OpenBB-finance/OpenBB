from typing import List
import os
from openbb_terminal.rich_config import console

IGNORE: List[str] = ["OpenBBUserError", "OpenBBAPIError", "OpenBBBaseError"]


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


class OpenBBBaseError(Exception):
    """Base class for other OpenBB exceptions"""

    def __init__(self, message=None):

        if message:
            self.message = message
            console.print(self.message, style="info")


class OpenBBUserError(OpenBBBaseError):
    """Raised for user usage errors"""


class OpenBBAPIError(OpenBBBaseError):
    """Raised for API errors"""
