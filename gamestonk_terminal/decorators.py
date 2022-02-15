"""Decorators"""
__docformat__ = "numpy"
import functools
import logging
import os

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

            kwargs_passed_in_function = list()
            args_passed_in_function = [repr(a) for a in args]
            # view files have parameters that are usually small given they are input by the user
            if "_view" in log.name:
                kwargs_passed_in_function = [f"{k}={v!r}" for k, v in kwargs.items()]
            # we are only interested in the other_args from controller methods
            elif "_controller" in log.name:
                # check len of args is 2 because of (self, other_args: List[str])
                if len(args) == 2:
                    args_passed_in_function = (
                        args[1] if isinstance(args[1], list) else [args[1]]
                    )
            # other files can have as parameters big variables, therefore adds logic to only add small ones
            else:
                for k, v in kwargs.items():
                    if type(v) in (int, float):
                        kwargs_passed_in_function.append(f"{k}={v!r}")
                    elif k == "export":
                        kwargs_passed_in_function.append(f"{k}={v!r}")
                    else:
                        kwargs_passed_in_function.append(f"{k}={type(v)!r}")

            if args_passed_in_function or kwargs_passed_in_function:
                formatted_arguments = ", ".join(
                    args_passed_in_function + kwargs_passed_in_function
                )
                log.info(
                    f"START params: {formatted_arguments}",
                    extra={"func_name_override": func.__name__},
                )
            else:
                log.info("START", extra={"func_name_override": func.__name__})

            if os.environ.get("DEBUG_MODE") == "true":
                value = func(*args, **kwargs)
                log.info("END", extra={"func_name_override": func.__name__})
                return value
            try:
                value = func(*args, **kwargs)
                log.info("END", extra={"func_name_override": func.__name__})
                return value
            except Exception as e:
                console.print(f"[red]Error: {e}\n[/red]")
                log.exception("Exception", extra={"func_name_override": func.__name__})
                return []

        return wrapper

    return decorator(func) if callable(func) else decorator
