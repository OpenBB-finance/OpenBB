"""扩展加载器。"""

from enum import Enum
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, FastAPI
from importlib_metadata import EntryPoint, EntryPoints, entry_points
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.extension import Extension

if TYPE_CHECKING:
    from openbb_core.app.router import Router
    from openbb_core.provider.abstract.provider import Provider


class OpenBBGroups(Enum):
    """OpenBB 扩展组。"""

    core = "openbb_core_extension"
    provider = "openbb_provider_extension"
    obbject = "openbb_obbject_extension"

    @staticmethod
    def groups() -> list[str]:
        """返回 OpenBBGroups。"""
        return [
            OpenBBGroups.core.value,
            OpenBBGroups.provider.value,
            OpenBBGroups.obbject.value,
        ]


class ExtensionLoader(metaclass=SingletonMeta):
    """扩展加载器类。"""

    def __init__(
        self,
    ) -> None:
        """初始化扩展加载器。"""
        self._obbject_entry_points: EntryPoints = self._sorted_entry_points(
            group=OpenBBGroups.obbject.value
        )
        self._core_entry_points: EntryPoints = self._sorted_entry_points(
            group=OpenBBGroups.core.value
        )
        self._provider_entry_points: EntryPoints = self._sorted_entry_points(
            group=OpenBBGroups.provider.value
        )
        self._obbject_objects: dict[str, Extension] = {}
        self._core_objects: dict[str, Router] = {}
        self._provider_objects: dict[str, Provider] = {}
        self._on_command_output_callbacks: dict[str, list[Extension]] = {}
        self._register_command_output_callbacks()

    @property
    def on_command_output_callbacks(self) -> dict[str, list[Extension]]:
        """返回命令输出回调。"""
        return self._on_command_output_callbacks

    def _register_command_output_callbacks(self) -> None:
        """注册在命令输出上起作用的扩展。"""
        for ext in self.obbject_objects.values():
            if ext.on_command_output:
                paths = ext.command_output_paths or ["*"]
                for path in paths:
                    if path not in self._on_command_output_callbacks:
                        self._on_command_output_callbacks[path] = []
                    self._on_command_output_callbacks[path].append(ext)

    @property
    def obbject_entry_points(self) -> EntryPoints:
        """返回 obbject 入口点。"""
        return self._obbject_entry_points

    @property
    def core_entry_points(self) -> EntryPoints:
        """返回核心入口点。"""
        return self._core_entry_points

    @property
    def provider_entry_points(self) -> EntryPoints:
        """返回提供者入口点。"""
        return self._provider_entry_points

    @property
    def entry_points(self) -> list[EntryPoints]:
        """返回入口点。"""
        return [
            self._core_entry_points,
            self._provider_entry_points,
            self._obbject_entry_points,
        ]

    @staticmethod
    def _get_entry_point(
        entry_points_: EntryPoints, ext_name: str
    ) -> EntryPoint | None:
        """给定扩展名称和入口点列表，返回相应的入口点。"""
        return next((ep for ep in entry_points_ if ep.name == ext_name), None)

    def get_obbject_entry_point(self, ext_name: str) -> EntryPoint | None:
        """给定扩展名称，返回相应的入口点。"""
        return self._get_entry_point(self._obbject_entry_points, ext_name)

    def get_core_entry_point(self, ext_name: str) -> EntryPoint | None:
        """给定扩展名称，返回相应的入口点。"""
        return self._get_entry_point(self._core_entry_points, ext_name)

    def get_provider_entry_point(self, ext_name: str) -> EntryPoint | None:
        """给定扩展名称，返回相应的入口点。"""
        return self._get_entry_point(self._provider_entry_points, ext_name)

    @property
    @lru_cache
    def obbject_objects(self) -> dict[str, Extension]:
        """返回 obbject 扩展对象的字典。"""
        self._obbject_objects = self._load_entry_points(
            self._obbject_entry_points, OpenBBGroups.obbject
        )
        return self._obbject_objects

    @property
    @lru_cache
    def core_objects(self) -> dict[str, "Router"]:
        """返回核心扩展对象的字典。"""
        self._core_objects = self._load_entry_points(
            self._core_entry_points, OpenBBGroups.core
        )
        return self._core_objects

    @property
    @lru_cache
    def provider_objects(self) -> dict[str, "Provider"]:
        """返回提供者扩展对象的字典。"""
        self._provider_objects = self._load_entry_points(
            self._provider_entry_points, OpenBBGroups.provider
        )
        return self._provider_objects

    @staticmethod
    def _sorted_entry_points(group: str) -> EntryPoints:
        """返回入口点的排序字典。"""
        return sorted(entry_points(group=group))  # type: ignore

    def _load_entry_points(
        self, entry_points_: EntryPoints, group: OpenBBGroups
    ) -> dict[str, Any]:
        """返回与入口点匹配的对象字典。"""

        def load_obbject(eps: EntryPoints) -> dict[str, Extension]:
            """
            返回 obbject 对象的字典。

            键是入口点名称，值是 Extension 类的实例。
            """
            return {
                ep.name: entry
                for ep in eps
                if isinstance((entry := ep.load()), Extension)
            }

        def load_core(eps: EntryPoints) -> dict[str, "Router"]:
            """返回核心对象的字典。"""
            # pylint: disable=import-outside-toplevel
            from openbb_core.app.router import Router

            entries: dict[str, Router] = {}
            for ep in eps:
                entry = ep.load()
                if isinstance(entry, Router):
                    entries[ep.name] = entry
                    continue
                if isinstance(entry, FastAPI):
                    entry = entry.router
                if isinstance(entry, APIRouter):
                    entries[ep.name] = Router.from_fastapi(entry)
            return entries

        def load_provider(eps: EntryPoints) -> dict[str, "Provider"]:
            """
            返回提供者对象的字典。

            键是入口点名称，值是 Provider 类的实例。
            """
            # pylint: disable=import-outside-toplevel
            from openbb_core.provider.abstract.provider import Provider

            entries: dict = {}
            for ep in eps:
                try:
                    if isinstance((entry := ep.load()), Provider):
                        entries[ep.name] = entry
                except ModuleNotFoundError:
                    continue
            return entries

        func = {
            OpenBBGroups.obbject: load_obbject,
            OpenBBGroups.core: load_core,
            OpenBBGroups.provider: load_provider,
        }
        return func[group](entry_points_)  # type: ignore
