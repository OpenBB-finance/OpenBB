from typing import List
import os
from openbb_terminal.rich_config import console

IGNORE_ERROR: List[str] = []
RAISE_ERROR: List[str] = []
IGNORE_ERROR_LIST = [item for item in IGNORE_ERROR if item not in RAISE_ERROR]

IGNORE_BASE_ERRORS: List[str] = ["OpenBBUserError", "OpenBBDevError"]
RAISE_BASE_ERRORS: List[str] = []
IGNORE_BASE_ERRORS_LIST = [
    item for item in IGNORE_BASE_ERRORS if item not in RAISE_BASE_ERRORS
]


def handle_exception(exception=None, logger=None) -> None:
    """Handle exceptions

    Parameters
    ----------
    exception : Exception
        Exception to handle
    logger : logging.Logger
        Logger to use

    Returns
    -------
    None
    """

    name = exception.__class__.__name__
    base_name = exception.__class__.__bases__[0].__name__

    if base_name in IGNORE_BASE_ERRORS_LIST:
        pass
    elif name in IGNORE_ERROR_LIST:
        pass
    elif name == "RequestException":
        console.print(
            "[red]There was an error connecting to the API. Please try again later.\n[/red]"
        )
        log_exception(exception, logger)
    elif name == "SSLError":
        console.print(
            "[red]There was an error connecting to the API. Please check whether your wifi is blocking this site.\n[/red]"
        )
        log_exception(exception, logger)
    elif os.environ.get("DEBUG_MODE") == "true":
        raise exception
    else:
        console.print("[red]Unexpected error.\n[/red]")
        log_exception(exception, logger)


def log_exception(exception=None, logger=None) -> None:
    """Log exception

    Parameters
    ----------
    exception : Exception
        Exception to log
    logger : logging.Logger
        Logger to use

    Returns
    -------
    None
    """
    if logger:
        logger.exception(
            "Exception: %s",
            str(exception),
        )


class OpenBBBaseError(Exception):
    """Base class for other exceptions"""

    def __init__(self, message=None, **kwargs):
        style = kwargs.get("style", "red")

        if message:
            self.message = message
            console.print(self.message, style=style)


class OpenBBUserError(OpenBBBaseError):
    """Raised for users"""


class OpenBBDevError(OpenBBBaseError):
    """Raised just for developers"""


# General exceptions
class OpenBBMissingAPIKeyError(OpenBBUserError):
    """Raised when the API key is missing"""

    def __init__(self):
        super().__init__(message="Please set your API key!")


class OpenBBAPIDownError(OpenBBDevError):
    """Raised when API is down"""

    def __init__(self):
        super().__init__(message="API down!")


# # We define two types of exceptions:
# # 1. Expected exceptions -> we should catch OpenBB expected exceptions and handle them
# # 1.1. General exceptions, like OpenBBMissingAPIKeyError, OpenBBAPIDownError
# #   - These exceptions are provided by us and contributors should not change its format.
# #     They should inherit from OpenBBBaseError, so that we can treat them as expected.
# # 1.2. Specific exceptions, like CurrencyPairNotLoadedError
# #   - These exceptions can be created and used by contributors at will.
# #     They should inherit from OpenBBBaseError, so that we can treat them as expected.
# # 1.3. Exceptions from external libraries, like requests.exceptions.RequestException
# #   - These exceptions are provided by external libraries and we treat them in
#       handle_exception function, for example by writing a meaningful message.
# # 2. Unexpected exceptions -> unexpected exceptions generally mean that there is a bug
#      in the code
# #   - If it's not a bug, it means it's expected so we should handle the exception and it
# #     will fall into the first category.

# # If the Base exception is not caught before, it will be caught here
# # We should not allow the Base exception to be raised intentionally
# # inside menus or other parts of the code.
# # The Base exception should only be raised if there is a bug in the code
# # so that we can see it in the integration tests report and fix it.
# # The remaining exceptions can be detected in the report but will
# # not need to be fixed.
# # OpenBB custom exceptions are raised intentionally so they are expected
# # Base Exception is not expected
