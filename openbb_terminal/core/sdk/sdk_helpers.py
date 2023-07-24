"""OpenBB Terminal SDK Helpers."""


import json
from inspect import signature
from logging import Logger, getLogger
from typing import Any, Callable, Dict, Optional

from openbb_terminal.core.config.paths import SETTINGS_ENV_FILE
from openbb_terminal.core.sdk.sdk_init import (
    FORECASTING_TOOLKIT_ENABLED,
    FORECASTING_TOOLKIT_WARNING,
    OPTIMIZATION_TOOLKIT_ENABLED,
    OPTIMIZATION_TOOLKIT_WARNING,
)
from openbb_terminal.core.session.current_system import (
    get_current_system,
    set_system_variable,
)
from openbb_terminal.rich_config import console

SETTINGS_ENV_FILE.parent.mkdir(parents=True, exist_ok=True)


if (
    not FORECASTING_TOOLKIT_ENABLED
    and not get_current_system().DISABLE_FORECASTING_WARNING
):
    set_system_variable("DISABLE_FORECASTING_WARNING", True)

    console.print(FORECASTING_TOOLKIT_WARNING)


if (
    not OPTIMIZATION_TOOLKIT_ENABLED
    and not get_current_system().DISABLE_OPTIMIZATION_WARNING
):
    set_system_variable("DISABLE_OPTIMIZATION_WARNING", True)

    console.print(OPTIMIZATION_TOOLKIT_WARNING)


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


def class_repr(cls_dict: Dict[str, Any]) -> list:
    """Return the representation of the class."""

    return [
        f"    {k}: {clean_attr_desc(v)}\n"
        for k, v in cls_dict.items()
        if v.__doc__ and not k.startswith("_")
    ]


class Operation:
    def __init__(self, name: str, trail: str, func: Callable) -> None:
        self._trail = trail

        self._method = func

        self._name = name

        for attr in [
            "__doc__",
            "__name__",
            "__annotations__",
            "__defaults__",
            "__kwdefaults__",
            "__module__",
        ]:
            setattr(self.__class__, attr, getattr(func, attr))

            setattr(self, attr, getattr(func, attr))

        self.__signature__ = signature(func)

        self.__class__.__signature__ = signature(func)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        method = self._method

        # We make a copy of the kwargs to avoid modifying the original

        log_kwargs = kwargs.copy()

        log_kwargs["chart"] = "chart" in self._name

        operation_logger = OperationLogger(
            trail=self._trail, method_chosen=method, args=args, kwargs=log_kwargs
        )

        operation_logger.log_before_call()

        method_result = method(*args, **kwargs)

        operation_logger.log_after_call(method_result=method_result)

        return method_result

    def about(self):
        # pylint: disable=C0415

        import webbrowser

        trail = "/".join(self._trail.split(".")).replace("_chart", "")

        url = f"https://docs.openbb.co/sdk/reference/{trail}"

        webbrowser.open(url)


class Category:

    """The base class that all categories must inherit from."""

    _location_path: str = ""

    def __init__(self, *args, **kwargs):
        """Initialize the class"""

        super().__init__(*args, **kwargs)

    def __repr__(self):
        """Return the representation of the class."""

        repr_docs = []

        if submodules := class_repr(self.__class__.__dict__):
            repr_docs += ["\nSubmodules:\n"] + submodules

        if attributes := class_repr(self.__dict__):
            repr_docs += ["\nAttributes:\n"] + attributes

        return f"{self.__class__.__name__}(\n{''.join(repr_docs)}\n)"

    def __getattribute__(self, name: str):
        """We override the __getattribute__ method and wrap all callable



        attributes with a wrapper that logs the call and the result.



        """

        attr = super().__getattribute__(name)

        if isinstance(attr, Operation) or name.startswith("__"):
            return attr

        trail = f"{self.__class__._location_path}.{name}"

        if callable(attr) and not isinstance(attr, Operation):
            # We set the attribute to the wrapped function so that we don't

            # have to wrap it when called again.

            setattr(self, name, Operation(name=name, trail=trail, func=attr))

            return getattr(self, name)

        return attr

    def about(self):
        # pylint: disable=C0415

        import webbrowser

        trail = "/".join(self._location_path.split("."))

        url = f"https://docs.openbb.co/sdk/reference/{trail}"

        webbrowser.open(url)


class OperationLogger:
    last_method: Dict[Any, Any] = {}

    def __init__(
        self,
        trail: str,
        method_chosen: Callable,
        args: Any,
        kwargs: Any,
        logger: Optional[Logger] = None,
    ) -> None:
        self.__trail = trail

        self.__method_chosen = method_chosen

        self.__logger = logger or getLogger(self.__method_chosen.__module__)

        self.__args = args

        self.__kwargs = kwargs

    def log_before_call(
        self,
    ):
        if self.__check_logging_conditions():
            logger = self.__logger

            self.__log_start(logger=logger, method_chosen=self.__method_chosen)

            self.__log_method_info(
                logger=logger,
                trail=self.__trail,
                method_chosen=self.__method_chosen,
                args=self.__args,
                kwargs=self.__kwargs,
            )

    @staticmethod
    def __log_start(logger: Logger, method_chosen: Callable):
        logger.info(
            "START",
            extra={"func_name_override": method_chosen.__name__},
        )

    def __log_method_info(
        self,
        logger: Logger,
        trail: str,
        method_chosen: Callable,
        args: Any,
        kwargs: Any,
    ):
        merged_args = self.__merge_function_args(method_chosen, args, kwargs)

        merged_args = self.__remove_key_and_log_state(
            method_chosen.__module__, merged_args
        )

        logging_info: Dict[str, Any] = {}

        logging_info["INPUT"] = {
            key: str(value)[:100] for key, value in merged_args.items()
        }

        logging_info["VIRTUAL_PATH"] = trail

        logging_info["CHART"] = kwargs.get("chart", False)

        logger.info(
            f"{json.dumps(logging_info)}",
            extra={"func_name_override": method_chosen.__name__},
        )

    @staticmethod
    def __merge_function_args(func: Callable, args: tuple, kwargs: dict) -> dict:
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

        import inspect  # pylint: disable=C0415

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

    @staticmethod
    def __remove_key_and_log_state(func_module: str, function_args: dict) -> dict:
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
            # pylint: disable=C0415

            # from openbb_terminal.core.log.generation.settings_logger import (

            #     log_credentials,

            # )

            # remove key if defined

            function_args.pop("key", None)

            # log_credentials()

        return function_args

    def log_after_call(
        self,
        method_result: Any,
    ):
        if self.__check_logging_conditions():
            logger = self.__logger

            self.__log_exception_if_any(
                logger=logger,
                method_result=method_result,
                method_chosen=self.__method_chosen,
            )

            self.__log_end(
                logger=logger,
                method_chosen=self.__method_chosen,
            )

            OperationLogger.last_method = {
                f"{self.__method_chosen.__module__}.{self.__method_chosen.__name__}": {
                    "args": str(self.__args)[:100],
                    "kwargs": str(self.__kwargs)[:100],
                }
            }

    @staticmethod
    def __log_exception_if_any(
        logger: Logger,
        method_chosen: Callable,
        method_result: Any,
    ):
        if isinstance(method_result, Exception):
            logger.exception(
                f"Exception: {method_result}",
                extra={"func_name_override": method_chosen.__name__},
            )

    @staticmethod
    def __log_end(logger: Logger, method_chosen: Callable):
        logger.info(
            "END",
            extra={"func_name_override": method_chosen.__name__},
        )

    def __check_logging_conditions(self) -> bool:
        return (
            not get_current_system().LOGGING_SUPPRESS and not self.__check_last_method()
        )

    def __check_last_method(self) -> bool:
        current_method = {
            f"{self.__method_chosen.__module__}.{self.__method_chosen.__name__}": {
                "args": str(self.__args)[:100],
                "kwargs": str(self.__kwargs)[:100],
            }
        }

        return OperationLogger.last_method == current_method


def get_sdk_imports_text() -> str:
    """Return the text for the SDK imports."""

    sdk_imports = """\"\"\"OpenBB Terminal SDK.\"\"\"







# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #







# flake8: noqa







# pylint: disable=unused-import,wrong-import-order







# pylint: disable=C0302,W0611,R0902,R0903,C0412,C0301,not-callable







import logging







import openbb_terminal.config_terminal as cfg







from openbb_terminal import helper_funcs as helper  # noqa: F401







from openbb_terminal.core.plots.plotly_helper import theme  # noqa: F401







from openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model import Coin







from openbb_terminal.dashboards.dashboards_controller import DashboardsController







from openbb_terminal.helper_classes import TerminalStyle  # noqa: F401







from openbb_terminal.reports import widget_helpers as widgets  # noqa: F401







from openbb_terminal.reports.reports_controller import ReportController







import openbb_terminal.core.sdk.sdk_init as lib







from openbb_terminal.core.sdk import (



    controllers as ctrl,







    models as model,



)







from openbb_terminal.core.session.current_system import get_current_system







from openbb_terminal.core.session.current_user import is_local







from openbb_terminal.terminal_helper import is_auth_enabled







cfg.setup_config_terminal(is_sdk=True)







logger = logging.getLogger(__name__)







cfg.theme.applyMPLstyle()







\r\r\r







"""

    return "\r".join(sdk_imports.splitlines())
