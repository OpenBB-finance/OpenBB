from importlib import import_module
from types import ModuleType
from typing import Callable, Optional

from fastapi import APIRouter
from importlib_metadata import entry_points
from openbb_core.app.model.abstract.singleton import SingletonMeta

EXT_GROUP = "openbb_core_extension"


class UserAuthService(metaclass=SingletonMeta):
    def __init__(self) -> None:
        """Initializes UserAuthService."""
        self._router: Optional[APIRouter] = None
        self._auth_hook: Optional[Callable] = None
        if self.is_installed:
            entry_mod = self._get_entry_mod("userauth")
            self._router = getattr(entry_mod, "router", None)
            self._auth_hook = getattr(entry_mod, "get_auth_hook", lambda: None)()
            getattr(entry_mod, "bootstrap", lambda: None)()

    @property
    def is_installed(self) -> bool:
        """Checks if extension is installed."""
        return self._is_installed("userauth")

    @property
    def router(self) -> Optional[APIRouter]:
        """Gets router."""
        return self._router

    @property
    def auth_hook(self) -> Optional[Callable]:
        """Gets authentication hook."""
        return self._auth_hook

    @staticmethod
    def _is_installed(ext_name: str, group: str = EXT_GROUP) -> bool:
        """Checks if extension is installed."""
        return ext_name in [ext.name for ext in entry_points(group=group)]

    @staticmethod
    def _get_entry_mod(ext_name: str, group: str = EXT_GROUP) -> ModuleType:
        """Get the module of the given extension."""
        return import_module(entry_points(group=group)[ext_name].module)
