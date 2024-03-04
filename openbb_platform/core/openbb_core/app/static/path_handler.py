from typing import Dict, List

from starlette.routing import BaseRoute

from openbb_core.app.router import RouterLoader


class PathHandler:
    """Handle the paths for the Platform."""

    @staticmethod
    def build_route_map() -> Dict[str, BaseRoute]:
        """Build the route map."""
        router = RouterLoader.from_extensions()
        route_map = {route.path: route for route in router.api_router.routes}  # type: ignore

        return route_map

    @staticmethod
    def build_path_list(route_map: Dict[str, BaseRoute]) -> List[str]:
        """Build the path list."""
        path_list = []
        for route_path in route_map:
            if route_path not in path_list:
                path_list.append(route_path)

                sub_path_list = route_path.split("/")

                for length in range(len(sub_path_list)):
                    sub_path = "/".join(sub_path_list[:length])
                    if sub_path not in path_list:
                        path_list.append(sub_path)

        return path_list

    @staticmethod
    def get_route(path: str, route_map: Dict[str, BaseRoute]):
        """Get the route from the path."""
        return route_map.get(path, None)

    @staticmethod
    def get_child_path_list(path: str, path_list: List[str]) -> List[str]:
        """Get the child path list."""
        direct_children = []
        for p in path_list:
            if p.startswith(path):
                path_reminder = p[len(path) :]  # noqa: E203
                if path_reminder.count("/") == 1:
                    direct_children.append(p)

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
