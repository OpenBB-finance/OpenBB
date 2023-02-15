import importlib
import inspect
from pathlib import Path
from types import FunctionType
from typing import Dict, List, Optional

import pandas as pd

from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.rich_config import console
from openbb_terminal.sdk_core.sdk_helpers import clean_attr_desc
from openbb_terminal.sdk_core.sdk_init import (
    FORECASTING_TOOLKIT_ENABLED,
    OPTIMIZATION_TOOLKIT_ENABLED,
)


class FuncAttr:
    def __init__(self, func: Optional[str] = None):
        self.short_doc: Optional[str] = None
        self.long_doc: Optional[str] = None
        self.func_def: Optional[str] = None
        self.path: Optional[str] = None
        self.lineon: Optional[int] = None
        self.full_path: Optional[str] = None
        self.func_unwrapped: Optional[FunctionType] = None
        self.func_wrapped: Optional[FunctionType] = None
        if func:
            self.get_func_attrs(func)

    def get_func_attrs(self, func: str) -> None:
        attr = getattr(
            importlib.import_module("openbb_terminal.sdk_core.sdk_init"),
            func.split(".")[0],
        )
        func_attr = getattr(attr, func.split(".")[1])
        self.func_wrapped = func_attr

        add_lineon = 0
        if hasattr(func_attr, "__wrapped__"):
            while hasattr(func_attr, "__wrapped__"):
                func_attr = func_attr.__wrapped__
                add_lineon += 1

        self.func_unwrapped = func_attr
        self.lineon = inspect.getsourcelines(func_attr)[1] + add_lineon

        self.func_def = self.get_definition()
        self.long_doc = func_attr.__doc__
        self.short_doc = clean_attr_desc(func_attr)

        self.path = inspect.getfile(func_attr)
        full_path = (
            inspect.getfile(func_attr).replace("\\", "/").split("openbb_terminal/")[1]
        )
        self.full_path = f"openbb_terminal/{full_path}"

    def get_definition(self) -> str:
        """Creates the function definition to be used in SDK docs."""
        funcspec = inspect.getfullargspec(self.func_unwrapped)

        definition = ""
        added_comma = False
        for arg in funcspec.args:
            annotation = (
                funcspec.annotations[arg] if arg in funcspec.annotations else "Any"
            )
            annotation = (
                str(annotation)
                .replace("<class '", "")
                .replace("'>", "")
                .replace("typing.", "")
                .replace("pandas.core.frame.", "pd.")
                .replace("pandas.core.series.", "pd.")
                .replace("openbb_terminal.portfolio.", "")
            )
            definition += f"{arg}: {annotation}, "
            added_comma = True

        if added_comma:
            definition = definition[:-2]

        return_def = (
            funcspec.annotations["return"].__name__
            if "return" in funcspec.annotations
            and hasattr(funcspec.annotations["return"], "__name__")
            and funcspec.annotations["return"] is not None
            else "None"
        )
        definition = f"def {self.func_unwrapped.__name__}({definition }) -> {return_def}"  # type: ignore
        return definition


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
        self.func_attrs["model"] = FuncAttr(self.model)
        self.func_attrs["view"] = FuncAttr(self.view)  # type: ignore


def get_trailmaps(sort: bool = False) -> List[Trailmap]:
    trailmaps = []

    MAP_PATH = PACKAGE_DIRECTORY / "sdk_core" / "trail_map.csv"
    MAP_FORECASTING_PATH = PACKAGE_DIRECTORY / "sdk_core" / "trail_map_forecasting.csv"
    MAP_OPTIMIZATION_PATH = (
        PACKAGE_DIRECTORY / "sdk_core" / "trail_map_optimization.csv"
    )

    def load_csv(path: Path = None) -> pd.DataFrame:
        path = path or MAP_PATH
        df = pd.read_csv(path, keep_default_na=False)
        df = df.set_index("trail")
        if sort:
            df = df.sort_index()
            df.to_csv(path, index=True)

        return df.to_dict(orient="index")

    def load():
        map_dict = load_csv(path=MAP_PATH)
        if FORECASTING_TOOLKIT_ENABLED:
            map_forecasting_dict = load_csv(path=MAP_FORECASTING_PATH)
            map_dict.update(map_forecasting_dict)

        if OPTIMIZATION_TOOLKIT_ENABLED:
            map_optimization_dict = load_csv(path=MAP_OPTIMIZATION_PATH)
            map_dict.update(map_optimization_dict)

        map_dict = dict(sorted(map_dict.items(), key=lambda item: item[0]))

        return map_dict

    map_dict = load()

    for trail, attrs in map_dict.items():
        model, view = attrs["model"], attrs["view"]
        if not FORECASTING_TOOLKIT_ENABLED and "forecast" in trail:
            console.print(
                f"[bold red]Forecasting is disabled. {trail} will not be included in the SDK.[/bold red]"
            )
            continue
        if not OPTIMIZATION_TOOLKIT_ENABLED and "portfolio.po" in trail:
            console.print(
                f"[bold red]Optimization is disabled. {trail} will not be included in the SDK.[/bold red]"
            )
            continue
        trail_map = Trailmap(trail, model, view)
        trailmaps.append(trail_map)

    return trailmaps
