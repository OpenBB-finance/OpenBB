import inspect
from pathlib import Path
from types import FunctionType
from typing import Any, Callable, Dict, ForwardRef, List, Optional

import pandas as pd

import openbb_terminal.core.sdk.sdk_init as lib
from openbb_terminal.core.config.paths import (
    MAP_FORECASTING_PATH,
    MAP_OPTIMIZATION_PATH,
    MAP_PATH,
)
from openbb_terminal.core.sdk.sdk_helpers import clean_attr_desc
from openbb_terminal.rich_config import console


def get_signature_parameters(
    function: Callable[..., Any], globalns: Dict[str, Any]
) -> Dict[str, inspect.Parameter]:
    signature = inspect.signature(function)

    params = {}

    cache: dict[str, Any] = {}

    for name, parameter in signature.parameters.items():
        annotation = parameter.annotation

        if annotation is parameter.empty:
            params[name] = parameter

            continue

        if annotation is None:
            params[name] = parameter.replace(annotation=type(None))

            continue

        if isinstance(annotation, ForwardRef):
            annotation = annotation.__forward_arg__

        if isinstance(annotation, str):
            annotation = eval(annotation, globalns, cache)  # pylint: disable=W0123

        params[name] = parameter.replace(annotation=annotation)

    return params


class FuncAttr:
    def __init__(self) -> None:
        self.short_doc: Optional[str] = None

        self.long_doc: Optional[str] = None

        self.func_def: Optional[str] = None

        self.path: Optional[str] = None

        self.lineon: Optional[int] = None

        self.full_path: Optional[str] = None

        self.func_unwrapped: Optional[FunctionType] = None

        self.func_wrapped: Optional[FunctionType] = None

        self.params: Dict[str, inspect.Parameter] = {}

    def get_func_attrs(self, func: str) -> None:
        module_path, function_name = func.rsplit(".", 1)

        func_attr = getattr(getattr(lib, module_path), function_name)

        self.func_wrapped = func_attr

        add_lineon = 0

        if hasattr(func_attr, "__wrapped__"):
            while hasattr(func_attr, "__wrapped__"):
                func_attr = func_attr.__wrapped__

                add_lineon += 1

        self.func_unwrapped = func_attr

        self.lineon = inspect.getsourcelines(func_attr)[1] + add_lineon

        self.long_doc = func_attr.__doc__

        self.short_doc = clean_attr_desc(func_attr)

        for k, p in get_signature_parameters(func_attr, func_attr.__globals__).items():
            self.params[k] = p

        self.path = inspect.getfile(func_attr)

        full_path = (
            inspect.getfile(func_attr).replace("\\", "/").split("openbb_terminal/")[1]
        )

        self.full_path = f"openbb_terminal/{full_path}"

    def get_definition(
        self, location_path: list, class_attr: str, view: bool = False
    ) -> str:
        """Creates the function definition to be used in SDK docs."""

        funcspec = self.params

        definition = ""

        for arg, param in funcspec.items():
            annotation = (
                (
                    str(param.annotation)
                    .replace("<class '", "")
                    .replace("'>", "")
                    .replace("typing.", "")
                    .replace("pandas.core.frame.", "pd.")
                    .replace("pandas.core.series.", "pd.")
                    .replace("openbb_terminal.portfolio.", "")
                )
                if param.annotation != inspect.Parameter.empty
                else "Any"
            )

            default = ""

            if param.default is not param.empty:
                arg_default = (
                    param.default
                    if param.default is not inspect.Parameter.empty
                    else "None"
                )

                default = (
                    f" = {arg_default}"
                    if not isinstance(arg_default, str)
                    else f' = "{arg_default}"'
                )

            definition += f"{arg}: {annotation}{default}, "

        definition = definition.rstrip(", ")

        trail = ".".join([t for t in location_path if t != ""])

        sdk_name = class_attr if not view else f"{class_attr}_chart"

        trail = trail.replace("root.", "")

        sdk_path = f"{f'openbb.{trail}' if trail else 'openbb'}.{sdk_name}"

        return f"{sdk_path}({definition })"


# pylint: disable=R0903


class Trailmap:
    def __init__(self, trailmap: str, model: str, view: Optional[str] = None):
        self.trailmap: str = trailmap

        tmap = trailmap.split(".")

        if len(tmap) == 1:
            tmap = ["root", tmap[0]]

        self.class_attr: str = tmap.pop(-1)

        self.location_path = tmap

        self.model = model

        self.view = view if view else None

        self.view_name = "_chart"

        self.model_func: Optional[str] = f"lib.{model}" if model else None

        self.view_func: Optional[str] = f"lib.{view}" if view else None

        self.func_attrs: Dict[str, FuncAttr] = {}

        self.func_attrs["model"] = FuncAttr()

        self.func_attrs["view"] = FuncAttr()

        for k, cls in self.func_attrs.items():
            if getattr(self, f"{k}_func"):
                cls.get_func_attrs(getattr(self, f"{k}"))

                cls.func_def = cls.get_definition(
                    tmap, self.class_attr, view=k == "view"
                )


def get_trailmaps(sort: bool = False) -> List[Trailmap]:
    trailmaps = []

    def load_csv(path: Optional[Path] = None) -> Dict[str, Dict[str, str]]:
        path = path or MAP_PATH

        df = pd.read_csv(path, keep_default_na=False)

        df = df.set_index("trail")

        if sort:
            df = df.sort_index()

            df.to_csv(path, index=True)

        return df.to_dict(orient="index")

    def print_error(error: str) -> None:
        console.print(
            f"[bold red]{error} is disabled and will not be included in the SDK.[/bold red]"
        )

        console.print(
            "[bold red]`poetry install -E all` to install all toolkits.[/bold red]"
        )

    def load():
        map_dict = load_csv(path=MAP_PATH)

        if lib.FORECASTING_TOOLKIT_ENABLED:
            map_forecasting_dict = load_csv(path=MAP_FORECASTING_PATH)

            map_dict.update(map_forecasting_dict)

        else:
            print_error("Forecasting")

        if lib.OPTIMIZATION_TOOLKIT_ENABLED:
            map_optimization_dict = load_csv(path=MAP_OPTIMIZATION_PATH)

            map_dict.update(map_optimization_dict)

        else:
            print_error("Optimization")

        map_dict = dict(sorted(map_dict.items(), key=lambda item: item[0]))

        return map_dict

    map_dict = load()

    for trail, attrs in map_dict.items():
        model, view = attrs["model"], attrs["view"]

        trail_map = Trailmap(trail, model, view)

        trailmaps.append(trail_map)

    return trailmaps
