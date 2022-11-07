"""OpenBB Terminal SDK Helpers."""
import types
import functools
from typing import (
    Any,
    Callable,
)
import logging
from openbb_terminal.decorators import log_start_end, sdk_arg_logger


def copy_func(
    f: Callable,
    logging_decorator: bool = False,
    chart: bool = False,
) -> Callable:
    """Copy the contents and attributes of the entered function.

    Based on https://stackoverflow.com/a/13503277

    Parameters
    ----------
    f: Callable
        Function to be copied
    logging_decorator: bool
        If True, the copied function will be decorated with the logging decorator
    chart: bool
        If True, the copied function will log info on whether it is a view (chart)

    Returns
    -------
    g: Callable
        New function
    """
    # Removing the logging decorator
    if hasattr(f, "__wrapped__"):
        f = f.__wrapped__  # type: ignore

    g = types.FunctionType(
        f.__code__,
        f.__globals__,  # type: ignore
        name=f.__name__,
        argdefs=f.__defaults__,  # type: ignore
        closure=f.__closure__,  # type: ignore
    )
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__  # type: ignore

    if logging_decorator:
        log_name = logging.getLogger(g.__module__)
        g = sdk_arg_logger(func=g, log=log_name, chart=chart)
        g = log_start_end(func=g, log=log_name)

    return g


def clean_attr_desc(attr: Any) -> str:
    return (
        attr.__doc__.splitlines()[1].lstrip()
        if not attr.__doc__.splitlines()[0]
        else attr.__doc__.splitlines()[0].lstrip()
        if attr.__doc__
        else ""
    )


class Category:
    """The base class that all categories must inherit from."""

    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)

    def __setattr__(self, attr: str, value: Any) -> None:
        """We override setattr to apply logging decorator to Catergory attributes."""
        chart = False
        if "_view" in attr:
            chart = True
        if callable(value) and not attr.startswith("_"):
            value = copy_func(value, logging_decorator=True, chart=chart)
        super().__setattr__(attr, value)

    def __repr__(self):
        """Return the representation of the class."""
        repr_docs = [
            f"    {k}: {clean_attr_desc(v)}\n"
            for k, v in self.__dict__.items()
            if v.__doc__
        ]
        return f"{self.__class__.__name__}(\n{''.join(repr_docs)}\n)"
