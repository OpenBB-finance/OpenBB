"""Settings module."""

import sys
from copy import deepcopy
from pathlib import Path
from typing import Optional

from openbb import obb
from openbb_core.app.model.user_settings import UserSettings as User
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from src.config.console import Console
from src.config.constants import HIST_FILE_PROMPT
from src.config.style import Style
from src.models.settings import Settings
from src.models.singleton import SingletonMeta


class Session(metaclass=SingletonMeta):
    """Session service."""

    def __init__(self):
        """Initialize system service."""
        self._user = self._read_platform_user()
        self._settings = self._read_terminal_settings()
        self._style = Style(
            style=self._settings.RICH_STYLE,
            directory=Path(self._user.preferences.user_styles_directory),
        )
        self._console = Console(
            settings=self._settings, style=self._style.console_style
        )
        self._prompt_session = self._get_prompt_session()

    @property
    def user(self) -> User:
        """Get platform user."""
        return self._user

    @property
    def settings(self) -> Settings:
        """Get terminal settings."""
        return self._settings

    @property
    def style(self) -> Style:
        """Get terminal style."""
        return self._style

    @property
    def console(self) -> Console:
        """Get console."""
        return self._console

    @property
    def prompt_session(self) -> Optional[PromptSession]:
        """Get prompt session."""
        return self._prompt_session

    @classmethod
    def _read_platform_user(cls) -> User:
        """Get platform user."""
        if hasattr(obb, "user"):
            return deepcopy(obb.user)
        raise AttributeError("The 'obb' object has no attribute 'user'")

    @classmethod
    def _read_terminal_settings(cls) -> Settings:
        """Get terminal settings."""
        # read from .env files
        return Settings()

    def _get_prompt_session(self) -> Optional[PromptSession]:
        """Initialize prompt session."""
        try:
            if sys.stdin.isatty():
                prompt_session: Optional[PromptSession] = PromptSession(
                    history=FileHistory(str(HIST_FILE_PROMPT))
                )
            else:
                prompt_session = None
        except Exception:
            prompt_session = None

        return prompt_session

    def is_local(self) -> bool:
        """Check if user is local."""
        return not bool(self.user.profile.hub_session)

    def reset(self) -> None:
        pass


# from src.config.constants import (
#     ENV_FILE_PROJECT,
#     ENV_FILE_REPOSITORY,
#     ENV_FILE_SETTINGS,
# )

# DEFAULT_ORDER = [ENV_FILE_SETTINGS, ENV_FILE_PROJECT, ENV_FILE_REPOSITORY]


# def load_env_files():
#     """Load .env files.

#     Loads the dotenv files in the following order:
#     1. Repository .env file
#     2. Package .env file
#     3. User .env file

#     This allows the user to override the package settings with their own
#     settings, and the package to override the repository settings.

#     openbb_terminal modules are reloaded to refresh config files with new env,
#     otherwise they will use cache with old variables.
#     """
#     load_dotenv(ENV_FILE_REPOSITORY, override=True)
#     load_dotenv(ENV_FILE_PROJECT, override=True)
#     load_dotenv(ENV_FILE_SETTINGS, override=True)


# def get_reading_order() -> list:
#     """Get order of .env files.

#     If we are on frozen app, we reverse the order to read the ENV_FILE_SETTINGS last.

#     Returns
#     -------
#     list
#         List of .env files.
#     """
#     local_order = DEFAULT_ORDER.copy()
#     if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
#         local_order.reverse()
#     return local_order


# def read_env() -> Dict[str, Any]:
#     """Read .env files."""
#     __env_dict: Dict[str, Optional[str]] = {}

#     for env_file in get_reading_order():
#         if env_file.exists():
#             __env_dict.update(**dotenv_values(env_file))

#     __env_dict_filtered = {
#         k[len("OPENBBB_") - 1 :]: v
#         for k, v in __env_dict.items()
#         if k.startswith("OPENBB_")
#     }

#     return __env_dict_filtered
