import json
from importlib import import_module
from logging import getLogger, Logger
from typing import Any, Callable, Dict, List, Optional

from inspect import signature

import openbb_terminal.config_terminal as cfg

from openbb_terminal.core.library.metadata import Metadata
from openbb_terminal.core.library.trail_map import TrailMap


class MetadataBuilder:
    def __init__(self, model: Optional[Callable], view: Optional[Callable]) -> None:
        self.__model = model
        self.__view = view

    @staticmethod
    def build_doc_string(
        model: Optional[Callable],
        view: Optional[Callable],
    ) -> str:
        if view is not None:
            view_doc = view.__doc__ or ""
            model_doc = model.__doc__ or ""
            index = view_doc.find("Parameters")

            all_parameters = (
                "\nSDK function, use the chart kwarg for getting the view model and it's plot. "
                "See every parameter below:\n\n    "
                + view_doc[index:]
                + """chart: bool
        If the view and its chart shall be used"""
            )
            doc_string = (
                all_parameters
                + "\n\nModel doc:\n"
                + model_doc
                + "\n\nView doc:\n"
                + view_doc
            )
        else:
            doc_string = model.__doc__ or ""

        return doc_string

    def build(self) -> Metadata:
        model = self.__model
        view = self.__view

        dir_list: List[str] = []
        docstring = self.build_doc_string(model=model, view=view)
        metadata = Metadata(dir_list=dir_list, doc_string=docstring)

        return metadata


class Operation:
    @staticmethod
    def __get_method(method_path: str) -> Callable:
        module_path, function_name = method_path.rsplit(".", 1)
        module = import_module(module_path)
        method = getattr(module, function_name)

        return method

    @classmethod
    def __get_model(cls, trail: str, trail_map: TrailMap) -> Optional[Callable]:
        map_dict = trail_map.map_dict
        model = None

        if trail in map_dict:
            if "model" in map_dict[trail] and map_dict[trail]["model"]:
                model_path = map_dict[trail]["model"]
                model = cls.__get_method(method_path=model_path)

        return model

    @classmethod
    def __get_view(cls, trail: str, trail_map: TrailMap) -> Optional[Callable]:
        map_dict = trail_map.map_dict
        view = None

        if trail in map_dict:
            if "view" in map_dict[trail] and map_dict[trail]["view"]:
                view_path = map_dict[trail]["view"]
                view = cls.__get_method(method_path=view_path)

        return view

    @staticmethod
    def is_valid(trail: str, trail_map: TrailMap) -> bool:
        return trail in trail_map.map_dict

    @property
    def trail(self) -> str:
        return self.__trail

    @property
    def trail_map(self) -> TrailMap:
        return self.__trail_map

    @property
    def model(self) -> Optional[Callable]:
        return self.__model

    @property
    def view(self) -> Optional[Callable]:
        return self.__view

    def __init__(
        self,
        trail: str,
        trail_map: Optional[TrailMap] = None,
        metadata: Optional[Metadata] = None,
    ) -> None:
        trail_map = trail_map or TrailMap()
        model = self.__get_model(trail=trail, trail_map=trail_map)
        view = self.__get_view(trail=trail, trail_map=trail_map)
        metadata = metadata or MetadataBuilder(model=model, view=view).build()

        self.__trail = trail
        self.__trail_map = trail_map
        self.__model = model
        self.__view = view

        self.__doc__ = metadata.doc_string

        if model:
            self.__signature__ = signature(model)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        model = self.__model
        view = self.__view

        if view and "chart" in kwargs and kwargs["chart"] is True:
            method_chosen = view
        elif model:
            method_chosen = model
        else:
            raise Exception("Unknown method")

        operation_logger = OperationLogger(
            trail=self.__trail,
            method_chosen=method_chosen,
            args=args,
            kwargs=kwargs,
        )

        operation_logger.log_before_call()

        if "chart" in kwargs:
            kwargs.pop("chart")
        method_result = method_chosen(*args, **kwargs)

        operation_logger.log_after_call(method_result=method_result)

        return method_result


class OperationLogger:
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
        if not cfg.LOGGING_SUPPRESS:
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

    @classmethod
    def __log_method_info(
        cls,
        logger: Logger,
        trail: str,
        method_chosen: Callable,
        args: Any,
        kwargs: Any,
    ):
        merged_args = cls.__merge_function_args(method_chosen, args, kwargs)
        merged_args = cls.__remove_key_and_log_state(
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

            from openbb_terminal.core.log.generation.settings_logger import (  # pylint: disable=C0415
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
        if not cfg.LOGGING_SUPPRESS:
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
