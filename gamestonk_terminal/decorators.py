"""Decorators"""
__docformat__ = "numpy"
import functools
import logging
import os
import pandas as pd

from gamestonk_terminal.rich_config import console

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
    assert callable(func) or func is None  # nosec

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            logging_name = ""

            args_passed_in_function = [
                repr(a) for a in args if isinstance(a, (pd.DataFrame, pd.Series)) or a
            ]

            if len(args) == 2 and (
                "__main__.TerminalController" in args_passed_in_function[0]
                or (
                    "gamestonk_terminal." in args_passed_in_function[0]
                    and "_controller" in args_passed_in_function[0]
                )
            ):
                logging_name = args_passed_in_function[0].split()[0][1:]
                args_passed_in_function = args_passed_in_function[1:]

            logger_used = logging.getLogger(logging_name) if logging_name else log

            logger_used.info(
                "START",
                extra={"func_name_override": func.__name__},
            )

            if os.environ.get("DEBUG_MODE") == "true":
                value = func(*args, **kwargs)
                log.info("END", extra={"func_name_override": func.__name__})
                return value
            try:
                value = func(*args, **kwargs)
                logger_used.info("END", extra={"func_name_override": func.__name__})
                return value
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
def check_api_key(source):
    """
    Wrap around the call function in the menu controller and
    print message statement to the console on the status of key and token.

    An extension of the KeysController class
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            # import inside the func due to circular import
            from gamestonk_terminal.keys_controller import KeysController

            key_controller = KeysController(menu_usage=False)

            # construct the check_key method
            method_to_call = "check_" + str(source) + "_key"
            check_single_key = getattr(key_controller, method_to_call)

            check_single_key()

            msg_map = {
                "not defined": "Missing API Keys. Set it in the keys menu or in your .env file",
                "defined, test failed": """API Keys set but returns an error. Check again to make sure it's correct""",
                "defined, test unsuccessful": "API Keys set but returns an error. Check again to make sure it's correct",
            }

            # get the error message from the msg_map
            console_message = msg_map.get(key_controller.key_dict["GLASSNODE"])

            if console_message is not None:
                console.print(console_message)
                console.print("\n")
            else:
                func(*args, **kwargs)

        return wrapper_decorator

    return decorator
