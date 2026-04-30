"""Import statement emitter for the static package."""

import typing as typing_module
from inspect import _empty, signature
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    get_args,
    get_type_hints,
)

from typing_extensions import _AnnotatedAlias

if TYPE_CHECKING:
    from numpy import ndarray  # noqa
    from pandas import DataFrame, Series  # noqa
    from openbb_core.provider.abstract.data import Data  # noqa

from importlib.util import find_spec

CHARTING_INSTALLED = find_spec("openbb_charting") is not None

try:
    _HAS_FCNTL = True
except Exception:  # pragma: no cover  # noqa
    _HAS_FCNTL = False
    import msvcrt  # noqa

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

from openbb_core.app.static.package_builder._indent import (  # noqa: F401
    TAB,
    create_indent,
)
from openbb_core.app.static.package_builder.path_handler import PathHandler


class ImportDefinition:
    """Build the import definition for the Platform."""

    @staticmethod
    def _sanitize_type_name(type_name: str) -> str:
        """Normalize a raw type name extracted from annotations."""
        sanitized = type_name.strip().replace('"', "").replace("'", "")
        sanitized = sanitized.replace("typing.", "").replace("typing_extensions.", "")
        sanitized = sanitized.split("[", 1)[0]
        sanitized = sanitized.split("(", 1)[0]
        return sanitized

    @staticmethod
    def filter_hint_type_list(hint_type_list: list[type]) -> list[type]:
        """Filter the hint type list."""
        new_hint_type_list = []
        primitive_types = {int, float, str, bool, list, dict, tuple, set}

        for hint_type in hint_type_list:
            # Skip primitive types and empty types
            # Check for _empty first (doesn't require hashing)
            if hint_type == _empty:
                continue

            # Skip Depends objects (they're not types we need to import)
            if (
                hasattr(hint_type, "__class__")
                and "Depends" in hint_type.__class__.__name__
            ):
                continue

            # Skip Annotated types that contain Depends in their metadata
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

            # Now safe to check against primitive_types set
            try:
                if hint_type in primitive_types:
                    continue
            except TypeError:
                # If somehow we still get an unhashable type, skip it
                continue

            # Only include types that have a module and are not builtins
            if (
                hasattr(hint_type, "__module__") and hint_type.__module__ != "builtins"
            ) or (isinstance(hint_type, str)):
                new_hint_type_list.append(hint_type)

        # Deduplicate without using set() to handle unhashable types
        deduplicated: list = []
        for hint_type in new_hint_type_list:
            is_duplicate = False
            for existing in deduplicated:
                try:
                    if hint_type == existing:
                        is_duplicate = True
                        break
                except TypeError:
                    # If comparison fails, compare by identity
                    if id(hint_type) == id(existing):
                        is_duplicate = True
                        break

            if not is_duplicate:
                deduplicated.append(hint_type)

        return deduplicated

    @classmethod
    def get_function_hint_type_list(cls, route) -> list[type]:
        """Get the hint type list from the function."""

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

            # Extract dependencies from Annotated metadata
            if isinstance(parameter.annotation, _AnnotatedAlias):
                for meta in parameter.annotation.__metadata__:
                    # Check if this is a Depends object
                    if hasattr(meta, "dependency"):
                        # Add the dependency function to hint_type_list
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
        """Get the hint type list from the path."""
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
                    hint_type_list.append(type(route.summary.metadata))
                function_hint_type_list = cls.get_function_hint_type_list(route=route)
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
        """Build the import definition."""
        hint_type_list = cls.get_path_hint_type_list(path=path)
        code = "from openbb_core.app.static.container import Container"
        code += "\nfrom openbb_core.app.model.obbject import OBBject"

        # These imports were not detected before build, so we add them manually and
        # ruff --fix the resulting code to remove unused imports.
        # TODO: Find a better way to handle this. This is a temporary solution.
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
            hint_type.__module__
            for hint_type in hint_type_list
            if hasattr(hint_type, "__module__")
        ]
        module_list = list(set(module_list))
        module_list.sort()

        code += "\n"
        for module in module_list:
            code += f"import {module}\n"

        # Group types by module and capture the return types for the imports.
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

        # Generate from-import statements for modules with specific types
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
