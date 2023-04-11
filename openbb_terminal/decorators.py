"""Decorators"""
__docformat__ = "numpy"
import functools
import logging
from ssl import SSLError

import pandas as pd
from requests.exceptions import RequestException

from openbb_terminal.core.session.current_system import get_current_system
from openbb_terminal.core.session.current_user import (
    get_current_user,
    set_current_user,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


def log_start_end(func=None, log=None):
    """Wrap function to add a log entry at execution start and end.

    Parameters
    ----------
    func : optional
        Function, by default None
    log : optional
        Logger, by default None

    Returns
    -------
        Wrapped function
    """
    assert callable(func) or func is None  # noqa: S101

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logging_name = ""

            args_passed_in_function = [
                repr(a) for a in args if isinstance(a, (pd.DataFrame, pd.Series)) or a
            ]

            if (
                len(args) == 2
                and args_passed_in_function
                and (
                    "__main__.TerminalController" in args_passed_in_function[0]
                    or (
                        "openbb_terminal." in args_passed_in_function[0]
                        and "_controller" in args_passed_in_function[0]
                    )
                )
            ):
                logging_name = args_passed_in_function[0].split()[0][1:]
                args_passed_in_function = args_passed_in_function[1:]

            logger_used = logging.getLogger(logging_name) if logging_name else log

            logger_used.info(
                "START",
                extra={"func_name_override": func.__name__},
            )

            if get_current_system().DEBUG_MODE:
                value = func(*args, **kwargs)
                log.info("END", extra={"func_name_override": func.__name__})
                return value
            try:
                value = func(*args, **kwargs)
                logger_used.info("END", extra={"func_name_override": func.__name__})
                return value
            except KeyboardInterrupt:
                logger_used.info(
                    "Interrupted by user",
                    extra={"func_name_override": func.__name__},
                )
                return []
            except RequestException as e:
                console.print(
                    "[red]There was an error connecting to the API."
                    " Please try again later.\n[/red]"
                )
                logger_used.exception(
                    "Exception: %s",
                    str(e),
                    extra={"func_name_override": func.__name__},
                )
                return []
            except SSLError as e:
                console.print(
                    "[red]There was an error connecting to the API."
                    " Please check whether your wifi is blocking this site.\n[/red]"
                )
                logger_used.exception(
                    "Exception: %s",
                    str(e),
                    extra={"func_name_override": func.__name__},
                )
                return []
            except Exception as e:
                console.print(f"[red]Error: {e}\n[/red]")
                logger_used.exception(
                    "Exception: %s",
                    str(e),
                    extra={"func_name_override": func.__name__},
                )
                return []

        return wrapper

    return decorator(func) if callable(func) else decorator


# pylint: disable=import-outside-toplevel
def check_api_key(api_keys):
    """
    Wrapper around the view or controller function and
    print message statement to the console if API keys are not yet defined.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            if get_current_user().preferences.ENABLE_CHECK_API:
                current_user = get_current_user()
                undefined_apis = []
                for key in api_keys:
                    # Get value of the API Keys
                    if (
                        getattr(current_user.credentials, key) == "REPLACE_ME"
                    ) and key not in ["API_KEY_ALPHAVANTAGE"]:
                        undefined_apis.append(key)

                if undefined_apis:
                    undefined_apis_name = ", ".join(undefined_apis)
                    console.print(
                        f"[red]{undefined_apis_name} not defined. "
                        "Set the API key under keys menu.[/red]"
                    )  # pragma: allowlist secret
                    return None
            return func(*args, **kwargs)

        return wrapper_decorator

    return decorator


def disable_check_api():
    current_user = get_current_user()
    current_user.preferences.ENABLE_CHECK_API = False
    set_current_user(current_user)
