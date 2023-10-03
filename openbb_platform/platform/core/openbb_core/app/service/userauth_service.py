from importlib import import_module
from types import ModuleType
from typing import Callable

from fastapi import APIRouter
from importlib_metadata import entry_points
from openbb_core.api.router.user import router as DefaultRouter
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.env import Env

EXT_GROUP = "openbb_core_extension"
EXT_NAME = Env().AUTH_EXTENSION


def get_user_settings():
    pass


class UserAuthService(metaclass=SingletonMeta):
    def __init__(
        self,
        default_router: APIRouter = DefaultRouter,
        default_auth_hook: Callable = get_user_settings,
    ) -> None:
        """Initializes UserAuthService."""
        auth_extension = EXT_NAME
        if auth_extension and self._is_installed(auth_extension):
            entry_mod = self._get_entry_mod(auth_extension)
            self._router = getattr(entry_mod, "router", None)
            self._auth_hook = getattr(entry_mod, "auth_hook", None)
        else:
            self._router = default_router
            self._auth_hook = default_auth_hook

    @property
    def router(self) -> APIRouter:
        """Gets router."""
        return self._router

    @property
    def auth_hook(self) -> Callable:
        """Gets authentication hook."""
        return self._auth_hook

    @staticmethod
    def _is_installed(ext_name: str, group: str = EXT_GROUP) -> bool:
        """Checks if auth_extension is installed."""
        return ext_name in [ext.name for ext in entry_points(group=group)]

    @staticmethod
    def _get_entry_mod(ext_name: str, group: str = EXT_GROUP) -> ModuleType:
        """Get the module of the given auth_extension."""
        return import_module(entry_points(group=group)[ext_name].module)
