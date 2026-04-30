"""Path / route handler helpers used during package generation."""

import re
from typing import (
    TYPE_CHECKING,
    TypeVar,
)

from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

from openbb_core.app.router import RouterLoader

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


class PathHandler:
    """Handle the paths for the Platform."""

    @staticmethod
    def get_router_dependencies(path: str) -> list:
        """Collect APIRouter dependencies for the path and its parents."""
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
        """Build the route map."""
        router = RouterLoader.from_extensions()
        route_map = {
            route.path: route
            for route in router.api_router.routes
            if isinstance(route, APIRoute)
            and "." not in str(route.path)
            and getattr(route, "include_in_schema", True)
        }

        # Also include routes directly registered on _api_router instances
        # We need to traverse the router tree to find all _api_router instances
        def collect_api_router_routes(router_obj, collected_routes):
            """Recursively collect routes from _api_router instances."""
            if hasattr(router_obj, "_api_router"):
                for inner_route in router_obj._api_router.routes:
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
                for route in router_obj.api_router.routes:
                    if not isinstance(route, APIRoute):
                        continue
                    endpoint = getattr(route, "endpoint", None)
                    if endpoint and hasattr(endpoint, "__self__"):
                        collect_api_router_routes(endpoint.__self__, collected_routes)

        collect_api_router_routes(router, route_map)

        return route_map  # type: ignore

    @staticmethod
    def build_path_list(route_map: dict[str, BaseRoute]) -> list[str]:
        """Build the path list."""
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
        """Get the route from the path."""
        return route_map.get(path)

    @staticmethod
    def get_child_path_list(path: str, path_list: list[str]) -> list[str]:
        """Get the child path list.

        This returns both sub-router paths AND direct route paths that are children of the given path.
        For example, for path="/empty", it returns both:
        - "/empty/sub_router" (a sub-router in path_list)
        - "/empty/also_empty/{param}" (a direct route from route_map)
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
        """Clean the path."""
        if path.startswith("/"):
            path = path[1:]
        return path.replace("-", "_").replace("/", "_")

    @classmethod
    def build_module_name(cls, path: str) -> str:
        """Build the module name."""
        if not path:
            return "__extensions__"
        return cls.clean_path(path=path)

    @classmethod
    def build_module_class(cls, path: str) -> str:
        """Build the module class."""
        if not path:
            return "Extensions"
        return f"ROUTER_{cls.clean_path(path=path)}"

    @staticmethod
    def extract_path_parameters(path: str) -> list[str]:
        """Extract path parameters from a route path.

        Parameters
        ----------
        path : str
            The route path (e.g., "/users/{user_id}/posts/{post_id}")

        Returns
        -------
        list[str]
            List of path parameter names (e.g., ["user_id", "post_id"])
        """
        # Match parameters in curly braces
        pattern = r"\{(\w+)\}"
        return re.findall(pattern, path)

    @staticmethod
    def get_router_description(path: str) -> str:
        """Return the description for a router path."""
        router = RouterLoader.from_extensions()
        description = router.get_attr(path or "/", "description")
        if description:
            return description
        clean_path = path or "/"
        return f"Router for {clean_path}."
