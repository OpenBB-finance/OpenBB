"""OpenBB Terminal SDK Helpers."""
from traceback import format_stack
import types
import functools
from typing import (
    Any,
    Callable,
    Optional,
)
import logging
from openbb_terminal.decorators import log_start_end, sdk_arg_logger


def check_suppress_logging(suppress_dict: dict) -> bool:
    """
    Check if logging should be suppressed.
    If the dict contains a value that is found in the stack trace,
    the logging should be suppressed.

    Parameters
    ----------
    supress_dict: dict
        Dictionary with values that trigger log suppression

    Returns
    -------
    bool
        True if logging shall be suppressed, False otherwise
    """
    for _, value in suppress_dict.items():
        for ele in format_stack():
            if value in ele:
                return True
    return False


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


def clean_attr_desc(attr: Optional[Any] = None) -> Optional[str]:
    """Clean the attribute description."""
    if attr.__doc__ is None:
        return None
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


def get_sdk_imports_text() -> str:
    """Return the text for the SDK imports."""
    sdk_imports = """\"\"\"OpenBB Terminal SDK.\"\"\"
# flake8: noqa
# pylint: disable=unused-import,wrong-import-order
# pylint: disable=C0302,W0611,R0902,R0903,C0412,C0301,not-callable
import logging

import openbb_terminal.config_terminal as cfg
from openbb_terminal import helper_funcs as helper  # noqa: F401
from openbb_terminal.config_terminal import theme

from openbb_terminal.core.log.generation.settings_logger import log_all_settings
from openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model import Coin
from openbb_terminal.dashboards.dashboards_controller import DashboardsController
from openbb_terminal.helper_classes import TerminalStyle  # noqa: F401
from openbb_terminal.loggers import setup_logging
from openbb_terminal.portfolio.portfolio_model import PortfolioModel as Portfolio
from openbb_terminal.reports import widget_helpers as widgets  # noqa: F401
from openbb_terminal.reports.reports_controller import ReportController

from openbb_terminal.sdk_core.sdk_helpers import check_suppress_logging
from openbb_terminal.sdk_core import (
    controllers as ctrl,
    models as model,
)

logger = logging.getLogger(__name__)
theme.applyMPLstyle()

SUPPRESS_LOGGING_CLASSES = {
    ReportController: "ReportController",
    DashboardsController: "DashboardsController",
}\r\r\r
"""
    return "\r".join(sdk_imports.splitlines())
