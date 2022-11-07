from importlib import import_module
from logging import getLogger, Logger
from typing import Any, Callable, List, Optional
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
        map_list = trail_map.map_list

        if trail in map_list:
            if "model" in map_list[trail] and map_list[trail]["model"]:
                model_path = map_list[trail]["model"]
                model = cls.__get_method(method_path=model_path)
            else:
                model = None
        return model

    @classmethod
    def __get_view(cls, trail: str, trail_map: TrailMap) -> Optional[Callable]:
        map_list = trail_map.map_list

        if trail in map_list:
            if "view" in map_list[trail] and map_list[trail]["view"]:
                view_path = map_list[trail]["view"]
                view = cls.__get_method(method_path=view_path)
            else:
                view = None

        return view

    @staticmethod
    def is_valid(trail: str, trail_map: TrailMap) -> bool:
        return trail in trail_map.map_list

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

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        model = self.__model
        view = self.__view

        if view and "chart" in kwargs and kwargs["chart"] is True:
            method_chosen = view
        elif model:
            method_chosen = model
        else:
            raise Exception("Unknown method")

        OperationLogger.log_before_call(
            operation=self,
            method_chosen=method_chosen,
        )

        if "chart" in kwargs:
            kwargs.pop("chart")
        method_result = method_chosen(*args, **kwargs)

        OperationLogger.log_after_call(
            operation=self,
            method_chosen=method_chosen,
            method_result=method_result,
        )

        return method_result


class OperationLogger:
    __logger = getLogger(__name__)

    @staticmethod
    def log_start(logger: Logger, method_chosen: Callable):
        logger.info(
            "START",
            extra={"func_name_override": method_chosen.__name__},
        )

    @staticmethod
    def log_end(logger: Logger, method_chosen: Callable):
        logger.info(
            "END",
            extra={"func_name_override": method_chosen.__name__},
        )

    @classmethod
    def log_before_call(
        cls,
        operation: Operation,
        method_chosen: Callable,
    ):
        logger = cls.__logger
        cls.log_start(logger, method_chosen=method_chosen)

    @classmethod
    def log_after_call(
        cls,
        operation: Operation,
        method_chosen: Callable,
        method_result: Any,
    ):
        logger = cls.__logger
        cls.log_end(logger, method_chosen=method_chosen)
