import os
from os import _Environ
from pathlib import Path

import dotenv

from openbb_core.app.model.abstract.singleton import SingletonMeta


class Env(metaclass=SingletonMeta):
    _environ: _Environ

    def __init__(self) -> None:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        dotenv.load_dotenv(Path(current_dir, ".env"))
        self._environ = os.environ

    @property
    def DEBUG_MODE(self) -> bool:
        return self.str_to_bool(self._environ.get("DEBUG_MODE", False))

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
