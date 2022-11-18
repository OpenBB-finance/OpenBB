from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY

try:
    import darts  # pylint: disable=W0611 # noqa: F401

    from darts import utils  # pylint: disable=W0611 # noqa: F401

    FORECASTING = True
except ImportError:
    FORECASTING = False


class TrailMap:
    MAP_PATH = MISCELLANEOUS_DIRECTORY / "library" / "trail_map.csv"
    MAP_FORECASTING_PATH = (
        MISCELLANEOUS_DIRECTORY / "library" / "trail_map_forecasting.csv"
    )

    @classmethod
    def load_csv(cls, path: Path = None) -> Dict[str, Dict[str, str]]:
        path = path or cls.MAP_PATH
        df = pd.read_csv(path, keep_default_na=False)
        df.set_index("trail", inplace=True)
        return df.to_dict(orient="index")

    @classmethod
    def save_csv(cls, map_dict: Dict[str, Dict[str, str]], path: Path = None) -> None:
        path = path or cls.MAP_PATH
        df = pd.DataFrame.from_dict(data=map_dict, orient="index")
        df.index.name = "trail"
        df.to_csv(path_or_buf=path)

    @property
    def map_dict(self) -> Dict[str, Dict[str, str]]:
        return self.__map_dict

    def get_view_function(self, trail: str) -> Optional[str]:
        """Retrieves the view function from the mapping.

        Views ends with "_chart".

        Args:
            trail (str): Trail like "futures.curves_chart"

        Returns:
            Optional[str]: View function import path.
        """

        map_dict = self.__map_dict
        trail = trail[: -len("_chart")]

        view = None
        if trail in map_dict and "view" in map_dict[trail] and map_dict[trail]["view"]:
            view = map_dict[trail]["view"]

        return view

    def get_model_function(self, trail: str) -> Optional[str]:
        map_dict = self.map_dict

        model = None
        if trail in map_dict and "view" in map_dict[trail] and map_dict[trail]["model"]:
            model = map_dict[trail]["model"]

        return model

    def get_model_or_view(self, trail: str) -> str:
        model_path = self.get_model_function(trail=trail)
        view_path = self.get_view_function(trail=trail)

        if model_path:
            method_path = model_path
        elif view_path:
            method_path = view_path
        else:
            raise AttributeError(f"Unknown method : {trail}")

        return method_path

    def load(self):
        map_dict = self.load_csv(path=self.MAP_PATH)
        if FORECASTING:
            map_forecasting_dict = self.load_csv(path=self.MAP_FORECASTING_PATH)
            map_dict = {**map_dict, **map_forecasting_dict}

        self.__map_dict = map_dict

    def __init__(self):
        self.load()
