from pathlib import Path
from typing import Dict

import pandas as pd

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY

try:
    import darts  # pylint: disable=W0611 # noqa: F401

    # If you just import darts this will pass during pip install, this creates
    # Failures later on, also importing utils ensures that darts is installed correctly
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

    def load(self):
        map_dict = self.load_csv(path=self.MAP_PATH)
        if FORECASTING:
            map_forecasting_dict = self.load_csv(path=self.MAP_FORECASTING_PATH)
            map_dict = {**map_dict, **map_forecasting_dict}

        self.__map_dict = map_dict

    def __init__(self):
        self.load()
