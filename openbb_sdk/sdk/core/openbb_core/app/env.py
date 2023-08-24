import os
from pathlib import Path
from typing import Dict

import dotenv

from openbb_core.app.model.abstract.singleton import SingletonMeta


class Env(metaclass=SingletonMeta):
    _environ: Dict[str, str]

    def __init__(self) -> None:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        dotenv.load_dotenv(Path(current_dir, ".env"))
        self._environ = os.environ.copy()

    @property
    def DEBUG_MODE(self) -> bool:
        return self.str_to_bool(self._environ.get("OPENBB_DEBUG_MODE", False))

    @property
    def DEV_MODE(self) -> bool:
        # TODO: Change default to false when ready to deploy
        return self.str_to_bool(self._environ.get("OPENBB_DEV_MODE", True))

    @staticmethod
    def str_to_bool(value) -> bool:
        """Match a string to a boolean value."""
        if isinstance(value, bool):
            return value
        if value.lower() in {"false", "f", "0", "no", "n"}:
            return False
        if value.lower() in {"true", "t", "1", "yes", "y"}:
            return True
        raise ValueError(f"Failed to cast {value} to bool.")
