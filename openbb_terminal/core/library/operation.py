import json
from importlib import import_module
from inspect import signature
from logging import Logger, getLogger
from typing import Any, Callable, Dict, List, Optional

import openbb_terminal.config_terminal as cfg
from openbb_terminal.core.library.metadata import Metadata
from openbb_terminal.core.library.trail_map import TrailMap

# pylint: disable=import-outside-toplevel


class MetadataBuilder:
    def __init__(
        self,
        method: Callable,
        trail: str,
        trail_map: TrailMap,
    ) -> None:
        self.__method = method
        self.__trail = trail
        self.__trail_map = trail_map

    @staticmethod
    def build_docstring(
        method: Callable,
        trail: str,
        trail_map: TrailMap,
    ) -> str:
        doc = ""

        view_trail = f"{trail}_chart"
        if trail_map.get_view_function(view_trail):
            doc += f"Use '{view_trail}' to access the view.\n"

        if method.__doc__:
            doc += method.__doc__

        return doc

    def build(self) -> Metadata:
        method = self.__method
        trail = self.__trail
        trail_map = self.__trail_map

        dir_list: List[str] = []
        docstring = self.build_docstring(
            method=method,
            trail=trail,
            trail_map=trail_map,
        )
        metadata = Metadata(dir_list=dir_list, docstring=docstring)

        return metadata


class Operation:
    @staticmethod
    def __get_method(method_path: str) -> Callable:
        module_path, function_name = method_path.rsplit(".", 1)
        module = import_module(module_path)
        func = getattr(module, function_name)

        return func

    def __init__(
        self,
        trail: str,
        trail_map: Optional[TrailMap] = None,
        metadata: Optional[Metadata] = None,
    ) -> None:
        trail_map = trail_map or TrailMap()

        method_path = trail_map.get_model_or_view(trail=trail)
        method = self.__get_method(method_path=method_path)
        metadata = (
            metadata
            or MetadataBuilder(method=method, trail=trail, trail_map=trail_map).build()
        )

        self._trail = trail
        self._trail_map = trail_map
        self._method = method
        self.__doc__ = metadata.docstring
        self.__signature__ = signature(method)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        method = self._method

        operation_logger = OperationLogger(
            trail=self._trail,
            method_chosen=method,
            args=args,
            kwargs=kwargs,
        )

        operation_logger.log_before_call()

        method_result = method(*args, **kwargs)

        operation_logger.log_after_call(method_result=method_result)

        return method_result

    def about(self):
        import webbrowser

        trail = self._trail
        url = "https://docs.openbb.co/sdk/reference/"
        url += "/".join(trail.split("."))
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
        logging_info["CHART"] = "chart" in kwargs and kwargs["chart"] is True

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
        ----------
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
        ----------
        dict
            Function args with API key removed
        """

        if func_module == "openbb_terminal.keys_model":
            from openbb_terminal.core.log.generation.settings_logger import (  # pylint: disable=import-outside-toplevel
                log_keys,
            )

            # remove key if defined
            function_args.pop("key", None)
            log_keys()
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
        return not cfg.LOGGING_SUPPRESS and not self.__check_last_method()

    def __check_last_method(self) -> bool:
        current_method = {
            f"{self.__method_chosen.__module__}.{self.__method_chosen.__name__}": {
                "args": str(self.__args)[:100],
                "kwargs": str(self.__kwargs)[:100],
            }
        }
        return OperationLogger.last_method == current_method
