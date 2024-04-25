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
        self._obb = obb
        self._settings = self._read_terminal_settings()
        self._style = Style(
            style=self._settings.RICH_STYLE,
            directory=Path(self._obb.user.preferences.user_styles_directory),
        )
        self._console = Console(
            settings=self._settings, style=self._style.console_style
        )
        self._prompt_session = self._get_prompt_session()

    @property
    def user(self) -> User:
        """Get platform user."""
        return self._obb.user

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
