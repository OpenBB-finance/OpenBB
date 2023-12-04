"""Router testers."""

import importlib
import os
from inspect import getmembers, isfunction
from typing import Dict, List, Optional

from openbb_core.app.provider_interface import ProviderInterface


def collect_routers(path) -> List:
    """Collect all routers in the path."""
    routers = []
    for root, _, files in os.walk(path):
        for name in files:
            if name.endswith("_router.py"):
                routers.append(os.path.join(root, name))

    return routers


def import_routers(routers: List) -> List:
    """Import all routers."""
    loaded_routers: List = []
    for router in routers:
        module = importlib.import_module(router.replace("/", ".").replace(".py", ""))
        loaded_routers.append(module)

    return loaded_routers


def collect_router_functions(loaded_routers: List) -> Dict:
    """Collect all router functions."""
    router_functions = {}
    for router in loaded_routers:
        router_functions[router.__name__] = [
            function[1]
            for function in getmembers(router, isfunction)
            if function[0] != "router"
        ]

    return router_functions


def find_decorator(file_path: str, function_name: str) -> Optional[str]:
    """Find the decorator of the function in the file."""
    with open(file_path) as file:
        lines = file.readlines()
        for index, line in enumerate(lines):
            if function_name in line:
                decorator = lines[index - 1]
                if "@" not in decorator:
                    continue
                decorator = decorator.split('"')[1]
                return decorator

    return None


def find_missing_router_function_models(
    router_functions: Dict, pi_map: Dict
) -> List[str]:
    """Find the missing models in the router functions."""
    missing_models: List[str] = []
    for router_name, functions in router_functions.items():
        for function in functions:
            decorator = find_decorator(
                os.path.join(*router_name.split(".")) + ".py",
                function.__name__,
            )
            if (
                decorator not in pi_map
                and decorator is not None
                and "POST" not in decorator
                and "GET" not in decorator
            ):
                missing_models.append(
                    f"{function.__name__} in {router_name} model doesn't exist in the provider interface map."
                )

    return missing_models


def check_router_function_models() -> List[str]:
    """Check if the models in the router functions exist in the provider interface map."""
    pi = ProviderInterface()
    pi_map = pi.map
    routers = collect_routers(os.path.join("openbb_platform", "extensions", "routers"))
    loaded_routers = import_routers(routers)
    router_functions = collect_router_functions(loaded_routers)
    missing_models = find_missing_router_function_models(router_functions, pi_map)

    return missing_models
