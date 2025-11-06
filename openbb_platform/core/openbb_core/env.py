"""Environment variables."""

import os
from pathlib import Path

import dotenv
from openbb_core.app.constants import OPENBB_DIRECTORY
from openbb_core.app.model.abstract.singleton import SingletonMeta


class Env(metaclass=SingletonMeta):
    """Environment variables."""

    _environ: dict[str, str]

    def __init__(self) -> None:
        """Initialize the environment."""
        dotenv.load_dotenv(Path(OPENBB_DIRECTORY, ".env"))
        self._environ = os.environ.copy()

    @property
    def API_AUTH(self) -> bool:
        """API authentication: enables API endpoint authentication."""
        return self.str2bool(self._environ.get("OPENBB_API_AUTH", False))

    @property
    def API_USERNAME(self) -> str | None:
        """API username: sets API username."""
        return self._environ.get("OPENBB_API_USERNAME", None)

    @property
    def API_PASSWORD(self) -> str | None:
        """API password: sets API password."""
        return self._environ.get("OPENBB_API_PASSWORD", None)

    @property
    def API_AUTH_EXTENSION(self) -> str | None:
        """Auth extension: specifies which authentication extension to use."""
        return self._environ.get("OPENBB_API_AUTH_EXTENSION", None)

    @property
    def AUTO_BUILD(self) -> bool:
        """Automatic build: enables automatic package build on import."""
        return self.str2bool(self._environ.get("OPENBB_AUTO_BUILD", True))

    @property
    def DEBUG_MODE(self) -> bool:
        """Debug mode: enables debug mode."""
        return self.str2bool(self._environ.get("OPENBB_DEBUG_MODE", False))

    @property
    def DEV_MODE(self) -> bool:
        """Dev mode: enables development mode."""
        return self.str2bool(self._environ.get("OPENBB_DEV_MODE", False))

    @property
    def ALLOW_MUTABLE_EXTENSIONS(self) -> bool:
        """Allow mutable extensions: enables extensions that modify OBBject output."""
        return self.str2bool(
            self._environ.get("OPENBB_ALLOW_MUTABLE_EXTENSIONS", False)
        )

    @property
    def ALLOW_ON_COMMAND_OUTPUT(self) -> bool:
        """Allow on command output: enables extensions that act on command output."""
        return self.str2bool(self._environ.get("OPENBB_ALLOW_ON_COMMAND_OUTPUT", False))

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
