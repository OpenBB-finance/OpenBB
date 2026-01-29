"""提供者注册表模块。"""

import traceback
import warnings
from functools import lru_cache

from openbb_core.app.extension_loader import ExtensionLoader
from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.env import Env
from openbb_core.provider.abstract.provider import Provider


class Registry:
    """维护提供者注册表。"""

    def __init__(self) -> None:
        """初始化注册表。"""
        self._providers: dict[str, Provider] = {}

    @property
    def providers(self):
        """返回提供者字典。"""
        return self._providers

    def include_provider(self, provider: Provider) -> None:
        """在注册表中包含提供者。"""
        self._providers[provider.name.lower()] = provider


class LoadingError(Exception):
    """加载提供者出错。"""


class RegistryLoader:
    """从入口点加载提供者。"""

    @staticmethod
    @lru_cache
    def from_extensions() -> Registry:
        """从入口点加载提供者。"""
        registry = Registry()

        for name, entry in ExtensionLoader().provider_objects.items():  # type: ignore[attr-defined]
            try:
                registry.include_provider(provider=entry)
            except Exception as e:
                msg = f"加载扩展出错：{name}\n"
                if Env().DEBUG_MODE:
                    traceback.print_exception(type(e), e, e.__traceback__)
                    raise LoadingError(msg + f"\033[91m{e}\033[0m") from e
                warnings.warn(
                    message=msg,
                    category=OpenBBWarning,
                )
        return registry
