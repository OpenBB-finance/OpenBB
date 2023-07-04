from inspect import getmembers, isfunction
from typing import List

from openbb_sdk_core.app.router import RouterLoader

CHARTING_ROUTER = "charting_extensions/openbb_custom/charting/charting_router.py"


def get_routes() -> List[str]:
    router = RouterLoader.from_plugins()
    return [route.path for route in router.api_router.routes]


def create_charting_functions_w_routes(routes_to_add: List[str]):
    with open(CHARTING_ROUTER, "a") as f:
        for route in routes_to_add:
            original_route = route.replace("_", "/")
            f.write(
                f"""

def {route}(**kwargs):
    raise NotImplementedError("Command `{original_route}` does not have a charting function")
"""
            )


def get_charting_functions() -> List[str]:
    from charting_extensions.openbb_custom.charting import (  # pylint: disable=import-outside-toplevel
        charting_router,
    )

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
