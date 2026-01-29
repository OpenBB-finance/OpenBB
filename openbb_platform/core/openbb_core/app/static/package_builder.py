"""包构建器类。"""

# pylint: disable=too-many-lines,too-many-locals,too-many-nested-blocks,too-many-statements,too-many-branches,too-many-positional-arguments,protected-access
import builtins
import contextlib
import inspect
import os
import re
import shutil
import sys
import textwrap
import typing as typing_module
from collections import OrderedDict
from collections.abc import Callable
from functools import partial
from inspect import Parameter, _empty, isclass, signature
from json import dumps, load
from pathlib import Path
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    Optional,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from fastapi import Query, Request, Response, WebSocket
from fastapi.routing import APIRoute
from importlib_metadata import entry_points
from openbb_core.app.extension_loader import ExtensionLoader, OpenBBGroups
from openbb_core.app.model.example import Example
from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import RouterLoader
from openbb_core.app.service.system_service import SystemService
from openbb_core.app.static.utils.console import Console
from openbb_core.app.static.utils.linters import Linters
from openbb_core.app.version import CORE_VERSION, VERSION
from openbb_core.env import Env
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
from starlette.routing import BaseRoute
from starlette.websockets import WebSocket as StarletteWebSocket
from typing_extensions import _AnnotatedAlias

if TYPE_CHECKING:
    # pylint: disable=import-outside-toplevel
    from numpy import ndarray  # noqa
    from pandas import DataFrame, Series  # noqa
    from openbb_core.provider.abstract.data import Data  # noqa

try:
    from openbb_charting import Charting  # type: ignore

    CHARTING_INSTALLED = True
except ImportError:
    CHARTING_INSTALLED = False

try:
    import fcntl  # type: ignore

    _HAS_FCNTL = True
except Exception:  # pylint: disable=broad-except  # noqa
    _HAS_FCNTL = False
    import msvcrt  # pylint: disable=unused-import  # noqa

DataProcessingSupportedTypes = TypeVar(
    "DataProcessingSupportedTypes",
    list,
    dict,
    "DataFrame",
    list["DataFrame"],
    "Series",
    list["Series"],
    "ndarray",
    "Data",
)

TAB = "    "


def create_indent(n: int) -> str:
    """创建 n 个缩进空格。"""
    return TAB * n


class FileLock:
    """仅用于此模块的简单跨平台文件锁包装器。"""

    def __init__(self, file_obj):
        """初始化文件锁。"""
        self._file = file_obj

    def acquire(self, blocking: bool = True) -> None:
        """获取文件锁。"""
        if _HAS_FCNTL:
            flags = fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB)
            fcntl.flock(self._file.fileno(), flags)
        else:  # Windows via msvcrt

            mode = msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK  # type: ignore # pylint: disable=E0601
            try:
                # 在文件开始处锁定 1 字节；file.seek(0) 以确保位置
                self._file.seek(0)
                msvcrt.locking(self._file.fileno(), mode, 1)  # type: ignore
            except OSError as exc:  # pragma: no cover - platform specific
                # Normalize to BlockingIOError for parity with fcntl non-blocking
                raise BlockingIOError from exc

    def release(self) -> None:
        """释放文件锁。"""
        try:
            if _HAS_FCNTL:
                fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
            else:
                try:
                    self._file.seek(0)
                    msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)  # type: ignore
                except OSError:
                    # 如果在 Windows 上解锁失败，请忽略 - 文件将很快关闭
                    pass
        except Exception:  # pylint: disable=broad-except  # noqa
            pass


class PackageBuilder:
    """构建平台的扩展包。"""

    def __init__(
        self, directory: Path | None = None, lint: bool = True, verbose: bool = False
    ) -> None:
        """初始化包构建器。"""
        self.directory = directory or Path(__file__).parent
        self.lint = lint
        self.verbose = verbose
        self.console = Console(verbose)
        self.route_map = PathHandler.build_route_map()
        self.path_list = PathHandler.build_path_list(route_map=self.route_map)
        self._lock_path = self.directory / ".build.lock"

    def auto_build(self) -> None:
        """如果构建的扩展与安装的扩展之间存在差异，则触发构建。"""
        if Env().AUTO_BUILD:
            reference = PackageBuilder._read(
                self.directory / "assets" / "reference.json"
            )
            ext_map = reference.get("info", {}).get("extensions", {})
            add, remove = PackageBuilder._diff(ext_map)
            if add:
                a = ", ".join(sorted(add))
                print(f"要添加的扩展：{a}")  # noqa: T201

            if remove:
                r = ", ".join(sorted(remove))
                print(f"要移除的扩展：{r}")  # noqa: T201

            if add or remove:
                print("\n正在构建...")  # noqa: T201
                self.build()

    def build(
        self,
        modules: str | list[str] | None = None,
    ) -> None:
        """构建平台的扩展。"""
        self._lock_path.touch(exist_ok=True)

        # 打开锁定文件并获取独占锁
        with open(self._lock_path, "w", encoding="utf-8") as lock_file:
            file_lock = FileLock(lock_file)
            try:
                # 获取文件的独占锁
                file_lock.acquire(blocking=False)

                # 将 PID 写入锁定文件以进行调试
                lock_file.seek(0)
                lock_file.truncate()
                lock_file.write(str(os.getpid()))
                lock_file.flush()

                # 实际构建步骤
                self.console.log("\n正在构建扩展包...\n")
                self._clean(modules)
                ext_map = self._get_extension_map()
                self._save_modules(modules, ext_map)
                self._save_reference_file(ext_map)
                self._save_package()
                if self.lint:
                    self._run_linters()
            except BlockingIOError:
                raise RuntimeError(  # noqa # pylint: disable=W0707
                    f"另一个构建进程正在运行并已锁定 {self._lock_path}"
                )
            finally:
                # 释放文件锁，在清理过程中抑制任何异常
                with contextlib.suppress(Exception):
                    file_lock.release()

    def _clean(self, modules: str | list[str] | None = None) -> None:
        """在构建之前删除 assets 和 package 文件夹或模块。"""
        shutil.rmtree(self.directory / "assets", ignore_errors=True)
        if modules:
            for module in modules:
                module_path = self.directory / "package" / f"{module}.py"
                if module_path.exists():
                    module_path.unlink()
        else:
            shutil.rmtree(self.directory / "package", ignore_errors=True)

    def _get_extension_map(self) -> dict[str, list[str]]:
        """获取构建时可用的扩展映射。"""
        el = ExtensionLoader()
        og = OpenBBGroups.groups()
        ext_map: dict[str, list[str]] = {}

        for group, entry_point in zip(og, el.entry_points):
            ext_map[group] = [
                f"{e.name}@{getattr(e.dist, 'version', '')}" for e in entry_point
            ]
        return ext_map

    def _save_modules(
        self,
        modules: str | list[str] | None = None,
        ext_map: dict[str, list[str]] | None = None,
    ):
        """保存模块。"""
        self.console.log("\n正在写入模块...")

        if not self.path_list:
            self.console.log("\n没有内容可写入。")
            return

        MAX_LEN = max([len(path) for path in self.path_list if path != "/"])

        _path_list = (
            [path for path in self.path_list if path in modules]
            if modules
            else self.path_list
        )

        for path in _path_list:
            route = PathHandler.get_route(path, self.route_map)
            # 仅当此路径没有直接路由时才创建模块
            # 这可以防止为类似 /empty/also_empty 的路径创建子路由器模块
            # 当实际路由是 /empty/also_empty/{param} 时
            if route is None:
                code = ModuleBuilder.build(path, ext_map)
                name = PathHandler.build_module_name(path)
                self.console.log(f"({path})", end=" " * (MAX_LEN - len(path)))
                self._write(code, name)

    def _save_package(self):
        """保存包。"""
        self.console.log("\n正在写入包 __init__...")
        code = '""" Autogenerated OpenBB module."""\n'
        code += "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###"
        self._write(code=code, name="__init__")

    def _save_reference_file(self, ext_map: dict[str, list[str]] | None = None):
        """保存 reference.json 文件。"""
        self.console.log("\n正在写入参考文件...")
        code = dumps(
            obj={
                "openbb": VERSION.replace("dev", ""),
                "info": {
                    "title": "OpenBB Platform (Python)",
                    "description": "Investment research for everyone, anywhere.",
                    "core": CORE_VERSION.replace("dev", ""),
                    "extensions": ext_map,
                },
                "paths": ReferenceGenerator.get_paths(self.route_map),
                "routers": ReferenceGenerator.get_routers(self.route_map),
            },
            indent=4,
        )
        self._write(code=code, name="reference", extension="json", folder="assets")

    def _run_linters(self):
        """运行 linters。"""
        self.console.log("\n正在运行 linters...")
        linters = Linters(self.directory / "package", self.verbose)
        linters.black()
        linters.ruff()

    def _write(
        self, code: str, name: str, extension: str = "py", folder: str = "package"
    ) -> None:
        """将模块写入包。"""
        package_folder = self.directory / folder
        package_path = package_folder / f"{name}.{extension}"
        package_folder.mkdir(exist_ok=True)
        self.console.log(str(package_path))

        with package_path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(code.replace("typing.", "").replace("List", "list"))

    @staticmethod
    def _read(path: Path) -> dict:
        """从文件夹获取内容。"""
        try:
            with open(Path(path)) as fp:
                content = load(fp)
        except Exception:
            content = {}

        return content

    @staticmethod
    def _diff(ext_map: dict[str, list[str]]) -> tuple[set[str], set[str]]:
        """检查已构建和已安装扩展之间的差异。

        Parameters
        ----------
        ext_map: Dict[str, List[str]]
            Dictionary containing the extensions.
            Example:
                {
                    "openbb_core_extension": [
                        "commodity@1.0.1",
                        ...
                    ],
                    "openbb_provider_extension": [
                        "benzinga@1.1.3",
                        ...
                    ],
                    "openbb_obbject_extension": [
                        "openbb_charting@1.0.0",
                        ...
                    ]
                }

        Returns
        -------
        Tuple[Set[str], Set[str]]
            第一个元素：已安装但不在包中的扩展集。
            第二个元素：在包中但未安装的扩展集。
        """
        add: set[str] = set()
        remove: set[str] = set()
        groups = OpenBBGroups.groups()

        for g in groups:
            built = set(ext_map.get(g, {}))
            installed = set(
                f"{e.name}@{getattr(e.dist, 'version', '')}"
                for e in entry_points(group=g)
            )
            add = add.union(installed - built)
            remove = remove.union(built - installed)

        return add, remove


class ModuleBuilder:
    """构建平台的模块。"""

    @staticmethod
    def build(path: str, ext_map: dict[str, list[str]] | None = None) -> str:
        """构建模块。"""
        code = f'"""Autogenerated OpenBB {path} Module."""\n\n'
        code += "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n\n#  pylint: disable=R0917,C0103,C0415\n\n"
        code += ImportDefinition.build(path)
        code += ClassDefinition.build(path, ext_map)

        return code


class ImportDefinition:
    """构建平台的导入定义。"""

    @staticmethod
    def _sanitize_type_name(type_name: str) -> str:
        """标准化从注释中提取的原始类型名称。"""
        sanitized = type_name.strip().replace('"', "").replace("'", "")
        sanitized = sanitized.replace("typing.", "").replace("typing_extensions.", "")
        sanitized = sanitized.split("[", 1)[0]
        sanitized = sanitized.split("(", 1)[0]
        return sanitized

    @staticmethod
    def filter_hint_type_list(hint_type_list: list[type]) -> list[type]:
        """过滤提示类型列表。"""
        new_hint_type_list = []
        primitive_types = {int, float, str, bool, list, dict, tuple, set}

        for hint_type in hint_type_list:
            # 跳过原始类型和空类型
            # 首先检查 _empty（不需要哈希）
            if hint_type == _empty:
                continue

            # 跳过 Depends 对象（它们不是我们需要导入的类型）
            if (
                hasattr(hint_type, "__class__")
                and "Depends" in hint_type.__class__.__name__
            ):
                continue

            # 跳过在其元数据中包含 Depends 的 Annotated 类型
            if isinstance(hint_type, _AnnotatedAlias):
                has_depends = False
                if hasattr(hint_type, "__metadata__"):
                    for meta in hint_type.__metadata__:
                        if (
                            hasattr(meta, "__class__")
                            and "Depends" in meta.__class__.__name__
                        ):
                            has_depends = True
                            break
                if has_depends:
                    continue

            # 现在可以安全地检查 primitive_types 集合
            try:
                if hint_type in primitive_types:
                    continue
            except TypeError:
                # 如果我们仍然得到一个不可哈希的类型，跳过它
                continue

            # 仅包含具有模块且不是内置函数的类型
            if (
                hasattr(hint_type, "__module__") and hint_type.__module__ != "builtins"
            ) or (isinstance(hint_type, str)):
                new_hint_type_list.append(hint_type)

        # 去重而不使用 set() 以处理不可哈希的类型
        deduplicated: list = []
        for hint_type in new_hint_type_list:
            is_duplicate = False
            for existing in deduplicated:
                try:
                    if hint_type == existing:
                        is_duplicate = True
                        break
                except TypeError:
                    # 如果比较失败，则按身份比较
                    if id(hint_type) == id(existing):
                        is_duplicate = True
                        break

            if not is_duplicate:
                deduplicated.append(hint_type)

        return deduplicated

    @classmethod
    def get_function_hint_type_list(cls, route) -> list[type]:
        """从函数获取提示类型列表。"""

        no_validate = (getattr(route, "openapi_extra", None) or {}).get("no_validate")

        func = route.endpoint
        sig = signature(func)
        if no_validate is True:
            route.response_model = None

        parameter_map = sig.parameters
        return_type = (
            sig.return_annotation if not no_validate else route.response_model or Any
        )

        hint_type_list: list = []

        for parameter in parameter_map.values():
            hint_type_list.append(parameter.annotation)

            # 从 Annotated 元数据中提取依赖项
            if isinstance(parameter.annotation, _AnnotatedAlias):
                for meta in parameter.annotation.__metadata__:
                    # 检查此是否为 Depends 对象
                    if hasattr(meta, "dependency"):
                        # 将依赖函数添加到 hint_type_list
                        hint_type_list.append(meta.dependency)

        if return_type:
            hint_type = (
                get_args(get_type_hints(return_type)["results"])[0]
                if hasattr(return_type, "__class__")
                and hasattr(return_type.__class__, "__name__")
                and "OBBject" in getattr(return_type.__class__, "__name__", "")
                else return_type
            )
            hint_type_list.append(hint_type)

        hint_type_list = cls.filter_hint_type_list(hint_type_list)

        return hint_type_list

    @classmethod
    def get_path_hint_type_list(cls, path: str) -> list[type]:
        """从路径获取提示类型列表。"""
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)
        child_path_list = PathHandler.get_child_path_list(
            path=path, path_list=path_list
        )
        hint_type_list = []
        for child_path in child_path_list:
            route = PathHandler.get_route(path=child_path, route_map=route_map)
            if route:
                if getattr(route, "deprecated", None):
                    hint_type_list.append(type(route.summary.metadata))  # type: ignore
                function_hint_type_list = cls.get_function_hint_type_list(route=route)  # type: ignore
                hint_type_list.extend(function_hint_type_list)

        for dependency in PathHandler.get_router_dependencies(path):
            dependency_func = getattr(dependency, "dependency", None)
            if callable(dependency_func):
                hint_type_list.append(dependency_func)

        hint_type_list = [
            d
            for d in list(set(hint_type_list))
            if d not in [int, list, str, dict, float, set, bool, tuple]
        ]
        return hint_type_list

    @classmethod
    def build(cls, path: str) -> str:
        """构建导入定义。"""
        hint_type_list = cls.get_path_hint_type_list(path=path)
        code = "from openbb_core.app.static.container import Container"
        code += "\nfrom openbb_core.app.model.obbject import OBBject"

        # 这些导入在构建之前未检测到，因此我们手动添加它们，并
        # 运行 ruff --fix 以删除未使用的导入。
        # TODO: 找到更好的方法来处理此问题。这是一个临时解决方案。
        code += "\nimport openbb_core.provider"
        code += "\nfrom openbb_core.provider.abstract.data import Data"
        code += "\nimport pandas"
        code += "\nfrom pandas import DataFrame, Series"
        code += "\nimport numpy"
        code += "\nfrom numpy import ndarray"
        code += "\nimport datetime"
        code += "\nfrom datetime import date"
        code += "\nimport pydantic"
        code += "\nfrom pydantic import BaseModel"
        code += "\nfrom inspect import Parameter"
        code += "\nimport typing"
        code += "\nfrom typing import TYPE_CHECKING, Annotated, ForwardRef, Union, Optional, Literal, Any"
        code += "\nfrom annotated_types import Ge, Le, Gt, Lt"
        code += "\nfrom warnings import warn, simplefilter"
        code += "\nfrom openbb_core.app.static.utils.decorators import exception_handler, validate\n"
        code += "\nfrom openbb_core.app.static.utils.filters import filter_inputs\n"
        code += "\nfrom openbb_core.app.deprecation import OpenBBDeprecationWarning\n"
        code += "\nfrom openbb_core.app.model.field import OpenBBField"
        code += "\nfrom fastapi import Depends"

        module_list = [
            hint_type.__module__ if hasattr(hint_type, "__module__") else hint_type
            for hint_type in hint_type_list
        ]
        module_list = list(set(module_list))
        module_list.sort()  # type: ignore

        code += "\n"
        for module in module_list:
            code += f"import {module}\n"

        # 按模块对类型进行分组并捕获导入的返回类型。
        module_types: dict = {}
        for hint_type in hint_type_list:
            if hasattr(hint_type, "__module__") and hint_type.__module__ != "builtins":
                module = hint_type.__module__

                if hasattr(hint_type, "__origin__"):
                    type_name = (
                        hint_type.__origin__.__name__
                        if hasattr(hint_type.__origin__, "__name__")
                        else str(hint_type.__origin__)
                    )
                else:
                    raw_type_name = getattr(
                        hint_type,
                        "__name__",
                        str(hint_type).rsplit(".", maxsplit=1)[-1],
                    )
                    type_name = (
                        raw_type_name.split("[")[0]
                        if "[" in raw_type_name
                        else raw_type_name
                    )

                type_name_str = str(type_name)
                if type_name_str.startswith("typing.Optional"):
                    continue
                if "|" in type_name_str:
                    continue

                sanitized_name = cls._sanitize_type_name(type_name_str)
                if not sanitized_name:
                    continue
                if (
                    module == "typing" and sanitized_name in dir(__builtins__)
                ) or sanitized_name in {
                    "Dict",
                    "List",
                    "int",
                    "float",
                    "str",
                    "dict",
                    "list",
                    "set",
                    "bool",
                    "tuple",
                }:
                    continue
                if not (
                    sanitized_name == "TYPE_CHECKING" or sanitized_name.isidentifier()
                ):
                    continue

                if module not in module_types:
                    module_types[module] = set()

                module_types[module].add(sanitized_name)

        # 为具有特定类型的模块生成 from-import 语句
        for module, types in sorted(module_types.items()):
            if module == "types":
                continue
            _types = types
            if module == "typing":
                _types = {t for t in types if hasattr(typing_module, t)}
                if not _types:
                    continue

            if len(_types) == 1:
                type_name = next(iter(_types))
                code += f"\nfrom {module} import {type_name}"
            else:
                import_types = [
                    d
                    for d in sorted(_types)
                    if d
                    not in [
                        "Dict",
                        "List",
                        "int",
                        "float",
                        "str",
                        "dict",
                        "list",
                        "set",
                    ]
                ]
                if import_types:
                    code += f"\nfrom {module} import ("
                    for type_name in import_types:
                        code += f"\n    {type_name},"
                    code += "\n)"
                    code += "\n"

        return code + "\n"


class ClassDefinition:
    """构建平台的类定义。"""

    @staticmethod
    def build(path: str, ext_map: dict[str, list[str]] | None = None) -> str:
        """构建类定义。"""
        class_name = PathHandler.build_module_class(path=path)
        code = f"class {class_name}(Container):\n"
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map)
        child_path_list = sorted(
            PathHandler.get_child_path_list(
                path,
                path_list,
            )
        )
        doc = f'    """{path}\n' if path else '    # fmt: off\n    """\nRouters:\n'
        methods = ""

        for c in child_path_list:
            route = PathHandler.get_route(c, route_map)
            has_subroutes = any(r.startswith(c + "/") and r != c for r in route_map)

            if route is None:
                if has_subroutes:
                    doc += "    /" if path else "    /"
                    doc += c.split("/")[-1] + "\n"
                    methods += MethodDefinition.build_class_loader_method(path=c)
                continue

            route_methods = getattr(route, "methods", None)
            is_command_route = (
                route
                and hasattr(route, "endpoint")
                and callable(route.endpoint)  # type: ignore
                and isinstance(route_methods, set)
                and route_methods
            )

            if (path == "" and is_command_route) or "." in path:
                continue

            if is_command_route:
                doc += f"    {route.name}\n"  # type: ignore
                methods += MethodDefinition.build_command_method(
                    path=route.path,  # type: ignore
                    func=route.endpoint,  # type: ignore
                    model_name=(
                        route.openapi_extra.get("model", None)  # type: ignore
                        if hasattr(route, "openapi_extra")  # type: ignore
                        and getattr(route, "openapi_extra", None) is not None
                        else None
                    ),
                    examples=(
                        route.openapi_extra.get("examples", [])  # type: ignore
                        if hasattr(route, "openapi_extra")  # type: ignore
                        and getattr(route, "openapi_extra", None) is not None
                        else []
                    ),
                )
                continue

            if has_subroutes:
                # 这是一个子路由器路径 - 创建一个属性
                doc += "    /" if path else "    /"
                doc += c.split("/")[-1] + "\n"
                methods += MethodDefinition.build_class_loader_method(path=c)

        if not path:
            if ext_map:
                doc += "\n"
                doc += "Extensions:\n"
                doc += "\n".join(
                    [f"    - {ext}" for ext in ext_map.get("openbb_core_extension", [])]
                )
                doc += "\n\n"
                doc += "\n".join(
                    [
                        f"    - {ext}"
                        for ext in ext_map.get("openbb_provider_extension", [])
                    ]
                )
            doc += '    """\n'
            doc += "    # fmt: on\n"
        else:
            doc += '    """\n'

        code += doc + "\n"
        code += "    def __repr__(self) -> str:\n"
        code += '        return self.__doc__ or ""\n'
        code += methods

        return code


class MethodDefinition:
    """构建平台的方法定义。"""

    # 这些是我们想要扩展的类型。
    # 例如，start_date 始终是 'date'，但也接受 'str' 作为输入。
    # 小心，如果 pydantic 无法将类型强制转换为原始类型，您
    # 需要在输入过滤器中添加一些转换代码。
    TYPE_EXPANSION = {
        "data": DataProcessingSupportedTypes,
        "start_date": str,
        "end_date": str,
        "date": str,
        "provider": None,
    }

    REQUEST_BOUND_PARAM_TYPES = tuple(
        t
        for t in (
            Request,
            StarletteRequest,
            Response,
            StarletteResponse,
            WebSocket,
            StarletteWebSocket,
        )
        if t is not None
    )
    REQUEST_BOUND_ANNOTATION_NAMES = {
        "header",
        "request",
        "fastapi.request",
        "fastapi.requests.request",
        "starlette.request",
        "starlette.requests.request",
        "response",
        "fastapi.response",
        "fastapi.responses.response",
        "starlette.response",
        "starlette.responses.response",
        "websocket",
        "starlette.websockets.websocket",
        "fastapi.websockets.websocket",
    }

    @staticmethod
    def _snake_case(name: str) -> str:
        if not name:
            return ""
        name = name.replace(".", "_")
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def _dependency_identifier(dependency_func: Callable) -> str:
        try:
            return_annotation = signature(dependency_func).return_annotation
        except (ValueError, TypeError):
            return_annotation = inspect._empty

        class_name = ""
        if return_annotation not in (inspect._empty, None):
            if isinstance(return_annotation, str):
                class_name = return_annotation.rsplit(".", maxsplit=1)[-1]
            elif isclass(return_annotation):
                class_name = return_annotation.__name__

        if not class_name and isclass(dependency_func):
            class_name = dependency_func.__name__

        if not class_name:
            func_name = dependency_func.__name__
            class_name = (
                func_name[4:]
                if func_name.startswith("get_") and len(func_name) > 4
                else func_name
            )

        identifier = MethodDefinition._snake_case(class_name)
        return identifier or MethodDefinition._snake_case(dependency_func.__name__)

    @staticmethod
    def _is_none_like_return(annotation: Any) -> bool:
        if annotation in (None, type(None)):
            return True
        if annotation is inspect._empty:
            return False
        if isinstance(annotation, str):
            normalized = annotation.lower().strip()
            normalized = normalized.replace("typing.", "")
            normalized = normalized.replace("builtins.", "")
            normalized = normalized.split("[", 1)[0]
            return normalized in {"none", "nonetype"}

        origin = get_origin(annotation)
        if origin is Union or (UnionType is not None and origin is UnionType):
            args = get_args(annotation) or getattr(annotation, "__args__", ())
            if not args:
                return True
            return all(MethodDefinition._is_none_like_return(arg) for arg in args)

        return False

    @staticmethod
    def _has_request_bound_annotation(annotation: Any) -> bool:
        if annotation is Parameter.empty:
            return False

        origin = get_origin(annotation)
        if origin is Annotated:
            args = get_args(annotation)
            if not args:
                return False
            return MethodDefinition._has_request_bound_annotation(args[0])

        origin = get_origin(annotation)
        if origin is Union or (UnionType is not None and origin is UnionType):
            args = get_args(annotation) or getattr(annotation, "__args__", ())
            return any(
                MethodDefinition._has_request_bound_annotation(arg) for arg in args
            )

        if isinstance(annotation, str):
            normalized = annotation.lower().strip()
            normalized = normalized.replace("typing.", "")
            normalized = normalized.replace("builtins.", "")
            normalized = normalized.split("[", 1)[0]
            return normalized in MethodDefinition.REQUEST_BOUND_ANNOTATION_NAMES

        if isinstance(annotation, type):
            return annotation in MethodDefinition.REQUEST_BOUND_PARAM_TYPES

        return annotation in MethodDefinition.REQUEST_BOUND_PARAM_TYPES

    @staticmethod
    def _is_safe_dependency(dependency_func: Callable) -> bool:
        try:
            sig = signature(dependency_func)
        except (TypeError, ValueError):
            return False

        if MethodDefinition._is_none_like_return(sig.return_annotation):
            return False

        for param in sig.parameters.values():
            annotation = param.annotation
            if MethodDefinition._has_request_bound_annotation(annotation):
                return False

            if (
                param.kind
                in (
                    Parameter.POSITIONAL_ONLY,
                    Parameter.POSITIONAL_OR_KEYWORD,
                    Parameter.KEYWORD_ONLY,
                )
                and param.default is Parameter.empty
            ):
                return False
        return True

    @staticmethod
    def build_class_loader_method(path: str) -> str:
        """构建类加载器方法。"""
        module_name = PathHandler.build_module_name(path=path)
        class_name = PathHandler.build_module_class(path=path)
        function_name = path.rsplit("/", maxsplit=1)[-1].strip("/")
        description = PathHandler.get_router_description(path)

        code = "\n    @property\n"
        code += f"    def {function_name}(self):\n"
        if description:
            escaped = description.replace('"""', '\\"\\"\\"')
            code += f'        """{escaped}"""\n'
        code += f"        from . import {module_name}\n\n"
        code += f"        return {module_name}.{class_name}(command_runner=self._command_runner)\n"

        return code

    @staticmethod
    def get_type(field: FieldInfo) -> type:
        """获取字段的类型。"""
        field_type = getattr(
            field, "annotation", getattr(field, "type", Parameter.empty)
        )
        if isclass(field_type):
            name = field_type.__name__
            if name.startswith("Constrained") and name.endswith("Value"):
                name = name[11:-5].lower()
                return getattr(builtins, name, field_type)
            return field_type
        return field_type

    @staticmethod
    def get_default(field: FieldInfo):
        """获取字段的默认值。"""
        # First check if field has a default attribute at all
        if not hasattr(field, "default"):
            return Parameter.empty

        # Check for Ellipsis directly in field.default
        if field.default is Ellipsis:
            return None

        if hasattr(field, "default") and hasattr(field.default, "default"):
            default_val = field.default.default
            if default_val is PydanticUndefined:
                return Parameter.empty
            if default_val is Ellipsis:
                return None
            return default_val
        return field.default

    @staticmethod
    def get_extra(field: FieldInfo) -> dict:
        """获取 json 架构额外信息。"""
        field_default = getattr(field, "default", None)
        if field_default:
            # Getting json_schema_extra without changing the original dict
            json_schema_extra = getattr(field_default, "json_schema_extra", {}).copy()
            json_schema_extra.pop("choices", None)
            return json_schema_extra
        return {}

    @staticmethod
    def is_annotated_dc(annotation) -> bool:
        """检查注释是否为带注释的数据类。"""
        return isinstance(annotation, _AnnotatedAlias) and hasattr(
            annotation.__args__[0], "__dataclass_fields__"
        )

    @staticmethod
    def is_data_processing_function(path: str) -> bool:
        """检查函数是否为数据处理函数。"""
        route = PathHandler.build_route_map().get(path)
        if not route:
            return False
        methods: set = getattr(route, "methods", set())
        # Consider POST, PUT, PATCH as data processing, but not GET
        return bool(methods & {"POST", "PUT", "PATCH"})

    @staticmethod
    def is_deprecated_function(path: str) -> bool:
        """检查函数是否已弃用。"""
        return getattr(PathHandler.build_route_map()[path], "deprecated", False)

    @staticmethod
    def get_deprecation_message(path: str) -> str:
        """获取弃用消息。"""
        return getattr(PathHandler.build_route_map()[path], "summary", "")

    @staticmethod
    def reorder_params(
        params: dict[str, Parameter],
        var_kw: list[str] | None = None,
        for_docstring: bool = False,
    ) -> "OrderedDict[str, Parameter]":
        """根据上下文重新排序参数。

        For function signatures: provider is placed last (before VAR_KEYWORD)
        For docstrings: provider is placed first
        """
        formatted_keys = list(params.keys())

        if for_docstring and "provider" in formatted_keys:
            # For docstrings: Place "provider" first
            formatted_keys.remove("provider")
            formatted_keys.insert(0, "provider")
        else:
            # For function signatures: Place "provider" and VAR_KEYWORD at the end
            for k in ["provider"] + (var_kw or []):
                if k in formatted_keys:
                    formatted_keys.remove(k)
                    formatted_keys.append(k)

        od: OrderedDict[str, Parameter] = OrderedDict()
        for k in formatted_keys:
            od[k] = params[k]

        return od

    @staticmethod
    def format_params(
        path: str, parameter_map: dict[str, Parameter]
    ) -> OrderedDict[str, Parameter]:
        """格式化参数。"""

        parameter_map.pop("cc", None)

        # Extract path parameters from the route path
        path_params = PathHandler.extract_path_parameters(path)

        # we need to add the chart parameter here bc of the docstring generation
        if CHARTING_INSTALLED and path.replace("/", "_")[1:] in Charting.functions():
            parameter_map["chart"] = Parameter(
                name="chart",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[
                    bool,
                    Query(
                        description="是否创建图表，默认为 False。",
                    ),
                ],
                default=False,
            )

        formatted: dict[str, Parameter] = {}
        var_kw = []

        # First, handle path parameters - they must come first
        for name in path_params:
            if name in parameter_map:
                formatted[name] = Parameter(
                    name=name,
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[
                        str,
                        OpenBBField(
                            description=f"路径参数：{name}",
                        ),
                    ],
                    default=Parameter.empty,  # Path params are always required
                )

        # Then process all other parameters
        for name, param in parameter_map.items():
            # Skip path parameters - they should be required string parameters
            if name in path_params or name in ("kwargs", "**kwargs"):
                continue  # Already handled above

            # Case 1: Handle Query objects inside Annotated
            if isinstance(param.annotation, _AnnotatedAlias):
                has_depends = any(
                    hasattr(meta, "dependency")
                    for meta in param.annotation.__metadata__
                )
                model = param.annotation.__args__[0]
                is_pydantic_model = hasattr(model, "model_fields") or hasattr(
                    model, "__pydantic_fields__"
                )
                is_get_request = not MethodDefinition.is_data_processing_function(path)

                if is_pydantic_model and is_get_request and not has_depends:
                    # Unpack the model fields as query parameters
                    fields = getattr(
                        model,
                        "model_fields",
                        getattr(model, "__pydantic_fields__", {}),
                    )
                    for field_name, field in fields.items():
                        type_ = field.annotation
                        default = (
                            field.default
                            if field.default is not PydanticUndefined
                            else Parameter.empty
                        )
                        description = getattr(field, "description", "")

                        extra = getattr(field, "json_schema_extra", {}) or {}
                        new_type = MethodDefinition.get_expanded_type(
                            field_name, extra, type_
                        )
                        updated_type = (
                            type_ if new_type is ... else Union[type_, new_type]  # noqa
                        )

                        formatted[field_name] = Parameter(
                            name=field_name,
                            kind=Parameter.POSITIONAL_OR_KEYWORD,
                            annotation=Annotated[
                                updated_type,
                                OpenBBField(
                                    description=description,
                                ),
                            ],
                            default=default,
                        )
                    continue

                query_obj = None
                # Look for Query object in the metadata
                for meta in param.annotation.__metadata__:
                    if (
                        hasattr(meta, "__class__")
                        and "Query" in meta.__class__.__name__
                    ):
                        query_obj = meta
                        break
                if query_obj:
                    description = getattr(query_obj, "description", "") or ""
                    default_value = getattr(query_obj, "default", Parameter.empty)
                    if default_value is PydanticUndefined:
                        default_value = Parameter.empty

                    # Create a new annotation with OpenBBField containing the description
                    formatted[name] = Parameter(
                        name=name,
                        kind=param.kind,
                        annotation=Annotated[
                            param.annotation.__args__[0],  # Get the original type
                            OpenBBField(
                                description=description,
                            ),
                        ],
                        default=param.default,
                    )
                    continue

            # Case 2: Handle Query objects as default values
            if (
                hasattr(param.default, "__class__")
                and "Query" in param.default.__class__.__name__
            ):
                query_obj = param.default
                description = getattr(query_obj, "description", "") or ""
                default_value = getattr(query_obj, "default", "")
                formatted[name] = Parameter(
                    name=name,
                    kind=param.kind,
                    annotation=Annotated[
                        param.annotation,
                        OpenBBField(
                            description=description,
                        ),
                    ],
                    default=(
                        Parameter.empty
                        if default_value is PydanticUndefined
                        or default_value is Ellipsis
                        else default_value
                    ),
                )
                continue

            if name == "extra_params":
                formatted[name] = Parameter(name="kwargs", kind=Parameter.VAR_KEYWORD)
                var_kw.append(name)
            elif name == "provider_choices":
                if param.annotation != Parameter.empty and hasattr(
                    param.annotation, "__args__"
                ):
                    fields = param.annotation.__args__[0].__dataclass_fields__
                    field = fields["provider"]
                else:
                    continue
                type_ = getattr(field, "type")
                default_priority = getattr(type_, "__args__")
                formatted["provider"] = Parameter(
                    name="provider",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[
                        Optional[MethodDefinition.get_type(field)],  # noqa
                        OpenBBField(
                            description=(
                                "要使用的提供者，默认为 None。"
                                "如果为 None，则使用设置中配置的优先级列表。"
                                f"默认优先级：{', '.join(default_priority)}。"
                            ),
                        ),
                    ],
                    default=None,
                )

            elif MethodDefinition.is_annotated_dc(param.annotation):
                fields = param.annotation.__args__[0].__dataclass_fields__
                for field_name, field in fields.items():
                    type_ = MethodDefinition.get_type(field)
                    default = MethodDefinition.get_default(field)
                    extra = MethodDefinition.get_extra(field)
                    new_type = MethodDefinition.get_expanded_type(
                        field_name, extra, type_
                    )
                    updated_type = (
                        type_ if new_type is ... else Union[type_, new_type]  # noqa
                    )

                    formatted[field_name] = Parameter(
                        name=field_name,
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=updated_type,
                        default=default,
                    )

            if isinstance(param.annotation, _AnnotatedAlias):
                # Specifically look for Depends dependency rather than any annotation
                has_depends = any(
                    hasattr(meta, "dependency")
                    for meta in param.annotation.__metadata__
                )
                if has_depends:
                    continue

                # If not a dependency, process it as a normal parameter
                new_type = MethodDefinition.get_expanded_type(name)
                updated_type = (
                    param.annotation
                    if new_type is ...
                    else Union[param.annotation, new_type]  # noqa
                )

                metadata = getattr(param.annotation, "__metadata__", [])
                description = (
                    getattr(metadata[0], "description", "") if metadata else ""
                )

                formatted[name] = Parameter(
                    name=name,
                    kind=param.kind,
                    annotation=Annotated[
                        updated_type,
                        OpenBBField(
                            description=description,
                        ),
                    ],
                    default=MethodDefinition.get_default(param),  # type: ignore
                )

            else:
                new_type = MethodDefinition.get_expanded_type(name)
                if hasattr(new_type, "__constraints__"):
                    types = new_type.__constraints__ + (param.annotation,)  # type: ignore
                    updated_type = Union[types]  # type: ignore  # noqa
                else:
                    updated_type = (
                        param.annotation
                        if new_type is ...
                        else Union[param.annotation, new_type]  # noqa
                    )

                metadata = getattr(param.annotation, "__metadata__", [])
                description = (
                    getattr(metadata[0], "description", "") if metadata else ""
                )
                # Untyped positional arguments are typed as Any
                updated_type = (
                    Any
                    if updated_type is inspect._empty  # pylint: disable=W0212
                    else updated_type
                )

                formatted[name] = Parameter(
                    name=name,
                    kind=param.kind,
                    annotation=Annotated[
                        updated_type,
                        OpenBBField(
                            description=description,
                        ),
                    ],
                    default=MethodDefinition.get_default(param),  # type: ignore
                )
                if param.kind == Parameter.VAR_KEYWORD:
                    var_kw.append(name)

        required_params = OrderedDict()
        optional_params = OrderedDict()

        for name, param in formatted.items():
            if param.default == Parameter.empty:
                required_params[name] = param
            else:
                optional_params[name] = param

        # Combine them in the correct order
        ordered_params = OrderedDict(
            list(required_params.items()) + list(optional_params.items())
        )

        return MethodDefinition.reorder_params(params=ordered_params, var_kw=var_kw)

    @staticmethod
    def add_field_custom_annotations(
        od: OrderedDict[str, Parameter], model_name: str | None = None
    ):
        """将字段自定义描述和选择作为注释添加到参数签名中。"""
        if not model_name:
            return

        provider_interface = ProviderInterface()

        # Get fields from standard model
        try:
            available_fields = provider_interface.params[model_name][
                "standard"
            ].__dataclass_fields__
            extra_fields = provider_interface.params[model_name][
                "extra"
            ].__dataclass_fields__
        except (KeyError, AttributeError):
            return

        # Combined fields
        all_fields: dict = {}
        all_fields.update(available_fields)
        all_fields.update(extra_fields)

        for param, value in od.items():
            if param not in all_fields:
                continue

            field_default = all_fields[param].default
            extra = MethodDefinition.get_extra(all_fields[param])
            choices = getattr(all_fields[param], "json_schema_extra", {}).get(
                "choices", []
            ) or extra.get("choices", [])
            description = getattr(field_default, "description", "")

            # Handle provider-specific choices and add them to the description
            provider_specific: dict = {}
            for provider, provider_info in extra.items():
                if isinstance(provider_info, dict) and "choices" in provider_info:
                    provider_specific[provider] = provider_info["choices"]

            # Add provider-specific choices to description
            if provider_specific:
                # Add each provider's choices on a new line
                for provider, provider_choices in provider_specific.items():
                    if provider_choices:
                        choices_str = ", ".join(f"'{c}'" for c in provider_choices)
                        description += f"\nChoices for {provider}: {choices_str}"

            # Handle multiple_items_allowed
            multiple_items_providers: list = []
            for provider, provider_info in extra.items():
                if (
                    isinstance(provider_info, dict)
                    and provider_info.get("multiple_items_allowed")
                    or (
                        isinstance(provider_info, list)
                        and "multiple_items_allowed" in provider_info
                    )
                ):
                    multiple_items_providers.append(provider)

            if (
                multiple_items_providers
                and "Multiple comma separated items allowed for provider(s)"
                not in description
            ):
                description += f"\nMultiple items supported by: {', '.join(multiple_items_providers)}"

            # Process the field type - if it's a Union of many Literals, simplify to base type
            field_type = all_fields[param].type
            simplified_type = field_type

            # If there are provider-specific choices, try to simplify the type
            if (
                provider_specific
                and hasattr(field_type, "__origin__")
                and field_type.__origin__ is Union
            ):
                # Check if all union members are Literals
                all_literals = True
                for arg in field_type.__args__:
                    if not (hasattr(arg, "__origin__") and arg.__origin__ is Literal):
                        all_literals = False
                        break

                if all_literals:
                    # Find the base type of the literals (usually str or int)
                    literal_types = set()
                    for arg in field_type.__args__:
                        for lit_val in arg.__args__:
                            literal_types.add(type(lit_val))

                    # If all literals are of the same type, use that type
                    if len(literal_types) == 1:
                        simplified_type = next(iter(literal_types))

            # Create field with enhanced description and possibly simplified type
            field_kwargs = {
                "description": description,
            }

            if choices:
                field_kwargs["choices"] = choices

            new_value = value.replace(
                annotation=Annotated[
                    (
                        simplified_type
                        if simplified_type != field_type
                        else value.annotation
                    ),
                    OpenBBField(description=description),
                ],
            )

            od[param] = new_value

    @staticmethod
    def build_func_params(formatted_params: OrderedDict[str, Parameter]) -> str:
        """将函数参数转换为字符串表示形式。"""

        def get_type_repr(type_hint: Any) -> str:
            """获取类型提示的字符串表示形式。"""
            if isinstance(type_hint, type):
                return type_hint.__name__

            s = str(type_hint)
            if s.startswith("typing."):
                s = s[7:]
            return s

        def stringify_param(param: Parameter) -> str:
            """将参数格式化为字符串。"""
            if not (
                isinstance(param.annotation, _AnnotatedAlias)
                and any(
                    isinstance(m, OpenBBField) for m in param.annotation.__metadata__
                )
            ):
                return str(param)

            type_hint = param.annotation.__args__[0]
            type_repr = get_type_repr(type_hint)
            meta = next(
                m for m in param.annotation.__metadata__ if isinstance(m, OpenBBField)
            )
            desc = meta.description
            desc_repr = repr(desc)

            if desc is None:
                desc = ""
            # For function signatures, use shorter max width to prevent line overflow
            max_width = 50

            if len(desc) <= max_width:
                desc_repr = repr(desc)
            else:
                parts = textwrap.wrap(desc, width=max_width)
                # For function signature context, don't add extra indentation
                # The parameter will be properly indented by the calling context
                joined = "\n                    ".join(f"{repr(p)}" for p in parts)
                desc_repr = f"(\n                    {joined}" + "\n                )"

            default_part = ""

            if param.default is not Parameter.empty:
                default_repr = repr(param.default)
                if default_repr == "Ellipsis":
                    default_repr = "None"
                default_part = f" = {default_repr}"
            if (
                "None" in default_part
                and "| None" not in type_repr
                and "Optional" not in type_repr
            ):
                type_repr += " | None"
            final_param = f"""{param.name.strip()}: Annotated[
            {type_repr},
            OpenBBField(
                description={desc_repr}
            )
        ]{default_part}"""

            return final_param

        params_list = [stringify_param(p) for p in formatted_params.values()]
        func_params = ",\n        ".join(params_list)

        func_params = func_params.replace("NoneType", "None")
        func_params = func_params.replace(
            "pandas.core.frame.DataFrame", "pandas.DataFrame"
        )
        func_params = func_params.replace(
            "openbb_core.provider.abstract.data.Data", "Data"
        )
        func_params = func_params.replace("ForwardRef('Data')", "Data")
        func_params = func_params.replace("ForwardRef('DataFrame')", "DataFrame")
        func_params = func_params.replace("ForwardRef('Series')", "Series")
        func_params = func_params.replace("ForwardRef('ndarray')", "ndarray")
        func_params = func_params.replace("Dict", "dict").replace("List", "list")
        func_params = func_params.replace("typing.", "")

        return func_params

    @staticmethod
    def build_func_returns(return_type: type) -> str:
        """构建函数返回值。"""
        if return_type == _empty:
            func_returns = "Any"
        elif isinstance(return_type, str):
            func_returns = f"ForwardRef('{return_type}')"
        elif isclass(return_type) and issubclass(return_type, OBBject):
            func_returns = "OBBject"
        else:
            func_returns = return_type.__name__ if return_type else Any  # type: ignore

        return func_returns  # type: ignore

    @staticmethod
    def build_command_method_signature(
        func_name: str,
        formatted_params: OrderedDict[str, Parameter],
        return_type: type,
        path: str,
        model_name: str | None = None,
    ) -> str:
        """构建命令方法签名。"""

        MethodDefinition.add_field_custom_annotations(
            od=formatted_params, model_name=model_name
        )  # this modified `od` in place
        func_params = MethodDefinition.build_func_params(formatted_params)
        func_returns = MethodDefinition.build_func_returns(return_type)

        args = (
            '(config={"arbitrary_types_allowed": True})'
            if "DataFrame" in func_params
            or "Series" in func_params
            or "ndarray" in func_params
            else ""
        )

        code = ""
        deprecated = ""

        if MethodDefinition.is_deprecated_function(path):
            deprecation_message = MethodDefinition.get_deprecation_message(path)
            deprecation_type_class = type(deprecation_message.metadata).__name__  # type: ignore

            deprecated = "\n    @deprecated("
            deprecated += f'\n        "{deprecation_message}",'
            deprecated += f"\n        category={deprecation_type_class},"
            deprecated += "\n    )"

        code += "\n    @exception_handler"
        code += f"\n    @validate{args}"
        code += deprecated
        code += f"\n    def {func_name}("
        code += f"\n        self,\n        {func_params}\n    ) -> {func_returns}:\n"

        return code

    @staticmethod
    def build_command_method_doc(
        path: str,
        func: Callable,
        formatted_params: OrderedDict[str, Parameter],
        model_name: str | None = None,
        examples: list[Example] | None = None,
    ):
        """构建命令方法文档字符串。"""
        doc = func.__doc__
        doc = DocstringGenerator.generate(
            path=path,
            func=func,
            formatted_params=formatted_params,
            model_name=model_name,
            examples=examples,
        )
        if doc:
            indent = create_indent(2)
            lines = doc.splitlines(True)
            cleaned_lines = []
            for line in lines:
                if line.startswith(indent):
                    cleaned_lines.append(line[len(indent) :])
                else:
                    cleaned_lines.append(line)
            doc = "".join(cleaned_lines)

        code = (
            f'{create_indent(2)}"""{doc}{create_indent(2)}"""  # noqa: E501 # pylint: disable=line-too-long\n\n'
            if doc
            else ""
        )

        return code

    @staticmethod
    def build_command_method_body(
        path: str,
        func: Callable,
        formatted_params: OrderedDict[str, Parameter] | None = None,
    ):
        """构建命令方法实现。"""
        if formatted_params is None:
            formatted_params = OrderedDict()

        sig = signature(func)
        parameter_map = dict(sig.parameters)
        parameter_map.pop("cc", None)

        # Extract dependencies without disrupting other code paths
        dependency_calls: list = []
        dependency_names = set()

        seen_router_dependency_funcs: set = set()
        for dependency in PathHandler.get_router_dependencies(path):
            dependency_func = getattr(dependency, "dependency", None)
            if (
                callable(dependency_func)
                and dependency_func not in seen_router_dependency_funcs
                and MethodDefinition._is_safe_dependency(dependency_func)
            ):
                dependency_identifier = MethodDefinition._dependency_identifier(
                    dependency_func
                )
                dependency_calls.append(
                    f"        {dependency_identifier} = {dependency_func.__name__}()"
                )
                dependency_calls.append(
                    f"        kwargs['{dependency_identifier}'] = {dependency_identifier}"
                )
                seen_router_dependency_funcs.add(dependency_func)

        # Process dependencies
        for name, param in parameter_map.items():
            if isinstance(param.annotation, _AnnotatedAlias):
                for meta in param.annotation.__metadata__:
                    if hasattr(meta, "dependency") and meta.dependency is not None:
                        dependency_func = meta.dependency

                        if not MethodDefinition._is_safe_dependency(dependency_func):
                            continue

                        func_name = dependency_func.__name__
                        dependency_calls.append(f"        {name} = {func_name}()")
                        dependency_names.add(name)

        code = ""

        if dependency_calls:
            code += "\n".join(dependency_calls) + "\n\n"

        if CHARTING_INSTALLED and path.replace("/", "_")[1:] in Charting.functions():
            parameter_map["chart"] = Parameter(
                name="chart",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=bool,
                default=False,
            )

        if MethodDefinition.is_deprecated_function(path):
            deprecation_message = MethodDefinition.get_deprecation_message(path)
            code += "        simplefilter('always', DeprecationWarning)\n"
            code += f"""        warn("{deprecation_message}", category=DeprecationWarning, stacklevel=2)\n\n"""

        info = {}

        code += "        return self._run(\n"
        code += f"""            "{path}",\n"""
        code += "            **filter_inputs(\n"

        # Check if we already have a kwargs parameter (VAR_KEYWORD) in formatted_params
        has_kwargs = any(
            param.kind == Parameter.VAR_KEYWORD for param in formatted_params.values()
        )
        has_extra_params = False

        for name, param in parameter_map.items():
            if name == "extra_params":
                has_extra_params = True
                fields = (
                    param.annotation.__args__[0].__dataclass_fields__
                    if hasattr(param.annotation, "__args__")
                    else param.annotation
                )
                values = {k: k for k in fields}
                for k in values:
                    if extra := MethodDefinition.get_extra(fields[k]):
                        info[k] = extra
                code += f"                {name}=kwargs,\n"
            elif name == "provider_choices":
                field = param.annotation.__args__[0].__dataclass_fields__["provider"]
                available = field.type.__args__
                cmd = path.strip("/").replace("/", ".")
                code += "                provider_choices={\n"
                code += '                    "provider": self._get_provider(\n'
                code += "                        provider,\n"
                code += f'                        "{cmd}",\n'
                code += f"                        {available},\n"
                code += "                    )\n"
                code += "                },\n"
            elif MethodDefinition.is_annotated_dc(param.annotation):
                fields = param.annotation.__args__[0].__dataclass_fields__
                values = {k: k for k in fields}
                code += f"                {name}={{\n"
                for k, v in values.items():
                    code += f'                    "{k}": {v},\n'
                    if extra := MethodDefinition.get_extra(fields[k]):
                        info[k] = extra
                code += "                },\n"
            elif (
                isinstance(param.annotation, _AnnotatedAlias)
                and (
                    hasattr(param.annotation.__args__[0], "model_fields")
                    or hasattr(param.annotation.__args__[0], "__pydantic_fields__")
                )
                and not MethodDefinition.is_data_processing_function(path)
            ):
                has_depends = any(
                    hasattr(meta, "dependency")
                    for meta in param.annotation.__metadata__
                )
                if not has_depends:
                    model = param.annotation.__args__[0]
                    fields = getattr(
                        model,
                        "model_fields",
                        getattr(model, "__pydantic_fields__", {}),
                    )
                    values = {k: k for k in fields}
                    code += f"                {name}={{\n"
                    for k, v in values.items():
                        code += f'                    "{k}": {v},\n'
                    code += "                },\n"
                else:
                    code += f"                {name}={name},\n"
            elif name != "kwargs":
                code += f"                {name}={name},\n"

        if info:
            code += f"                info={info},\n"

        if MethodDefinition.is_data_processing_function(path):
            code += "                data_processing=True,\n"

        # Add kwargs parameter
        if has_kwargs and not has_extra_params:
            code += "                **kwargs,\n"

        code += "            )\n"
        code += "        )\n"

        return code

    @classmethod
    def get_expanded_type(
        cls,
        field_name: str,
        extra: dict | None = None,
        original_type: type | None = None,
    ) -> object:
        """展开原始字段类型。"""
        if extra and any(
            (
                v.get("multiple_items_allowed")
                if isinstance(v, dict)
                # For backwards compatibility, before this was a list
                else "multiple_items_allowed" in v
            )
            for v in extra.values()
        ):
            if original_type is None:
                raise ValueError(
                    "multiple_items_allowed requires the original type to be specified."
                )
            return list[original_type]  # type: ignore
        return cls.TYPE_EXPANSION.get(field_name, ...)

    @classmethod
    def build_command_method(
        cls,
        path: str,
        func: Callable,
        model_name: str | None = None,
        examples: list[Example] | None = None,
    ) -> str:
        """构建命令方法。"""
        path_parts = [p for p in path.split("/") if p and not p.startswith("{")]
        func_name = path_parts[-1] if path_parts else func.__name__
        sig = signature(func)
        parameter_map = dict(sig.parameters)
        # Get the function source code and extract filter_inputs parameters
        additional_params = {}

        if hasattr(func, "__code__"):
            try:
                func_source = inspect.getsource(func)

                # First, find the filter_inputs block to extract parameter names
                filter_inputs_match = re.search(
                    r"filter_inputs\(\s*(.*?)\s*\)", func_source, re.DOTALL
                )
                if filter_inputs_match:
                    filter_inputs_text = filter_inputs_match.group(1)
                    filter_params = re.findall(r"(\w+)=(\w+)", filter_inputs_text)

                    # Then look for parameter definitions in function body
                    # Find parameters defined with types in comments or actual code
                    param_defs = re.findall(
                        r"(\w+)\s*:\s*(\w+)(?:\s*=\s*([^,\n]+))?", func_source
                    )
                    param_dict = {
                        name: (typ, default) for name, typ, default in param_defs
                    }

                    # Add missing parameters preserving types when available
                    for param_name, param_value in filter_params:
                        if (
                            param_name != param_value
                            and param_value not in parameter_map
                            and param_value not in ["True", "False", "None"]
                        ):
                            # Use type from param_dict if available, otherwise Any
                            if param_value in param_dict:
                                param_type = param_dict[param_value][0]
                                try:
                                    # Try to evaluate the type
                                    annotation = (
                                        eval(  # noqa: S307  # pylint: disable=eval-used
                                            param_type
                                        )
                                    )
                                except (NameError, SyntaxError):
                                    annotation = Any

                                # Get default if available
                                default_str = param_dict[param_value][1]
                                try:
                                    default = (
                                        eval(  # noqa: S307  # pylint: disable=eval-used
                                            default_str
                                        )
                                        if default_str
                                        else None
                                    )
                                except (NameError, SyntaxError):
                                    default = None
                            else:
                                annotation = Any
                                default = None

                            # Add parameter with preserved type/default
                            additional_params[param_value] = Parameter(
                                name=param_value,
                                kind=Parameter.POSITIONAL_OR_KEYWORD,
                                annotation=annotation,
                                default=default,
                            )
            except (OSError, TypeError):
                pass

        # Add missing parameters to parameter_map
        for name, param in additional_params.items():
            if name not in parameter_map:
                parameter_map[name] = param

        formatted_params = cls.format_params(path=path, parameter_map=parameter_map)

        has_var_kwargs = any(
            param.kind == Parameter.VAR_KEYWORD for param in formatted_params.values()
        )

        # If not, add **kwargs to formatted_params
        if not has_var_kwargs:
            formatted_params["kwargs"] = Parameter(
                name="kwargs",
                kind=Parameter.VAR_KEYWORD,
                annotation=Any,
                default=Parameter.empty,
            )

        code = cls.build_command_method_signature(
            func_name=func_name,
            formatted_params=formatted_params,
            return_type=sig.return_annotation,
            path=path,
            model_name=model_name,
        )
        code += cls.build_command_method_doc(
            path=path,
            func=func,
            formatted_params=formatted_params,
            model_name=model_name,
            examples=examples,
        )

        code += cls.build_command_method_body(
            path=path, func=func, formatted_params=formatted_params
        )

        return code


class DocstringGenerator:
    """动态生成命令的文档字符串。"""

    provider_interface = ProviderInterface()

    @staticmethod
    def get_field_type(
        field_type: Any,
        is_required: bool,
        target: Literal["docstring", "website"] = "docstring",
    ) -> str:
        """获取已定义的 Pydantic 字段的隐式数据类型。
        Parameters
        ----------
        field_type : Any
            包含字段类型的 Typing 对象。
        is_required : bool
            指示字段是否必需的标志。
        target : Literal["docstring", "website"]
            返回类型的目标。默认为 "docstring"。
        Returns
        -------
        str
            字段类型的字符串表示形式。
        """
        is_optional = not is_required

        try:
            _type = field_type

            if "BeforeValidator" in str(_type):
                _type = "Optional[int]" if is_optional else "int"  # type: ignore

            origin = get_origin(_type)
            if origin is Union:
                args = get_args(_type)
                type_names = []
                has_none = False
                for arg in args:
                    if arg is type(None):
                        has_none = True
                        continue
                    if get_origin(arg) is Literal:
                        continue
                    type_name = str(arg)
                    if hasattr(arg, "__name__"):
                        type_name = arg.__name__
                    type_name = (
                        type_name.replace("typing.", "")
                        .replace("pydantic.types.", "")
                        .replace("datetime.datetime", "datetime")
                        .replace("datetime.date", "date")
                    )
                    if "openbb_" in type_name:
                        type_name = type_name.rsplit(".", 1)[-1]
                    if type_name != "NoneType":
                        type_names.append(type_name)

                unique_types = sorted(list(set(type_names)))
                if has_none:
                    unique_types.append("None")
                _type = " | ".join(unique_types)
            else:
                _type = (
                    str(_type)
                    .replace("<class '", "")
                    .replace("'>", "")
                    .replace("typing.", "")
                    .replace("pydantic.types.", "")
                    .replace("datetime.datetime", "datetime")
                    .replace("datetime.date", "date")
                    .replace("NoneType", "None")
                    .replace(", None", "")
                )

            if "openbb_" in str(_type):
                _type = (
                    str(_type).split(".", maxsplit=1)[0].split("openbb_")[0]
                    + str(_type).rsplit(".", maxsplit=1)[-1]
                )

            _type = (
                f"Optional[{_type}]"
                if is_optional
                and "Optional" not in str(_type)
                and " | " not in str(_type)
                else _type
            )

            if target == "website":
                _type = re.sub(r"Optional\[(.*)\]", r"\1", _type)

            return _type

        except TypeError:
            return str(field_type)

    @staticmethod
    def get_OBBject_description(
        results_type: str,
        providers: str | None,
    ) -> str:
        """获取命令输出描述。"""
        available_providers = providers or "Optional[str]"
        indent = 2

        obbject_description = (
            f"{create_indent(indent)}OBBject\n"
            f"{create_indent(indent + 1)}results : {results_type}\n"
            f"{create_indent(indent + 2)}可序列化的结果。\n"
            f"{create_indent(indent + 1)}provider : {available_providers}\n"
            f"{create_indent(indent + 2)}提供者名称。\n"
            f"{create_indent(indent + 1)}warnings : Optional[list[Warning_]]\n"
            f"{create_indent(indent + 2)}警告列表。\n"
            f"{create_indent(indent + 1)}chart : Optional[Chart]\n"
            f"{create_indent(indent + 2)}图表对象。\n"
            f"{create_indent(indent + 1)}extra : dict[str, Any]\n"
            f"{create_indent(indent + 2)}额外信息。\n"
        )

        obbject_description = obbject_description.replace("NoneType", "None")

        return obbject_description

    @staticmethod
    def build_examples(
        func_path: str,
        param_types: dict[str, type],
        examples: list[Example] | None,
        target: Literal["docstring", "website"] = "docstring",
    ) -> str:
        """从示例中获取示例部分。"""
        if examples:
            if target == "docstring":
                prompt = ">>> "
                indent = create_indent(2)
            else:
                prompt = "\n```python\n"
                indent = create_indent(0)

            doc = f"{indent}Examples\n"
            doc += f"{indent}--------\n"
            doc += f"{indent}{prompt}from openbb import obb\n"

            for e in examples:
                doc += e.to_python(
                    func_path=func_path,
                    param_types=param_types,
                    indentation=indent,
                    prompt=">>> " if target == "docstring" else "",
                )
            return doc if target == "docstring" else doc + "```\n\n"
        return ""

    @classmethod
    def generate_model_docstring(  # noqa: PLR0912, PLR0917
        cls,
        model_name: str,
        summary: str,
        explicit_params: dict[str, Parameter],
        kwarg_params: dict,
        returns: dict[str, FieldInfo],
        results_type: str,
        sections: list[str],
    ) -> str:
        """为模型创建文档字符串。"""
        docstring: str = "\n"

        def format_type(type_: str, char_limit: int | None = None) -> str:
            """在文档字符串中格式化类型。"""
            type_str = str(type_)

            # Apply the standard formatting first
            type_str = (
                type_str.replace("<class '", "")
                .replace("'>", "")
                .replace("typing.", "")
                .replace("pydantic.types.", "")
                .replace("datetime.date", "date")
                .replace("datetime.datetime", "datetime")
                .replace("NoneType", "None")
            )

            # Convert Optional[X] to X | None
            optional_pattern = r"Optional\[(.+?)\]"
            optional_match = re.search(optional_pattern, type_str)
            if optional_match:
                inner = optional_match.group(1)
                type_str = type_str.replace(f"Optional[{inner}]", f"{inner} | None")

            # Convert Union[X, Y, ...] to X | Y | ... format
            union_pattern = r"Union\[(.+)\]"
            union_match = re.search(union_pattern, type_str)
            if union_match:
                inner = union_match.group(1)
                # Split by comma, but be careful with nested types like list[str]
                parts = []
                depth = 0
                current = ""
                for char in inner:
                    if char == "[":
                        depth += 1
                    elif char == "]":
                        depth -= 1
                    elif char == "," and depth == 0:
                        parts.append(current.strip())
                        current = ""
                        continue
                    current += char
                if current.strip():
                    parts.append(current.strip())
                # Remove None and NoneType from parts, we'll add | None at the end if needed
                has_none = any(p in ("None", "NoneType") for p in parts)
                parts = [p for p in parts if p not in ("None", "NoneType")]
                type_str = " | ".join(parts)
                if has_none:
                    type_str += " | None"

            # Simplify Literal[...] to str (choices shown in description)
            # Handle Literal[...] | None -> str | None
            if "Literal[" in type_str:
                # Check if there's | None at the end
                has_none = type_str.endswith(" | None")
                # Replace any Literal[...] with str
                type_str = re.sub(r"Literal\[[^\]]+\]", "str", type_str)
                # Ensure | None is preserved
                if has_none and not type_str.endswith(" | None"):
                    type_str += " | None"

            # Clean up ", None" that might be left over
            type_str = type_str.replace(", None", "")

            # Deduplicate types while preserving order (e.g. str | str | str -> str)
            if " | " in type_str:
                parts = [p.strip() for p in type_str.split(" | ")]
                has_none = "None" in parts
                # Remove None for now, deduplicate, then add back
                parts = [p for p in parts if p != "None"]
                # Deduplicate while preserving order
                seen: set[str] = set()
                unique_parts = []
                for p in parts:
                    if p not in seen:
                        seen.add(p)
                        unique_parts.append(p)
                type_str = " | ".join(unique_parts)
                if has_none:
                    type_str += " | None"

            # Apply char_limit if specified (simple truncation with bracket balancing)
            if char_limit and len(type_str) > char_limit:
                truncated = type_str[:char_limit]
                open_brackets = truncated.count("[") - truncated.count("]")
                if open_brackets > 0:
                    truncated += "]" * open_brackets
                type_str = truncated

            return type_str

        def format_schema_description(description: str) -> str:
            """格式化文档字符串中的解释。"""
            description = (
                description.replace("\n", f"\n{create_indent(2)}")
                if "\n        " not in description
                else description
            )

            return description

        def format_description(description: str) -> str:
            """格式化文档字符串中的描述，并为提供商选择提供适当的缩进。"""
            # Base indent for description content (called with create_indent(3) prefix)
            base_indent = create_indent(3)  # 12 spaces

            # Extract "Choices for provider: ..." into a dict keyed by provider
            provider_choices: dict[str, str] = {}
            main_description = description
            multi_items_text = ""

            if "\nChoices for " in description:
                choices_idx = description.index("\nChoices for ")
                main_description = description[:choices_idx]
                choices_text = description[choices_idx:]

                # Parse each "Choices for provider: values" line
                # Handle multi-line choices where continuation lines don't have "Choices for" prefix
                current_provider = None
                current_choices = []

                for ln in choices_text.strip().split("\n"):
                    line = ln.strip()

                    # Check if this is the "Multiple comma separated" line
                    if line.startswith("Multiple comma separated items allowed"):
                        # Save current provider's choices first
                        if current_provider and current_choices:
                            provider_choices[current_provider] = " ".join(
                                current_choices
                            )
                            current_provider = None
                            current_choices = []
                        multi_items_text = line
                        continue

                    if line.startswith("Choices for "):
                        # Save previous provider's choices if any
                        if current_provider and current_choices:
                            provider_choices[current_provider] = " ".join(
                                current_choices
                            )

                        # Extract provider name and choices
                        rest = line[len("Choices for ") :]
                        if ": " in rest:
                            prov, choices = rest.split(": ", 1)
                            current_provider = prov.strip()
                            current_choices = [choices.strip()]
                    elif current_provider and line:
                        # This is a continuation line for the current provider's choices
                        current_choices.append(line)

                # Save the last provider's choices
                if current_provider and current_choices:
                    provider_choices[current_provider] = " ".join(current_choices)

            # Extract multiple items text from main_description if not already found
            if not multi_items_text:
                multi_pattern = (
                    r"\nMultiple comma separated items allowed for provider\(s\): [^.]+"
                )
                multi_match = re.search(multi_pattern, main_description)
                if multi_match:
                    multi_items_text = multi_match.group().strip()
                    main_description = re.sub(multi_pattern, "", main_description)

            # Handle semicolon-separated provider descriptions
            if ";" in main_description and "(provider:" in main_description:
                parts = main_description.split(";")
                provider_sections = []

                # Extract provider tag pattern
                provider_pattern = re.compile(r"\s*\(provider:\s*([^)]+)\)")

                for part in parts:
                    p = part.strip()
                    match = provider_pattern.search(p)
                    if match:
                        provider_name = match.group(1).strip()
                        content = provider_pattern.sub("", p).strip()
                        provider_sections.append((provider_name, content))
                    elif p:
                        provider_sections.append((None, p))

                if provider_sections:
                    # Find common base description
                    provider_contents = [
                        (name, content)
                        for name, content in provider_sections
                        if name is not None
                    ]
                    base_description = ""

                    if len(provider_contents) >= 2:
                        first_sentences = []
                        for _, content in provider_contents:
                            if "." in content:
                                first_sent = content.split(".", 1)[0].strip()
                                first_sentences.append(first_sent)
                            else:
                                first_sentences.append(content)

                        if first_sentences and all(
                            s == first_sentences[0] for s in first_sentences
                        ):
                            base_description = first_sentences[0] + "."

                    # Check for base description without provider tag
                    base_parts = [
                        content
                        for name, content in provider_sections
                        if name is None and "Choices" not in content
                    ]
                    if base_parts and not base_description:
                        base_description = base_parts[0]

                    # Build formatted output
                    formatted_lines = []

                    if base_description:
                        formatted_lines.append(base_description)
                        formatted_lines.append("")

                    for provider_name, content in provider_sections:
                        if provider_name and content:
                            if base_description:
                                base_clean = base_description.rstrip(".")
                                if content.startswith(base_clean):
                                    content = content[len(base_clean) :].strip()  # noqa
                                    if content.startswith("."):
                                        content = content[1:].strip()  # noqa

                            if not content:
                                continue

                            formatted_lines.append(f"(provider: {provider_name})")
                            for line in content.split("\n"):
                                new_line = line.strip()
                                if new_line:
                                    formatted_lines.append(f"    {new_line}")

                            # Add choices for this provider inside its section
                            if provider_name in provider_choices:
                                formatted_lines.append(
                                    f"    Choices: {provider_choices[provider_name]}"
                                )

                            formatted_lines.append("")

                    while formatted_lines and formatted_lines[-1] == "":
                        formatted_lines.pop()

                    # Join lines
                    if formatted_lines:
                        result = formatted_lines[0]
                        for line in formatted_lines[1:]:
                            if line:
                                result += f"\n{base_indent}{line}"
                            else:
                                result += "\n"
                        main_description = result

            # If no provider sections but we have choices, add them at the end
            elif provider_choices:
                for prov, choices in provider_choices.items():
                    main_description += f"\n{base_indent}Choices for {prov}: {choices}"

            # Add multiple items text at the end
            if multi_items_text:
                main_description += f"\n{base_indent}{multi_items_text}"

            return main_description

        def get_param_info(parameter: Parameter | None) -> tuple[str, str]:
            """获取参数信息。"""
            if not parameter:
                return "", ""
            annotation = getattr(parameter, "_annotation", None)
            if isinstance(annotation, _AnnotatedAlias):
                args = getattr(annotation, "__args__", []) if annotation else []
                p_type = args[0] if args else None
            else:
                p_type = annotation
            type_ = (
                getattr(p_type, "__name__", "") if inspect.isclass(p_type) else p_type
            )
            metadata = getattr(annotation, "__metadata__", [])
            description = getattr(metadata[0], "description", "") if metadata else ""

            return type_, description  # type: ignore

        provider_param: Parameter | dict = {}
        chart_param: Parameter | dict = {}

        # Description summary
        if "description" in sections:
            docstring = summary.strip("\n").replace("\n    ", f"\n{create_indent(2)}")
            docstring += "\n\n"
        else:
            docstring += "\n\n"

        if "parameters" in sections:
            provider_param = explicit_params.pop("provider", {})  # type: ignore
            chart_param = explicit_params.pop("chart", {})  # type: ignore
            docstring += f"{create_indent(2)}Parameters\n"
            docstring += f"{create_indent(2)}----------\n"

            if provider_param:
                _, description = get_param_info(provider_param)  # type: ignore
                provider_param._annotation = str  # type: ignore  # pylint: disable=protected-access
                docstring += f"{create_indent(2)}provider : str\n"
                docstring += f"{create_indent(3)}{format_description(description)}\n"

            # Explicit parameters
            for param_name, param in explicit_params.items():
                type_, description = get_param_info(param)
                type_str = format_type(str(type_), char_limit=86)
                docstring += f"{create_indent(2)}{param_name} : {type_str}\n"
                docstring += f"{create_indent(3)}{format_description(description)}\n"

            # Kwargs
            for param_name, param in kwarg_params.items():
                type_, description = get_param_info(param)
                p_type = getattr(param, "type", "")
                type_ = (
                    getattr(p_type, "__name__", "")
                    if inspect.isclass(p_type)
                    else p_type
                )

                # Extract Literal values before formatting the type
                literal_choices: list = []
                type_str = str(type_)
                if "Literal[" in type_str:
                    # Extract values from Literal[...]
                    literal_match = re.search(r"Literal\[([^\]]+)\]", type_str)
                    if literal_match:
                        literal_content = literal_match.group(1)
                        # Parse the literal values (they're quoted strings)
                        literal_choices = re.findall(r"'([^']+)'", literal_content)

                type_ = format_type(type_)
                if "NoneType" in str(type_):
                    type_ = type_.replace(", NoneType", "")

                default = getattr(param, "default", "")
                description = getattr(default, "description", "")

                # If empty description, check for OpenBBField annotations in parameter's annotation
                if not description and hasattr(param, "annotation"):
                    param_annotation = getattr(param, "annotation", None)
                    # Check if annotation is an Annotated type
                    if (
                        hasattr(param_annotation, "__origin__") and param_annotation.__origin__ is Annotated  # type: ignore
                    ):
                        # Extract metadata from annotation
                        metadata = getattr(param_annotation, "__metadata__", [])
                        for meta in metadata:
                            # Look for OpenBBField with description
                            if hasattr(meta, "description") and meta.description:
                                description = meta.description
                                break

                # If still no description but param default is a Query object, extract from there
                if not description and hasattr(param, "default"):
                    param_default = getattr(param, "default")
                    if (
                        hasattr(param_default, "__class__")
                        and "Query" in param_default.__class__.__name__
                    ):
                        description = getattr(param_default, "description", "") or ""

                # Initialize provider_choices and multi_item_providers for this parameter
                provider_choices: dict = {}
                multi_item_providers: list = []

                # Extract choices and multiple_items_allowed from json_schema_extra
                # For kwarg_params (dataclass fields), json_schema_extra is on param.default (Query object)
                # For other params (Pydantic FieldInfo), it may be on param itself
                param_default = getattr(param, "default", None)
                json_extra = getattr(param_default, "json_schema_extra", None)
                if not json_extra:
                    json_extra = getattr(param, "json_schema_extra", None)
                if json_extra and isinstance(json_extra, dict):
                    for prov, prov_info in json_extra.items():
                        if isinstance(prov_info, dict):
                            if "choices" in prov_info:
                                provider_choices[prov] = prov_info["choices"]
                            if prov_info.get("multiple_items_allowed"):
                                multi_item_providers.append(prov)

                # If we have Literal choices from the type and no choices from json_schema_extra,
                # extract providers from the description and add choices for them
                if literal_choices and not provider_choices:
                    # Look for (provider: xxx) or (provider: xxx, yyy) in description
                    provider_match = re.search(r"\(provider:\s*([^)]+)\)", description)
                    if provider_match:
                        providers_text = provider_match.group(1)
                        providers_from_desc = [
                            p.strip() for p in providers_text.split(",")
                        ]
                        for prov in providers_from_desc:
                            if prov and prov not in provider_choices:
                                provider_choices[prov] = literal_choices

                # Extract provider-specific choices directly from the provider interface
                if (
                    not isinstance(p_type, str)
                    and hasattr(p_type, "__origin__")
                    and p_type.__origin__ is Union
                ):

                    # Get the list of providers for this model directly from provider_interface.model_providers
                    try:
                        model_providers = cls.provider_interface.model_providers.get(
                            model_name
                        )
                        if model_providers:
                            provider_field = model_providers.__dataclass_fields__.get(
                                "provider"
                            )
                            providers = (
                                list(provider_field.type.__args__)
                                if provider_field
                                else []
                            )
                        else:
                            providers = []

                        # For each provider, extract their specific choices for this parameter from the map
                        for provider in providers:
                            if provider == "openbb":
                                continue
                            try:
                                # Directly get provider field info from the map structure
                                provider_field_info = (
                                    cls.provider_interface.map.get(model_name, {})
                                    .get(provider, {})
                                    .get("QueryParams", {})
                                    .get("fields", {})
                                    .get(param_name)
                                )

                                # If the field exists and has a Literal annotation
                                if (
                                    provider_field_info
                                    and hasattr(provider_field_info, "annotation")
                                    and hasattr(
                                        provider_field_info.annotation, "__origin__"
                                    )
                                    and provider_field_info.annotation.__origin__
                                    is Literal
                                ):
                                    # Extract literal values as provider choices
                                    provider_choices[provider] = list(
                                        provider_field_info.annotation.__args__
                                    )
                            except (KeyError, AttributeError):
                                continue
                    except (AttributeError, KeyError):
                        pass

                # Add provider-specific choices to description
                for provider, choices in provider_choices.items():
                    if choices:
                        # Format choices with word wrapping for readability
                        formatted_choices = []
                        line_length = 0
                        line_limit = 80  # Max line length

                        for i, choice in enumerate(choices):
                            choice_str = f"'{choice}'"

                            # If adding this choice would exceed line limit, start a new line
                            if (
                                line_length > 0
                                and line_length + len(choice_str) + 2 > line_limit
                            ):
                                # End the current line
                                formatted_choices.append("\n")
                                line_length = 0

                            # Add comma and space if not the first choice in the line
                            if i > 0 and line_length > 0:
                                formatted_choices.append(", ")
                                line_length += 2

                            formatted_choices.append(choice_str)
                            line_length += len(choice_str)

                        choices_str = "".join(formatted_choices)
                        description += f"\nChoices for {provider}: {choices_str}"

                # Add multiple items allowed text at the end if applicable
                # But only if it's not already in the description
                if (
                    multi_item_providers
                    and "Multiple comma separated items allowed" not in description
                ):
                    providers_str = ", ".join(sorted(multi_item_providers))
                    description += f"\nMultiple comma separated items allowed for provider(s): {providers_str}."

                docstring += f"{create_indent(2)}{param_name} : {type_}\n"
                docstring += f"{create_indent(3)}{format_description(description)}\n"

            if chart_param:
                _, description = get_param_info(chart_param)  # type: ignore
                docstring += f"{create_indent(2)}chart : bool\n"
                docstring += f"{create_indent(3)}{format_description(description)}\n"

        if "returns" in sections:
            # Returns
            docstring += "\n"
            docstring += f"{create_indent(2)}Returns\n"
            docstring += f"{create_indent(2)}-------\n"
            _providers, _ = get_param_info(explicit_params.get("provider"))
            docstring += cls.get_OBBject_description(results_type, _providers)
            # Schema
            underline = "-" * len(model_name)
            docstring += f"\n{create_indent(2)}{model_name}\n"
            docstring += f"{create_indent(2)}{underline}\n"

            for name, field in returns.items():
                field_type = cls.get_field_type(field.annotation, field.is_required())
                description = getattr(field, "description", "")
                docstring += f"{create_indent(2)}{field.alias or name} : {field_type}\n"
                docstring += f"{create_indent(3)}{format_schema_description(description.strip())}\n"

        return docstring

    # flake8: noqa:PLR0912
    @classmethod
    def generate(  # pylint: disable=too-many-positional-arguments  # noqa: PLR0912
        cls,
        path: str,
        func: Callable,
        formatted_params: OrderedDict[str, Parameter],
        model_name: str | None = None,
        examples: list[Example] | None = None,
    ) -> str | None:
        """Generate the docstring for the function."""
        doc = inspect.getdoc(func) or ""
        param_types = {}
        sections = SystemService().system_settings.python_settings.docstring_sections
        max_length = (
            SystemService().system_settings.python_settings.docstring_max_length
        )
        # Parameters explicit in the function signature
        explicit_params = dict(formatted_params)
        explicit_params.pop("extra_params", None)
        # Map of parameter names to types
        param_types = {k: v.annotation for k, v in explicit_params.items()}

        if model_name:
            params = cls.provider_interface.params.get(model_name, {})
            return_schema = cls.provider_interface.return_schema.get(model_name, None)
            if params and return_schema:
                # Parameters passed as **kwargs
                kwarg_params = params["extra"].__dataclass_fields__
                param_types.update({k: v.type for k, v in kwarg_params.items()})
                # Format the annotation to hide the metadata, tags, etc.
                annotation = func.__annotations__.get("return")
                results_type = (
                    cls._get_repr(
                        cls._get_generic_types(
                            annotation.model_fields["results"].annotation,  # type: ignore[union-attr,arg-type]
                            [],
                        ),
                        model_name,
                    )
                    if isclass(annotation) and issubclass(annotation, OBBject)  # type: ignore[arg-type]
                    else model_name
                )
                doc = cls.generate_model_docstring(
                    model_name=model_name,
                    summary=func.__doc__ or "",
                    explicit_params=explicit_params,
                    kwarg_params=kwarg_params,
                    returns=return_schema.model_fields,
                    results_type=results_type,
                    sections=sections,
                )
                doc += "\n"

                if "examples" in sections:
                    doc += cls.build_examples(
                        path.replace("/", "."),
                        param_types,
                        examples,
                    )
                    doc += "\n"
        else:
            primitive_types = {
                "int",
                "float",
                "str",
                "bool",
                "list",
                "dict",
                "tuple",
                "set",
            }
            type_name: str = ""
            sections = (
                SystemService().system_settings.python_settings.docstring_sections
            )
            doc_has_parameters = bool(
                re.search(r"^\s*Parameters\s*\n[-=~`]{3,}", doc, re.MULTILINE)
            )
            doc_has_returns = bool(
                re.search(r"^\s*Returns\s*\n[-=~`]{3,}", doc, re.MULTILINE)
            )
            doc_has_examples = bool(
                re.search(r"^\s*Examples\s*\n[-=~`]{3,}", doc, re.MULTILINE)
            )
            result_doc = doc.strip("\n")

            if result_doc:
                result_doc += "\n\n"

            if (
                formatted_params
                and "parameters" in sections
                and not doc_has_parameters
                and [p for p_name, p in formatted_params.items() if p_name != "kwargs"]
            ):
                if result_doc and not result_doc.endswith("\n\n"):
                    result_doc = result_doc.rstrip("\n") + "\n\n"
                elif not result_doc:
                    result_doc = "\n\n"

                param_section = "Parameters\n----------\n"

                for param_name, param in formatted_params.items():
                    if param_name == "kwargs":
                        continue

                    annotation = getattr(param, "_annotation", None)

                    if isinstance(annotation, _AnnotatedAlias):
                        p_type = annotation.__args__[0]  # type: ignore
                        metadata = getattr(annotation, "__metadata__", [])
                        description = (
                            getattr(metadata[0], "description", "") if metadata else ""
                        )
                    else:
                        p_type = annotation
                        description = ""

                    type_str = cls.get_field_type(
                        p_type, param.default is Parameter.empty
                    )
                    param_section += f"{create_indent(1)}{param_name} : {type_str}\n"

                    if description and description.strip() != '""':
                        param_section += f"{create_indent(2)}{description}\n"

                result_doc += param_section + "\n"

            if "returns" in sections and not doc_has_returns:
                if result_doc and not result_doc.endswith("\n\n"):
                    result_doc = result_doc.rstrip("\n") + "\n\n"

                returns_section = "Returns\n-------\n"
                sig = inspect.signature(func)
                return_annotation = sig.return_annotation

                if (
                    return_annotation
                    and return_annotation
                    != inspect._empty  # pylint: disable=protected-access
                ):
                    if hasattr(return_annotation, "__name__"):
                        type_name = return_annotation.__name__
                    else:
                        type_name = str(return_annotation)

                    type_name = (
                        type_name.replace("typing.", "")
                        .replace("typing_extensions.", "")
                        .replace("<class '", "")
                        .replace("'>", "")
                        .replace("OBBject[T]", "OBBject")
                    )

                    returns_section += f"{type_name}\n"
                    is_primitive = type_name.lower() in primitive_types

                    if not is_primitive:
                        try:
                            if hasattr(return_annotation, "model_fields"):
                                fields = return_annotation.model_fields

                                for field_name, field in fields.items():
                                    field_type = cls.get_field_type(
                                        field.annotation, field.is_required
                                    )
                                    description = (
                                        field.description.replace('"', "'")
                                        if field.description
                                        else ""
                                    )

                                    if type_name.startswith("OBBject"):
                                        if field_name != "id":
                                            returns_section += "\n"

                                        returns_section += f"{create_indent(2)}{field_name.strip()} : {field_type}"
                                    else:
                                        returns_section += f"{create_indent(2)}{field_name} : {field_type}\n"
                                    if description:
                                        returns_section += (
                                            f"\n{create_indent(3)}{description}"
                                        )

                        except (AttributeError, TypeError):
                            pass
                else:
                    returns_section += "Any\n"

                result_doc += returns_section + "\n"
                result_doc = result_doc.replace("\n    ", f"\n{create_indent(2)}")

            doc = result_doc.rstrip()

            # Check response type for OBBject types to extract inner type
            # Expand the docstring with the schema fields like in model-based commands
            if type_name and "OBBject" in type_name:
                type_str = str(return_annotation).replace("[T]", "")
                match = re.search(r"OBBject\[(.*)\]", type_str)
                inner = match.group(1) if match else ""
                # Extract from list[Type] or dict[str, Type]
                type_match = re.search(r"\[([^\[\]]+)\]$", inner)
                extracted_type = type_match.group(1) if type_match else inner

                if extracted_type and extracted_type.lower() not in primitive_types:
                    route_map = PathHandler.build_route_map()
                    paths = ReferenceGenerator.get_paths(route_map)
                    route_path = paths.get(path, {}).get("data", {}).get("standard", [])

                    if route_path:
                        if doc and not doc.endswith("\n\n"):
                            doc += "\n\n"
                        doc += f"{extracted_type}\n"
                        doc += f"{'-' * len(extracted_type)}\n"

                        for field in route_path:
                            field_name = field.get("name", "")
                            field_type = field.get("type", "Any")
                            field_description = field.get("description", "")
                            doc += f"{create_indent(2)}{field_name} : {field_type}\n"
                            if field_description:
                                doc += f"{create_indent(3)}{field_description}\n"

                        doc += "\n"

            if "examples" in sections and not doc_has_examples:
                if doc and not doc.endswith("\n\n"):
                    doc += "\n\n"
                doc += cls.build_examples(
                    path.replace("/", "."),
                    param_types,
                    examples,
                )
                doc += "\n"

        if (  # pylint: disable=chained-comparison
            max_length and len(doc) > max_length and max_length > 3
        ):
            doc = doc[: max_length - 3] + "..."
        return doc

    @classmethod
    def _get_generic_types(cls, type_: type, items: list) -> list[str]:
        """递归地解包泛型类型。

        Parameters
        ----------
        type_ : type
            要解包的类型。
        items : list
            用于存储解包类型的列表。

        Returns
        -------
        List[str]
            解包后的类型名称列表。

        Examples
        --------
        Union[List[str], Dict[str, str], Tuple[str]] -> ["List", "Dict", "Tuple"]
        """
        if hasattr(type_, "__args__"):
            origin = get_origin(type_)
            # pylint: disable=unidiomatic-typecheck
            if (
                type(origin) is type
                and origin is not Annotated
                and (name := getattr(type_, "_name", getattr(type_, "__name__", None)))
            ):
                items.append(name)
            func = partial(cls._get_generic_types, items=items)
            set().union(*map(func, type_.__args__), items)  # type: ignore
        return items

    @staticmethod
    def _get_repr(items: list[str], model: str) -> str:
        """获取带有模型名称的类型列表的字符串表示形式。

        Parameters
        ----------
        items : List[str]
            类型名称列表。
        model : str
            用于访问模型提供程序的模型名称。

        Returns
        -------
        str
            解包后的类型列表的字符串表示形式。

        Examples
        --------
        [List, Dict, Tuple[str]] -> "Union[List[str], Dict[str, str], Tuple[str]]"
        """
        if s := [
            f"{i}[str, {model}]" if i.lower() == "dict" else f"{i}[{model}]"
            for i in items
        ]:
            return f"{' | '.join(s)}" if len(s) > 1 else s[0]
        return model


class PathHandler:
    """处理平台的路径。"""

    @staticmethod
    def get_router_dependencies(path: str) -> list:
        """收集路径及其父级的 APIRouter 依赖项。"""
        router = RouterLoader.from_extensions()
        segments = [
            segment
            for segment in path.split("/")
            if segment and not segment.startswith("{")
        ]
        candidate_paths = ["/"]
        current = ""
        for segment in segments:
            current = f"{current}/{segment}" if current else f"/{segment}"
            candidate_paths.append(current)

        dependencies: list = []
        seen: set = set()

        for candidate in candidate_paths:
            try:
                api_router = router.get_attr(candidate, "api_router")
            except Exception:  # pragma: no cover
                api_router = None
            if not api_router:
                continue
            for dependency in getattr(api_router, "dependencies", []) or []:
                dependency_func = getattr(dependency, "dependency", None)
                if callable(dependency_func) and dependency_func not in seen:
                    dependencies.append(dependency)
                    seen.add(dependency_func)
        return dependencies

    @staticmethod
    def build_route_map() -> dict[str, BaseRoute]:
        """建立路线图。"""
        router = RouterLoader.from_extensions()
        route_map = {
            route.path: route
            for route in router.api_router.routes  # type: ignore
            if isinstance(route, APIRoute)
            and "." not in str(route.path)
            and getattr(route, "include_in_schema", True)
        }

        # Also include routes directly registered on _api_router instances
        # We need to traverse the router tree to find all _api_router instances
        def collect_api_router_routes(router_obj, collected_routes):
            """递归地从 _api_router 实例收集路由。"""
            if hasattr(router_obj, "_api_router"):
                for inner_route in router_obj._api_router.routes:  # type: ignore  # pylint: disable=W0212
                    if (
                        isinstance(inner_route, APIRoute)
                        and getattr(inner_route, "include_in_schema", True)
                        and (inner_route.path not in collected_routes)
                    ):
                        collected_routes[inner_route.path] = inner_route

            # Check if this router has sub-routers
            if hasattr(router_obj, "api_router") and hasattr(
                router_obj.api_router, "routes"
            ):
                for route in router_obj.api_router.routes:  # type: ignore
                    if not isinstance(route, APIRoute):
                        continue
                    endpoint = getattr(route, "endpoint", None)
                    if endpoint and hasattr(endpoint, "__self__"):
                        collect_api_router_routes(endpoint.__self__, collected_routes)

        collect_api_router_routes(router, route_map)

        return route_map  # type: ignore

    @staticmethod
    def build_path_list(route_map: dict[str, BaseRoute]) -> list[str]:
        """构建路径列表。"""
        path_list = []
        for route_path in route_map:
            if route_path not in path_list:
                path_list.append(route_path)

                sub_path_list = route_path.split("/")

                for length in range(len(sub_path_list)):
                    sub_path = "/".join(sub_path_list[:length])
                    if sub_path not in path_list:
                        # Don't add paths that only exist as part of parameterized routes
                        has_direct_route = sub_path in route_map
                        # A child route is non-parameterized if the next segment doesn't start with {
                        has_real_children = False
                        for r in route_map:
                            if r.startswith(sub_path + "/"):
                                remainder = r[len(sub_path) + 1 :]
                                next_segment = (
                                    remainder.split("/")[0] if remainder else ""
                                )
                                if next_segment and not next_segment.startswith("{"):
                                    has_real_children = True
                                    break

                        if has_direct_route or has_real_children:
                            path_list.append(sub_path)

        return path_list

    @staticmethod
    def get_route(path: str, route_map: dict[str, BaseRoute]):
        """从路径获取路由。"""
        return route_map.get(path)

    @staticmethod
    def get_child_path_list(path: str, path_list: list[str]) -> list[str]:
        """获取子路径列表。

        这将返回作为给定路径子项的子路由器路径和直接路由路径。
        例如，对于 path="/empty"，它返回以下两者：
        - "/empty/sub_router"（path_list 中的子路由器）
        - "/empty/also_empty/{param}"（route_map 中的直接路由）
        """
        direct_children = []
        base_depth = path.count("/") if path else 0

        # Get route_map to check for routes that aren't in path_list
        route_map = PathHandler.build_route_map()

        # First, add children from path_list (these are sub-routers)
        for p in path_list:
            if p.startswith(path + "/") if path else p.startswith("/"):
                p_depth = p.count("/")
                if p_depth == base_depth + 1:
                    direct_children.append(p)

        # Second, add routes from route_map that are direct children but not in path_list
        # (these are endpoints with path parameters)
        for route_path in route_map:
            if route_path not in direct_children and (
                route_path.startswith(path + "/")
                if path
                else route_path.startswith("/")
            ):
                # Remove the parent path prefix
                remainder = route_path[len(path) + 1 :] if path else route_path[1:]

                # Split by "/" and count non-empty segments
                segments = [s for s in remainder.split("/") if s]
                if segments:
                    first_non_param_idx = next(
                        (
                            i
                            for i, seg in enumerate(segments)
                            if not seg.startswith("{")
                        ),
                        None,
                    )
                    is_direct_child = first_non_param_idx is None or (
                        first_non_param_idx == 0
                        and all(seg.startswith("{") for seg in segments[1:])
                    )
                    if is_direct_child and route_path not in direct_children:
                        direct_children.append(route_path)

        return direct_children

    @staticmethod
    def clean_path(path: str) -> str:
        """清理路径。"""
        if path.startswith("/"):
            path = path[1:]
        return path.replace("-", "_").replace("/", "_")

    @classmethod
    def build_module_name(cls, path: str) -> str:
        """构建模块名称。"""
        if not path:
            return "__extensions__"
        return cls.clean_path(path=path)

    @classmethod
    def build_module_class(cls, path: str) -> str:
        """构建模块类。"""
        if not path:
            return "Extensions"
        return f"ROUTER_{cls.clean_path(path=path)}"

    @staticmethod
    def extract_path_parameters(path: str) -> list[str]:
        """从路由路径中提取路径参数。

        Parameters
        ----------
        path : str
            路由路径（例如，"/users/{user_id}/posts/{post_id}"）

        Returns
        -------
        list[str]
            路径参数名称列表（例如，["user_id", "post_id"]）
        """
        # Match parameters in curly braces
        pattern = r"\{(\w+)\}"
        return re.findall(pattern, path)

    @staticmethod
    def get_router_description(path: str) -> str:
        """返回路由器路径的描述。"""
        router = RouterLoader.from_extensions()
        description = router.get_attr(path or "/", "description")
        if description:
            return description
        clean_path = path or "/"
        return f"Router for {clean_path}."


class ReferenceGenerator:
    """生成平台参考。"""

    REFERENCE_FIELDS = [
        "deprecated",
        "description",
        "examples",
        "parameters",
        "returns",
        "data",
    ]

    # pylint: disable=protected-access
    pi = DocstringGenerator.provider_interface
    route_map = PathHandler.build_route_map()

    @classmethod
    def _get_endpoint_examples(
        cls,
        path: str,
        func: Callable,
        examples: list[Example] | None,
    ) -> str:
        """获取给定标准模型 or 函数的示例。

        对于给定的标准模型或函数，示例是从 Example 对象列表中提取并格式化为字符串。

        Parameters
        ----------
        path : str
            路由器的路径。
        func : Callable
            路由端点函数。
        examples : Optional[List[Example]]
            端点的示例列表（APIEx 或 PythonEx 类型）。

        Returns
        -------
        str:
            包含端点示例的格式化字符串。
        """
        sig = signature(func)
        parameter_map = dict(sig.parameters)
        formatted_params = MethodDefinition.format_params(
            path=path, parameter_map=parameter_map
        )
        explicit_params = dict(formatted_params)
        explicit_params.pop("extra_params", None)
        param_types = {k: v.annotation for k, v in explicit_params.items()}

        return DocstringGenerator.build_examples(
            path.replace("/", "."),
            param_types,
            examples,
            "website",
        )

    @classmethod
    def _get_provider_parameter_info(cls, model: str) -> dict[str, Any]:
        """获取提供者参数的名称、类型、描述、默认值和可选性信息。

        Parameters
        ----------
        model : str
            用于访问模型提供程序的标准模型。

        Returns
        -------
        Dict[str, Any]
            提供者参数信息字典
        """
        pi_model_provider = cls.pi.model_providers[model]
        provider_params_field = pi_model_provider.__dataclass_fields__["provider"]

        name = provider_params_field.name
        field_type = DocstringGenerator.get_field_type(
            provider_params_field.type, False
        )
        default_priority = (
            provider_params_field.type.__args__
            if provider_params_field.type
            and hasattr(provider_params_field.type, "__args__")
            else []
        )
        description = (
            "要使用的提供者，默认为 None。 "
            "如果为 None，则使用设置中配置的优先级列表。 "
            f"默认优先级：{', '.join(default_priority)}。"
        )

        provider_parameter_info = {
            "name": name,
            "type": field_type,
            "description": description,
            "default": None,
            "optional": True,
        }

        return provider_parameter_info

    @classmethod
    def _get_provider_field_params(
        cls, model: str, params_type: str, provider: str = "openbb"
    ) -> list[dict[str, Any]]:
        """获取 standard_model 给定提供者的给定参数类型的字段。"""
        provider_field_params = []
        expanded_types = MethodDefinition.TYPE_EXPANSION
        model_map = cls.pi.map[model]

        # First, check if the provider class itself has __json_schema_extra__
        # This contains class-level schema information that applies to fields
        class_schema_extra = {}
        try:
            # Get the actual provider class
            provider_class = model_map[provider][params_type]["class"]
            # Check for class-level __json_schema_extra__ attribute
            if hasattr(provider_class, "__json_schema_extra__"):
                class_schema_extra = provider_class.__json_schema_extra__
        except (KeyError, AttributeError):
            pass

        for field, field_info in model_map[provider][params_type]["fields"].items():
            # Start with class-level schema information for this field if it exists
            extra = {}
            choices = None
            if field in class_schema_extra:
                extra = class_schema_extra[field].copy()
                choices = extra.get("choices")

            # Then apply field-level schema extra (which takes precedence)
            field_extra = field_info.json_schema_extra or {}
            extra.update(field_extra)
            if "choices" in field_extra:
                choices = field_extra.pop("choices", [])

            if provider != "openbb" and provider in extra:
                extra = extra[provider]

            # Determine the field type, expanding it if necessary
            field_type = field_info.annotation
            is_required = field_info.is_required()

            origin = get_origin(field_type)
            if origin is Union:
                args = get_args(field_type)
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    field_type = non_none_types[0]
                if type(None) in args:
                    is_required = False

            # Then unwrap Annotated
            while get_origin(field_type) is Annotated:
                args = get_args(field_type)
                if args:
                    field_type = args[0]
                else:
                    break

            field_type_str = DocstringGenerator.get_field_type(
                field_type, is_required, "website"
            )

            if field_type_str == "Annotated | None" or field_type_str.startswith(
                "Annotated"
            ):
                # If we still have "Annotated" in the string, extract the actual type
                if hasattr(field_type, "__name__") or isinstance(field_type, type):
                    field_type_str = field_type.__name__
                else:
                    # Last resort: try to parse from string representation
                    type_repr = str(field_type).replace("typing.", "")
                    if "Annotated[" in type_repr:
                        # Extract the first type argument
                        match = re.search(r"Annotated\[([^,\]]+)", type_repr)
                        if match:
                            field_type_str = match.group(1)
                    else:
                        field_type_str = type_repr

            if is_required is False and "| None" not in field_type_str:
                field_type_str = f"{field_type_str} | None"

            # Handle case where field_type_str contains ", optional" suffix
            if ", optional" in field_type_str:
                field_type_str = field_type_str.replace(", optional", "")
                is_required = False

            cleaned_description = str(field_info.description).strip().replace('"', "'")

            # Add information for the providers supporting multiple symbols
            if params_type == "QueryParams" and extra:
                providers: list = []
                for p, v in extra.items():
                    if isinstance(v, dict) and v.get("multiple_items_allowed"):
                        providers.append(p)
                        if "choices" in v:
                            choices = v.get("choices")
                    elif isinstance(v, list) and "multiple_items_allowed" in v:
                        providers.append(p)
                    elif isinstance(v, dict) and "choices" in v:
                        choices = v.get("choices")

                if providers or extra.get("multiple_items_allowed"):
                    cleaned_description += " Multiple items allowed"
                    if providers:
                        multiple_items = ", ".join(providers)
                        cleaned_description += f" for provider(s): {multiple_items}"
                    cleaned_description += "."
                    field_type_str = f"{field_type_str} | list[{field_type_str}]"
            elif field in expanded_types:
                expanded_type = DocstringGenerator.get_field_type(
                    expanded_types[field], is_required, "website"
                )
                field_type_str = f"{field_type_str} | {expanded_type}"

            default_value = (
                None if field_info.default is PydanticUndefined else field_info.default
            )
            if default_value == "":
                default_value = None

            to_append = {
                "name": field,
                "type": field_type_str,
                "description": cleaned_description,
                "default": default_value,
                "optional": not is_required,
            }
            if params_type != "Data":
                to_append.update(
                    {
                        "choices": choices or extra.pop("choices", []),
                        "multiple_items_allowed": extra.pop(
                            "multiple_items_allowed", False
                        ),
                        "json_schema_extra": extra or {},
                    }
                )
            else:
                to_append.update({"json_schema_extra": extra or {}})
            provider_field_params.append(to_append)

        return provider_field_params

    @staticmethod
    def _get_obbject_returns_fields(
        model: str,
        providers: str,
    ) -> list[dict[str, str]]:
        """获取给定 standard_model 的 OBBject 返回对象的字段。

        Parameters
        ----------
        model : str
            返回对象的标准模型。
        providers : str
            该模型的可用提供程序。

        Returns
        -------
        List[Dict[str, str]]
            包含每个字段的字段名称、类型、描述、默认值和可选性的字典列表。
        """
        obbject_list = [
            {
                "name": "results",
                "type": model,
                "description": "可序列化结果。",
            },
            {
                "name": "provider",
                "type": providers if providers else "str",
                "description": "提供者名称。",
            },
            {
                "name": "warnings",
                "type": "Optional[list[Warning_]]",
                "description": "警告列表。",
            },
            {
                "name": "chart",
                "type": "Optional[Chart]",
                "description": "图表对象。",
            },
            {
                "name": "extra",
                "type": "dict[str, Any]",
                "description": "额外信息。",
            },
        ]

        return obbject_list

    @staticmethod
    def _get_post_method_parameters_info(
        docstring: str,
    ) -> list[dict[str, bool | str]]:
        """获取 POST 方法端点的参数。

        Parameters
        ----------
        docstring : str
            路由器端点函数的文档字符串

        Returns
        -------
        List[Dict[str, str]]
            包含每个参数的名称、类型、描述、默认值和可选性的字典列表。
        """
        parameters_list: list = []

        # Extract only the Parameters section (between "Parameters" and "Returns")
        params_section = ""
        if "Parameters" in docstring and "Returns" in docstring:
            params_section = docstring.split("Parameters")[1].split("Returns")[0]
        elif "Parameters" in docstring:
            params_section = docstring.split("Parameters")[1]
        else:
            return parameters_list  # No parameters section found

        # Define a regex pattern to match parameter blocks
        # This pattern looks for a parameter name followed by " : ", then captures the type and description
        pattern = re.compile(
            r"\n\s*(?P<name>\w+)\s*:\s*(?P<type>[^\n]+?)(?:\s*=\s*(?P<default>[^\n]+))?\n\s*(?P<description>[^\n]+)"
        )

        # Find all matches in the parameters section only
        matches = pattern.finditer(params_section)

        if matches:
            # Iterate over the matches to extract details
            for match in matches:
                # Extract named groups as a dictionary
                param_info = match.groupdict()

                # Clean up and process the type string
                param_type = param_info["type"].strip()

                # Check for ", optional" in type and handle appropriately
                is_optional = "Optional" in param_type or ", optional" in param_type
                if ", optional" in param_type:
                    param_type = param_type.replace(", optional", "")

                # If no default value is captured, set it to an empty string
                default_value = (
                    param_info["default"] if param_info["default"] is not None else ""
                )
                param_type = (
                    str(param_type)
                    .replace("openbb_core.provider.abstract.data.Data", "Data")
                    .replace("List", "list")
                    .replace("Dict", "dict")
                    .replace("NoneType", "None")
                )
                # Create a new dictionary with fields in the desired order
                param_dict = {
                    "name": param_info["name"],
                    "type": ReferenceGenerator._clean_string_values(param_type),
                    "description": ReferenceGenerator._clean_string_values(
                        param_info["description"]
                    ),
                    "default": default_value,
                    "optional": is_optional,
                }

                # Append the dictionary to the list
                parameters_list.append(param_dict)

        return parameters_list

    @staticmethod
    def _clean_string_values(value: Any) -> Any:
        """将字符串值中的双引号转换为单引号并修复类型引用。

        Parameters
        ----------
        value : Any
            要清理的值

        Returns
        -------
        Any
            清理后的值
        """
        if isinstance(value, str):
            # Fix fully qualified Data type references
            value = re.sub(
                r"list\[openbb_core\.provider\.abstract\.data\.Data\]",
                "list[Data]",
                value,
            )
            value = re.sub(
                r"openbb_core\.provider\.abstract\.data\.Data", "Data", value
            )

            # Clean up Union types
            if "Union[" in value:
                try:
                    # Extract types from Union
                    types_str = value[value.find("[") + 1 : value.rfind("]")]
                    # Split types and clean them up
                    types = [t.strip() for t in types_str.split(",")]
                    # Use a set to handle unique types and maintain order for display
                    unique_types = sorted(list(set(types)))
                    # Rebuild the string with " | " separator
                    value = " | ".join(unique_types)
                except Exception:  # pylint: disable=broad-except  # noqa
                    pass

            # Handle Literal types specifically
            if (
                "Literal[" in value
                and "]" in value
                and "'" not in value
                and '"' not in value
            ):
                # Extract the content between Literal[ and ]
                start_idx = value.find("Literal[") + len("Literal[")
                end_idx = value.rfind("]")
                if start_idx < end_idx:
                    content = value[start_idx:end_idx]
                    # Add single quotes around each value
                    values = [f"'{v.strip()}'" for v in content.split(",")]
                    # Reconstruct the Literal type
                    return f"Literal[{', '.join(values)}]"

            value = re.sub(r"\bDict\b", "dict", value)
            value = re.sub(r"\bList\b", "list", value)

            return value.replace('"', "'")

        if isinstance(value, dict):
            return {
                k: ReferenceGenerator._clean_string_values(v) for k, v in value.items()
            }

        if isinstance(value, list):
            return [ReferenceGenerator._clean_string_values(item) for item in value]

        return value

    @staticmethod
    def _get_function_signature_info(func: Callable) -> list[dict[str, Any]]:
        """直接从函数签名中提取参数信息。"""
        params_info = []
        sig = signature(func)

        for name, param in sig.parameters.items():
            # Skip 'self' and context parameters
            if name in ["self", "cc"]:
                continue

            # Skip parameters with dependency injections through annotations
            if isinstance(param.annotation, _AnnotatedAlias) and any(
                hasattr(meta, "dependency") for meta in param.annotation.__metadata__
            ):
                continue

            # Skip parameters with Depends in default values
            if param.default is not Parameter.empty:
                default_str = str(param.default)
                if "Depends" in default_str:
                    continue

            param_type = param.annotation
            is_optional = (
                param.default is not Parameter.empty
            )  # Parameter is optional if it has a default value
            description = ""
            choices = None
            default = param.default if param.default is not Parameter.empty else None
            json_extra: dict = {}

            # Check if type is optional
            if (
                hasattr(param_type, "__origin__")
                and param_type.__origin__ is Union
                and (type(None) in param_type.__args__ or None in param_type.__args__)
            ):
                # Check if None or NoneType is in the union
                is_optional = True
                # Extract the actual type (excluding None)
                non_none_args = [
                    arg
                    for arg in param_type.__args__
                    if arg is not type(None) and arg is not None
                ]
                if len(non_none_args) == 1:
                    param_type = non_none_args[0]

            if isinstance(param_type, _AnnotatedAlias):
                base_type = param_type.__args__[0]
                for meta in param_type.__metadata__:
                    if hasattr(meta, "description"):
                        description = meta.description
                    if hasattr(meta, "choices"):
                        choices = meta.choices
                    if hasattr(meta, "default"):
                        default = meta.default
                    if hasattr(meta, "json_schema_extra"):
                        json_extra = meta.json_schema_extra

                # Set the actual type to the base type
                param_type = base_type

            # Handle Query objects passed as parameters or default values.
            if str(default.__class__).endswith("Query'>") or "Query" in str(
                default.__class__
            ):
                param_type = (
                    param_type.annotation
                    if hasattr(param_type, "annotation")
                    else str(param_type)
                )
                description = default.description  # type: ignore
                json_extra = default.json_schema_extra  # type: ignore
                has_default = hasattr(default, "default") and default.default not in [  # type: ignore
                    Parameter.empty,
                    PydanticUndefined,
                    Ellipsis,
                ]
                is_optional = has_default or (
                    hasattr(default, "is_required") and default.is_required is False  # type: ignore
                )
                default = (
                    default.default  # type: ignore
                    if default.default not in [Parameter.empty, PydanticUndefined, Ellipsis]  # type: ignore
                    else None
                )

            # Convert type to string representation
            type_str = str(param_type)
            # Clean up type string
            type_str = (
                type_str.replace("<class '", "")
                .replace("'>", "")
                .replace("typing.", "")
                .replace("NoneType", "None")
                .replace("inspect._empty", "Any")
            )
            params_info.append(
                {
                    "name": name,
                    "type": type_str,
                    "description": ReferenceGenerator._clean_string_values(description),
                    "default": (
                        None
                        if default in (PydanticUndefined, Parameter.empty, Ellipsis)
                        else ReferenceGenerator._clean_string_values(default)
                    ),
                    "optional": is_optional,
                    "choices": choices or json_extra.pop("choices", []),
                    "multiple_items_allowed": json_extra.pop(
                        "multiple_items_allowed", False
                    ),
                    "json_schema_extra": json_extra or {},
                }
            )

        return params_info

    @staticmethod
    def _get_post_method_returns_info(docstring: str) -> dict:
        """获取 POST 方法端点的返回信息。

        Parameters
        ----------
        docstring: str
            路由器端点函数的文档字符串

        Returns
        -------
        List[Dict[str, str]]
            包含包含返回值名称、类型、描述的字典的单元素列表
        """
        returns_dict: dict = {}
        # This pattern captures the model name inside "OBBject[]" and its description
        match = re.search(r"Returns\n\s*-------\n\s*([^\n]+)\n\s*([^\n]+)", docstring)

        if match:
            return_type = match.group(1).strip()  # type: ignore
            # Remove newlines and indentation from the description
            description = match.group(2).strip().replace("\n", "").replace("    ", "")  # type: ignore
            # Adjust regex to correctly capture content inside brackets, including nested brackets
            content_inside_brackets = re.search(
                r"OBBject\[\s*((?:[^\[\]]|\[[^\[\]]*\])*)\s*\]", return_type
            ) or re.search(r"list\[\s*((?:[^\[\]]|\[[^\[\]]*\])*)\s*\]", return_type)
            return_type = (  # type: ignore
                content_inside_brackets.group(1)
                if content_inside_brackets is not None
                else return_type
            )

            returns_dict = {
                "name": "results",
                "type": return_type,
                "description": description,
            }

        return returns_dict

    @classmethod
    def get_paths(  # noqa: PLR0912
        cls, route_map: dict[str, BaseRoute]
    ) -> dict[str, dict[str, Any]]:
        """获取路径参考数据。

        The reference data is a dictionary containing the description, parameters,
        returns and examples for each endpoint. This is currently useful for
        automating the creation of the website documentation files.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            包含每个端点的描述、参数、返回值和示例的字典。
        """
        reference: dict[str, dict] = {}

        for path, route in route_map.items():
            # Initialize the provider parameter fields as an empty dictionary
            provider_parameter_fields = {"type": ""}
            # Initialize the reference fields as empty dictionaries
            reference[path] = {field: {} for field in cls.REFERENCE_FIELDS}
            # Route method is used to distinguish between GET and POST methods
            route_method = getattr(route, "methods", None)
            # Route endpoint is the callable function
            route_func = getattr(route, "endpoint", lambda: None)
            # Attribute contains the model and examples info for the endpoint
            openapi_extra = getattr(route, "openapi_extra", {}) or {}
            # Standard model is used as the key for the ProviderInterface Map dictionary
            standard_model = openapi_extra.get("model", "")
            # Add endpoint model for GET methods
            reference[path]["model"] = standard_model
            # Add endpoint deprecation details
            reference[path]["deprecated"] = {
                "flag": MethodDefinition.is_deprecated_function(path),
                "message": MethodDefinition.get_deprecation_message(path),
            }
            # Add endpoint examples
            examples = openapi_extra.pop("examples", [])
            reference[path]["examples"] = cls._get_endpoint_examples(
                path,
                route_func,
                examples,  # type: ignore
            )
            validate_output = not openapi_extra.pop("no_validate", None)
            model_map = cls.pi.map.get(standard_model, {})
            reference[path]["openapi_extra"] = openapi_extra

            # Extract return type information for all endpoints
            return_info = cls._extract_return_type(route_func)

            # Add data for the endpoints having a standard model
            if route_method and model_map:
                reference[path]["description"] = getattr(
                    route, "description", "No description available."
                )
                for provider in model_map:
                    if provider == "openbb":
                        # openbb provider is always present hence its the standard field
                        reference[path]["parameters"]["standard"] = (
                            cls._get_provider_field_params(
                                standard_model, "QueryParams"
                            )
                        )
                        # Add `provider` parameter fields to the openbb provider
                        provider_parameter_fields = cls._get_provider_parameter_info(
                            standard_model
                        )

                        # Add endpoint data fields for standard provider
                        reference[path]["data"]["standard"] = (
                            cls._get_provider_field_params(standard_model, "Data")
                        )
                        continue

                    # Adds provider specific parameter fields to the reference
                    reference[path]["parameters"][provider] = (
                        cls._get_provider_field_params(
                            standard_model, "QueryParams", provider
                        )
                    )

                    # Adds provider specific data fields to the reference
                    reference[path]["data"][provider] = cls._get_provider_field_params(
                        standard_model, "Data", provider
                    )

                    # Remove choices from standard parameters if they exist in provider-specific parameters
                    provider_param_names = {
                        p["name"] for p in reference[path]["parameters"][provider]
                    }

                    for i, param in enumerate(
                        reference[path]["parameters"]["standard"]
                    ):
                        param_name = param.get("name")
                        if (
                            param_name in provider_param_names
                            and param.get("choices") is not None
                        ):
                            # This parameter has a provider-specific version, so remove choices from standard
                            reference[path]["parameters"]["standard"][i][
                                "choices"
                            ] = None

                # Add endpoint returns data
                if validate_output is False:
                    reference[path]["returns"]["Any"] = {
                        "description": "Unvalidated results object.",
                    }
                else:
                    providers = provider_parameter_fields["type"]
                    if isinstance(return_info, dict) and "OBBject" in return_info:
                        results_field = next(
                            (
                                f
                                for f in return_info["OBBject"]
                                if f["name"] == "results"
                            ),
                            None,
                        )
                        if results_field:
                            results_type = results_field["type"]
                            if results_type == "Any":
                                results_type = f"list[{standard_model}]"
                            reference[path]["returns"]["OBBject"] = (
                                cls._get_obbject_returns_fields(results_type, providers)
                            )
            # Add data for the endpoints without a standard model (data processing endpoints)
            else:
                results_type = "Any"
                openapi_extra = (
                    getattr(
                        route_func, "openapi_extra", getattr(route, "openapi_extra", {})
                    )
                    or {}
                )

                model_name = openapi_extra.get("model", "") or ""
                if isinstance(return_info, dict) and "OBBject" in return_info:
                    results_field = next(
                        (f for f in return_info["OBBject"] if f["name"] == "results"),
                        None,
                    )
                    if results_field:
                        results_type = results_field["type"]
                        # Extract model name from types like list[Model] or Model
                        if "[" in results_type and "]" in results_type:
                            inner_type = results_type.split("[")[1].split("]")[0]
                            extracted_model = (
                                inner_type.split(".")[-1]
                                if "." in inner_type
                                else inner_type
                            )
                            model_name = model_name or extracted_model
                        else:
                            extracted_model = (
                                results_type.split(".")[-1]
                                if "." in results_type
                                else results_type
                            )
                            model_name = model_name or extracted_model

                formatted_params = MethodDefinition.format_params(
                    path=path, parameter_map=dict(signature(route_func).parameters)
                )

                docstring = DocstringGenerator.generate(
                    path=path,
                    func=route_func,
                    formatted_params=formatted_params,
                    model_name=model_name,
                    examples=examples,
                )
                if not docstring:
                    continue

                description = docstring.split("Parameters")[0].strip()
                reference[path]["description"] = re.sub(" +", " ", description)

                # Extract parameters directly from formatted_params
                reference[path]["parameters"]["standard"] = []
                for param in formatted_params.values():
                    if param.name == "kwargs":
                        continue
                    annotation = param.annotation
                    if isinstance(annotation, _AnnotatedAlias):
                        type_str = DocstringGenerator.get_field_type(
                            annotation.__args__[0], False, "website"
                        )
                        description = (
                            annotation.__metadata__[0].description
                            if annotation.__metadata__
                            and hasattr(annotation.__metadata__, "description")
                            else ""
                        )
                    else:
                        type_str = DocstringGenerator.get_field_type(
                            annotation, False, "website"
                        )
                        description = ""
                    reference[path]["parameters"]["standard"].append(
                        {
                            "name": param.name,
                            "type": type_str,
                            "description": description,
                            "default": (
                                param.default
                                if param.default != Parameter.empty
                                else None
                            ),
                            "optional": param.default != Parameter.empty,
                        }
                    )
                # Set returns based on return_info
                if isinstance(return_info, dict) and "OBBject" in return_info:
                    results_field = next(
                        (f for f in return_info["OBBject"] if f["name"] == "results"),
                        None,
                    )
                    if results_field:
                        results_type = results_field["type"]
                        reference[path]["returns"]["OBBject"] = (
                            cls._get_obbject_returns_fields(results_type, "str")
                        )

                # Extract data fields from the model class if results_type is not "Any"
                if results_type != "Any":
                    # Try to extract model name
                    if "[" in results_type:
                        if results_type.startswith("list["):
                            extracted_model_name = results_type[5:-1]
                        else:
                            extracted_model_name = results_type.split("[")[1].split(
                                "]"
                            )[0]
                    else:
                        extracted_model_name = results_type

                    # Try to get the model class from the function's module
                    try:
                        module = sys.modules[route_func.__module__]
                        model_class = getattr(module, extracted_model_name, None)
                        if model_class and hasattr(model_class, "model_fields"):
                            # Set data to the fields
                            reference[path]["data"]["standard"] = []
                            for field_name, field in model_class.model_fields.items():
                                field_type = DocstringGenerator.get_field_type(
                                    field.annotation, field.is_required(), "website"
                                )
                                json_extra = getattr(field, "json_schema_extra", {})
                                reference[path]["data"]["standard"].append(
                                    {
                                        "name": field_name,
                                        "type": field_type,
                                        "description": getattr(
                                            field, "description", ""
                                        ),
                                        "default": (
                                            None
                                            if field.default is PydanticUndefined
                                            else field.default
                                        ),
                                        "optional": not field.is_required(),
                                        "json_schema_extra": json_extra or {},
                                    }
                                )
                    except (KeyError, AttributeError):
                        pass

        return reference

    @staticmethod
    def _extract_return_type(func: Callable) -> str | dict:
        """Extract return type information from function."""
        return_annotation = inspect.signature(func).return_annotation

        # If no return annotation, or return annotation is inspect.Signature.empty
        if return_annotation is inspect.Signature.empty:
            return {"type": "Any"}

        # Use get_type_hints to resolve TypeVars
        hints = get_type_hints(func)
        return_annotation = hints.get("return", return_annotation)

        # Check if the return type is an OBBject
        type_str = str(return_annotation)
        if "OBBject" in type_str or (
            hasattr(return_annotation, "__name__")
            and "OBBject" in return_annotation.__name__
        ):
            # Extract the model name from docstring or type annotation
            result_type = "Any"  # Default fallback

            # Try to extract from type annotation first (more reliable)
            origin = get_origin(return_annotation)
            if origin is not None:
                args = get_args(return_annotation)
                if len(args) > 1:
                    # For OBBject[T, SomeType], results type is SomeType
                    result_type = args[1].__name__
                else:
                    # For OBBject[SomeType]
                    inner_type = args[0] if args else None
                    if inner_type is not None:
                        # Handle container types like list[Model]
                        inner_origin = get_origin(inner_type)
                        if inner_origin is not None:
                            inner_args = get_args(inner_type)
                            if inner_args:
                                container_type = inner_origin
                                model_type = inner_args[0]
                                result_type = (
                                    f"{container_type.__name__}[{model_type.__name__}]"
                                )
                        elif hasattr(inner_type, "__name__"):
                            result_type = inner_type.__name__
                            # Resolve TypeVar bound if available
                            if (
                                hasattr(inner_type, "__bound__")
                                and inner_type.__bound__
                            ):
                                result_type = inner_type.__bound__.__name__
                        elif hasattr(inner_type, "_name") and inner_type._name:
                            result_type = inner_type._name
            else:
                # Fallback: parse from type_str if get_origin fails
                match = re.search(r"OBBject\[.*?\]\[(.*?)\]", type_str)
                if match:
                    result_type = match.group(1)
                # Check for OBBject_ModelName pattern
                elif "OBBject_" in type_str:
                    result_type = type_str.split("OBBject_")[1].split("'")[0]

            # If not found, try to extract from docstring
            if result_type == "list[Data]":
                docstring = inspect.getdoc(func) or ""
                if "Returns" in docstring:
                    returns_section = docstring.split("Returns")[1].split("\n\n")[0]
                    # Look for model name in docstring
                    patterns = [
                        r"OBBject\[(.*?)\]",  # OBBject[Model]
                        r"results : ([\w\d_]+)",  # results : Model
                        r"Returns\s+-------\s+(\w+)",  # Direct return type
                    ]

                    for pattern in patterns:
                        model_match = re.search(pattern, returns_section)
                        if model_match:
                            result_type = model_match.group(1)
                            break

            # Ensure result_type doesn't already have a container type
            if "[" in result_type and "]" not in result_type:
                result_type += "]"  # Add missing closing bracket
            result_type = ReferenceGenerator._clean_string_values(result_type)
            # Return the standard OBBject structure with correct result type
            return {
                "OBBject": [
                    {
                        "name": "results",
                        "type": result_type,
                        "description": "Serializable results.",
                    },
                    {
                        "name": "provider",
                        "type": "Optional[str]",
                        "description": "Provider name.",
                    },
                    {
                        "name": "warnings",
                        "type": "Optional[list[Warning_]]",
                        "description": "List of warnings.",
                    },
                    {
                        "name": "chart",
                        "type": "Optional[Chart]",
                        "description": "Chart object.",
                    },
                    {
                        "name": "extra",
                        "type": "dict[str, Any]",
                        "description": "Extra info.",
                    },
                ]
            }

        # Clean up return type string
        type_str = (
            type_str.replace("<class '", "")
            .replace("'>", "")
            .replace("typing.", "")
            .replace("NoneType", "None")
            .replace("inspect._empty", "Any")
        )

        # Basic types handling
        basic_types = ["int", "str", "dict", "bool", "float", "None", "Any"]
        if type_str.lower() in [t.lower() for t in basic_types]:
            return type_str.lower()

        # Check for container types with square brackets
        container_match = re.search(r"(\w+)\[(.*?)\]", type_str)
        if container_match:
            container_type = container_match.group(1)
            inner_type = container_match.group(2)

            inner_type_name = (
                inner_type.split(".")[-1] if "." in inner_type else inner_type
            )

            return f"{container_type}[{inner_type_name}]"

        model_name = (
            type_str.rsplit(".", maxsplit=1)[-1] if "." in type_str else type_str
        )

        return model_name

    @classmethod
    def get_routers(cls, route_map: dict[str, BaseRoute]) -> dict:
        """Get router reference data.

        Parameters
        ----------
        route_map : Dict[str, BaseRoute]
            Dictionary containing the path and route object for the router.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Dictionary containing the description for each router.
        """
        main_router = RouterLoader().from_extensions()
        routers: dict = {}
        for path in route_map:
            path_parts = path.split("/")
            # We start at 2: ["/", "some_router"] "/some_router"
            i = 2
            p = "/".join(path_parts[:i])
            while p != path:
                if p not in routers:
                    description = main_router.get_attr(p, "description")
                    if description is not None:
                        routers[p] = {"description": description}
                # We go down the path to include sub-routers
                i += 1
                p = "/".join(path_parts[:i])
        return routers
