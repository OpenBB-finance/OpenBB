"""认证服务。"""

import logging
from collections.abc import Awaitable, Callable
from importlib import import_module
from types import ModuleType

from fastapi import APIRouter
from openbb_core.api.router.user import (
    auth_hook as default_auth_hook,
    router as default_router,
    user_settings_hook as default_user_settings_hook,
)
from openbb_core.app.extension_loader import ExtensionLoader
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.env import Env

EXT_NAME = Env().API_AUTH_EXTENSION

logger = logging.getLogger("uvicorn.error")


class AuthServiceError(Exception):
    """认证服务错误。"""


class AuthService(metaclass=SingletonMeta):
    """认证服务。"""

    def __init__(self, ext_name: str | None = EXT_NAME) -> None:
        """初始化 AuthService。"""
        if not self._load_extension(ext_name):
            self._router = default_router
            self._auth_hook = default_auth_hook
            self._user_settings_hook = default_user_settings_hook

    @property
    def router(self) -> APIRouter:
        """获取路由器。"""
        return self._router

    @property
    def auth_hook(self) -> Callable[..., Awaitable[None]]:
        """获取通用认证钩子。"""
        return self._auth_hook

    @property
    def user_settings_hook(self) -> Callable[..., Awaitable[UserSettings]]:
        """获取用户设置钩子。"""
        return self._user_settings_hook

    @staticmethod
    def _is_installed(ext_name: str) -> bool:
        """检查是否安装了 auth_extension。"""
        extension = ExtensionLoader().get_core_entry_point(ext_name) or False
        return extension and ext_name == extension.name  # type: ignore

    @staticmethod
    def _get_entry_mod(ext_name: str) -> ModuleType:
        """获取给定 auth_extension 的模块。"""
        extension = ExtensionLoader().get_core_entry_point(ext_name)
        if not extension:
            raise AuthServiceError(f"未安装扩展 '{ext_name}'。")
        return import_module(extension.module)

    def _load_extension(self, ext_name: str | None) -> bool:
        """加载认证扩展。"""
        if ext_name and self._is_installed(ext_name):
            entry_mod = self._get_entry_mod(ext_name)
            self._router = entry_mod.router
            self._auth_hook = entry_mod.auth_hook
            self._user_settings_hook = entry_mod.user_settings_hook
            logger.info("已加载 auth_extension：%s", ext_name)
            return True
        return False
