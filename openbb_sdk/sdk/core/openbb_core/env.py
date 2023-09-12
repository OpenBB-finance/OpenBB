import os
from pathlib import Path
from typing import Dict

import dotenv

from openbb_core.app.constants import OPENBB_DIRECTORY
from openbb_core.app.model.abstract.singleton import SingletonMeta


class Env(metaclass=SingletonMeta):
    _environ: Dict[str, str]

    def __init__(self) -> None:
        dotenv.load_dotenv(Path(OPENBB_DIRECTORY, ".env"))
        self._environ = os.environ.copy()

    @property
    def DEBUG_MODE(self) -> bool:
        """Debug mode: enables verbosity while running the program"""
        return self.str2bool(self._environ.get("OPENBB_DEBUG_MODE", False))

    @property
    def DEV_MODE(self) -> bool:
        """Develop mode: points hub service to .co or .dev"""
        return self.str2bool(self._environ.get("OPENBB_DEV_MODE", False))

    @property
    def AUTO_BUILD(self) -> bool:
        """Automatic build: enables automatic SDK package build on import"""
        return self.str2bool(self._environ.get("OPENBB_AUTO_BUILD", True))

    @property
    def CHARTING_EXTENSION(self) -> str:
        """Charting extension: enables charting extension"""
        return self._environ.get("OPENBB_CHARTING_EXTENSION", "openbb_charting")

    @property
    def API_AUTH(self) -> bool:
        """API authentication: enables commands authentication in FastAPI"""
        return self.str2bool(self._environ.get("OPENBB_API_AUTH", True))

    @staticmethod
    def str2bool(value) -> bool:
        """Match a value to its boolean correspondent."""
        if isinstance(value, bool):
            return value
        if value.lower() in {"false", "f", "0", "no", "n"}:
            return False
        if value.lower() in {"true", "t", "1", "yes", "y"}:
            return True
        raise ValueError(f"Failed to cast {value} to bool.")
