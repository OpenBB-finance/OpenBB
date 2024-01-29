"""Script used to create charting functions in charting_router.py."""

from inspect import getmembers, isfunction
from typing import List

from openbb_core.app.router import RouterLoader

from openbb_charting import charting_router

# refers to the root of the repo, not the root of the extension
# this script should be run from the root of the repo
CHARTING_ROUTER = (
    "openbb_platform/obbject_extensions/charting/openbb_charting/charting_router.py"
)


def get_routes() -> List[str]:
    """Get all routes from the api router."""
    router = RouterLoader.from_extensions()
    return [route.path for route in router.api_router.routes]  # type: ignore


def create_charting_functions_w_routes(routes_to_add: List[str]):
    """Create new charting functions in charting_router.py."""
    with open(CHARTING_ROUTER, "a") as f:
        for route in routes_to_add:
            original_route = route.replace("_", "/")
            f.write(
                f"""
def {route}(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    raise NotImplementedError("Command `{original_route}` does not have a charting function")
"""
            )


def get_charting_functions() -> List[str]:
    """Get all functions from charting_router.py."""
    functions = getmembers(charting_router, isfunction)
    if functions:
        return [function[0] for function in functions]
    return []


if __name__ == "__main__":
    routes = get_routes()
    # format routes to be valid function names
    routes = [route.replace("/", "_")[1:] for route in routes]
    # get functions already in charting_router.py
    known_functions = get_charting_functions()
    # remove known functions from routes
    routes = [route for route in routes if route not in known_functions]
    # create new functions in charting_router.py
    create_charting_functions_w_routes(routes)
