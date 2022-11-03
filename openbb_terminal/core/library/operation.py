from importlib import import_module
from typing import Any, Callable, Optional
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
        if view.__doc__ is not None:
            index = view.__doc__.find("Parameters")
            all_parameters = (
                "\nSDK function, use the chart kwarg for getting the view model and it's plot. "
                "See every parameter below:\n\n    "
                + view.__doc__[index:]
                + """chart: bool
        If the view and its chart shall be used"""
            )
            doc_string = (
                all_parameters
                + "\n\nModel doc:\n"
                + model.__doc__
                + "\n\nView doc:\n"
                + view.__doc__
            )
        else:
            doc_string = model.__doc__

        return doc_string

    def build(self) -> Metadata:
        model = self.__model
        view = self.__view

        dir_list = []
        docstring = self.build_doc_string(model=model, view=view)
        metadata = Metadata(dir_list=dir_list, doc_string=docstring)

        return metadata

class Operation:
    def __init__(
        self,
        model: Optional[Callable],
        view: Optional[Callable],
        metadata: Optional[Metadata] = None,
    ) -> None:
        metadata = metadata or MetadataBuilder(model=model, view=view).build()

        self.__model = model
        self.__view = view

        self.__doc__ = metadata.doc_string

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        model = self.__model
        view = self.__view

        if (
            view
            and "chart" in kwargs
            and kwargs["chart"] is True
        ):
            method = view
        elif model:
            method = model
        else:
            raise Exception("Unknown action")

        return method(*args, **kwargs)

class OperationBuilder:
    @staticmethod
    def get_method(method_path: str) -> Callable:
        module_path, function_name = method_path.rsplit(".", 1)
        module = import_module(module_path)
        method = getattr(module, function_name)

        return method

    def __init__(
        self,
        trail_map: TrailMap = None,
    ) -> None:
        self.__trail_map = trail_map or TrailMap()

    def build(self, trail: str) -> Optional[Operation]:
        trail_map = self.__trail_map.map_list

        if trail in trail_map:
            if "model" in trail_map[trail] and trail_map[trail]["model"]:
                model_path = trail_map[trail]["model"]
                model = self.get_method(method_path=model_path)
            else:
                model = None

            if "view" in trail_map[trail] and trail_map[trail]["view"]:
                view_path = trail_map[trail]["view"]
                view = self.get_method(method_path=view_path)
            else:
                view = None

            operation = Operation(
                model=model,
                view=view,
            )
        else:
            operation = None

        return operation
