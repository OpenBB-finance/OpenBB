import logging
from importlib import import_module
from types import ModuleType
from typing import Awaitable, Callable, Optional

from fastapi import APIRouter
from importlib_metadata import entry_points
from openbb_core.api.router.user import (
    auth_hook as default_auth_hook,
    router as default_router,
    user_settings_hook as default_user_settings_hook,
)
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.env import Env

EXT_GROUP = "openbb_core_extension"
EXT_NAME = Env().API_AUTH_EXTENSION

logger = logging.getLogger("uvicorn.error")


class AuthService(metaclass=SingletonMeta):
    def __init__(self, ext_name: Optional[str] = EXT_NAME) -> None:
        """Initializes AuthService."""
        if not self._load_extension(ext_name):
            self._router = default_router
            self._auth_hook = default_auth_hook
            self._user_settings_hook = default_user_settings_hook

    @property
    def router(self) -> APIRouter:
        """Gets router."""
        return self._router

    @property
    def auth_hook(self) -> Callable[..., Awaitable[None]]:
        """Gets general authentication hook."""
        return self._auth_hook

    @property
    def user_settings_hook(self) -> Callable[..., Awaitable[UserSettings]]:
        """Gets user settings hook."""
        return self._user_settings_hook

    @staticmethod
    def _is_installed(ext_name: str, group: str = EXT_GROUP) -> bool:
        """Checks if auth_extension is installed."""
        return ext_name in [ext.name for ext in entry_points(group=group)]

    @staticmethod
    def _get_entry_mod(ext_name: str, group: str = EXT_GROUP) -> ModuleType:
        """Get the module of the given auth_extension."""
        return import_module(entry_points(group=group)[ext_name].module)

    def _load_extension(self, ext_name: Optional[str]) -> bool:
        """Load auth extension."""
        if ext_name and self._is_installed(ext_name):
            entry_mod = self._get_entry_mod(ext_name)
            self._router = entry_mod.router
            self._auth_hook = entry_mod.auth_hook
            self._user_settings_hook = entry_mod.user_settings_hook
            logger.info("Loaded auth_extension: %s", ext_name)
            return True
        return False
