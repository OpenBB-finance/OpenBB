"""Decorators"""
__docformat__ = "numpy"
import functools
import logging
import os
import json
import inspect
from typing import Callable
import pandas as pd

from openbb_terminal import feature_flags as obbff
from openbb_terminal.rich_config import console  # pragma: allowlist secret
from openbb_terminal.core.log.generation.settings_logger import log_keys

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
def check_api_key(api_keys):
    """
    Wrapper around the view or controller function and
    print message statement to the console if API keys are not yet defined.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            if obbff.ENABLE_CHECK_API:
                import openbb_terminal.config_terminal as cfg

                undefined_apis = []
                for key in api_keys:
                    # Get value of the API Keys
                    if getattr(cfg, key) == "REPLACE_ME" and key not in [
                        "API_KEY_ALPHAVANTAGE"
                    ]:
                        undefined_apis.append(key)

                if undefined_apis:
                    undefined_apis_name = ", ".join(undefined_apis)
                    console.print(
                        f"[red]{undefined_apis_name} not defined. "
                        "Set API Keys in ~/.openbb_terminal/.env or under keys menu.[/red]\n"
                    )  # pragma: allowlist secret
                    return None
            return func(*args, **kwargs)

        return wrapper_decorator

    return decorator


def disable_check_api():
    obbff.ENABLE_CHECK_API = False


def sdk_arg_logger(func=None, log=None, virtual_path: str = "", chart: bool = False):
    """
    Wrap function to add the function args to the log entry when using the SDK.
    """

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        try:
            value = func(*args, **kwargs)

            merged_args = merge_function_args(func, args, kwargs)
            merged_args = sdk_remove_key_and_log_state(func.__module__, merged_args)

            logging_info = {}
            logging_info["INPUT"] = {
                key: str(value) for key, value in merged_args.items()
            }
            logging_info["VIRTUAL_PATH"] = virtual_path
            logging_info["CHART"] = chart

            log.info(
                f"{json.dumps(logging_info)}",
                extra={"func_name_override": func.__name__},
            )
            return value

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            log.exception(
                "Exception: %s",
                str(e),
                extra={"func_name_override": func.__name__},
            )
            raise

    return wrapper_decorator


def merge_function_args(func: Callable, args: tuple, kwargs: dict) -> dict:
    """
    Merge user input args and kwargs with signature defaults into a dictionary.

    Parameters
    ----------

    func : Callable
        Function to get the args from
    args : tuple
        Positional args
    kwargs : dict
        Keyword args

    Returns
    -------
    dict
        Merged user args and signature defaults
    """

    sig = inspect.signature(func)
    sig_args = {
        param.name: param.default
        for param in sig.parameters.values()
        if param.default is not inspect.Parameter.empty
    }
    # merge args with sig_args
    sig_args.update(dict(zip(sig.parameters, args)))
    # add kwargs elements to sig_args
    sig_args.update(kwargs)
    return sig_args


def sdk_remove_key_and_log_state(func_module: str, function_args: dict) -> dict:
    """
    Remove API key from the function args and log state of keys.

    Parameters
    ----------
    func_module : str
        Module of the function
    function_args : dict
        Function args

    Returns
    -------
    dict
        Function args with API key removed
    """

    if func_module == "openbb_terminal.keys_model":
        # remove key if defined
        function_args.pop("key", None)
        log_keys()
    return function_args
