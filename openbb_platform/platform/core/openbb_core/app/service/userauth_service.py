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
            self._router = self._get_router(entry_mod)
            self._auth_hook = self._get_auth_hook(entry_mod)
            self._bootstrap(entry_mod)

    @property
    def is_installed(self) -> bool:
        """Checks if extension is installed."""
        return self._is_installed("userauth")

    @property
    def router(self) -> APIRouter:
        """Gets router."""
        return self._router

    @property
    def auth_hook(self) -> Callable:
        """Gets authentication hook."""
        return self._auth_hook

    @staticmethod
    def _get_router(entry_mod: ModuleType) -> APIRouter:
        """Get router."""
        return getattr(entry_mod, "router", None)

    @staticmethod
    def _get_auth_hook(entry_mod: ModuleType) -> Callable:
        """Get authentication hook."""
        func = getattr(entry_mod, "get_auth_hook", None)
        if func:
            func()

    @staticmethod
    def _bootstrap(entry_mod: ModuleType) -> None:
        """Bootstrap the extension with the given actions."""
        func = getattr(entry_mod, "bootstrap", None)
        if func:
            func()

    @staticmethod
    def _is_installed(ext_name: str, group: str = EXT_GROUP) -> bool:
        """Checks if extension is installed."""
        return ext_name in [ext.name for ext in entry_points(group=group)]

    @staticmethod
    def _get_entry_mod(ext_name: str, group: str = EXT_GROUP) -> ModuleType:
        """Get the module of the given extension."""
        return import_module(entry_points(group=group)[ext_name].module)
