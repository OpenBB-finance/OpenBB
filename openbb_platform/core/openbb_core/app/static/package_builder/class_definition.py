"""Class definition emitter for the static package."""

from typing import (
    TYPE_CHECKING,
    TypeVar,
)

if TYPE_CHECKING:
    from numpy import ndarray  # noqa
    from pandas import DataFrame, Series  # noqa
    from openbb_core.provider.abstract.data import Data  # noqa

from importlib.util import find_spec

CHARTING_INSTALLED = find_spec("openbb_charting") is not None

try:
    _HAS_FCNTL = True
except Exception:  # noqa
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
from openbb_core.app.static.package_builder.method_definition import MethodDefinition
from openbb_core.app.static.package_builder.path_handler import PathHandler


class ClassDefinition:
    """Build the class definition for the Platform."""

    @staticmethod
    def build(path: str, ext_map: dict[str, list[str]] | None = None) -> str:
        """Build the class definition."""
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
                and callable(route.endpoint)
                and isinstance(route_methods, set)
                and route_methods
            )

            if (path == "" and is_command_route) or "." in path:
                continue

            if is_command_route:
                doc += f"    {route.name}\n"
                methods += MethodDefinition.build_command_method(
                    path=route.path,
                    func=route.endpoint,
                    model_name=(
                        route.openapi_extra.get("model", None)
                        if hasattr(route, "openapi_extra")
                        and getattr(route, "openapi_extra", None) is not None
                        else None
                    ),
                    examples=(
                        route.openapi_extra.get("examples", [])
                        if hasattr(route, "openapi_extra")
                        and getattr(route, "openapi_extra", None) is not None
                        else []
                    ),
                )
                continue

            if has_subroutes:
                # This is a sub-router path - create a property
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
