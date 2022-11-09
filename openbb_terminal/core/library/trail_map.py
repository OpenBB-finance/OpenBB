import pickle
from enum import Enum
from typing import Dict

import pandas as pd

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY


class PERSISTENCE_FORMAT(Enum):
    PICKLE = 1
    CSV = 2


class TrailMap:
    MAP_PICKLE_PATH = MISCELLANEOUS_DIRECTORY / "library" / "trail_map.pickle"
    MAP_CSV_PATH = MISCELLANEOUS_DIRECTORY / "library" / "trail_map.csv"

    @classmethod
    def load_pickle(
        cls,
    ) -> Dict[str, Dict[str, str]]:
        map_dict = {}
        with cls.MAP_PICKLE_PATH.open("rb") as f:
            map_dict = pickle.load(f)
        return map_dict

    @classmethod
    def save_pickle(cls, map_dict: Dict[str, Dict[str, str]]) -> None:
        cls.MAP_PICKLE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with cls.MAP_PICKLE_PATH.open("wb") as f:
            pickle.dump(map_dict, f)

    @classmethod
    def load_csv(cls) -> Dict[str, Dict[str, str]]:
        df = pd.read_csv(cls.MAP_CSV_PATH, keep_default_na=False)
        df.set_index("trail", inplace=True)
        return df.to_dict(orient="index")

    @classmethod
    def save_csv(cls, map_dict: Dict[str, Dict[str, str]]) -> None:
        df = pd.DataFrame.from_dict(data=map_dict, orient="index")
        df.index.name = "trail"
        df.to_csv(path_or_buf=cls.MAP_CSV_PATH)

    @property
    def map_dict(self) -> Dict[str, Dict[str, str]]:
        return self.__map_dict

    def load(self):
        persitence_format = self.__persistence_format

        if persitence_format == PERSISTENCE_FORMAT.CSV:
            map_dict = self.load_csv()
        elif persitence_format == PERSISTENCE_FORMAT.PICKLE:
            map_dict = self.load_pickle()
        else:
            raise AttributeError("Incorrect 'persitence_format'")

        self.__map_dict = map_dict

    def persist(self):
        map_dict = self.__map_dict
        persitence_format = self.__persistence_format

        if persitence_format == PERSISTENCE_FORMAT.CSV:
            self.save_csv(map_dict=map_dict)
        elif persitence_format == PERSISTENCE_FORMAT.PICKLE:
            self.save_pickle(map_dict=map_dict)
        else:
            raise AttributeError("Incorrect 'persitence_format'")

    def __init__(self, persistence_format: PERSISTENCE_FORMAT = None):
        self.__persistence_format = persistence_format or PERSISTENCE_FORMAT.CSV

        self.load()
