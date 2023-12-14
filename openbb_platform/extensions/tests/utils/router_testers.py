"""Router testers."""

import importlib
import os
from inspect import getmembers, isfunction
from typing import Dict, List, Optional

from openbb_core.app.provider_interface import ProviderInterface


def collect_routers(target_dir: str) -> List[str]:
    """Collect all routers in the target directory."""
    current_dir = os.path.dirname(__file__)
    base_path = os.path.abspath(os.path.join(current_dir, "../../../"))

    full_target_path = os.path.abspath(os.path.join(base_path, target_dir))
    routers = []

    for root, _, files in os.walk(full_target_path):
        for name in files:
            if name.endswith("_router.py"):
                full_path = os.path.join(root, name)
                # Convert the full path to a module path
                relative_path = os.path.relpath(full_path, base_path)
                module_path = relative_path.replace("/", ".").replace(".py", "")
                routers.append(module_path)

    return routers


def import_routers(routers: List) -> List:
    """Import all routers."""
    loaded_routers: List = []
    for router in routers:
        module = importlib.import_module(router)
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
    this_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
        this_dir.split("openbb_platform/")[0], "openbb_platform", file_path
    )
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
    routers = collect_routers("extensions")
    loaded_routers = import_routers(routers)
    router_functions = collect_router_functions(loaded_routers)
    missing_models = find_missing_router_function_models(router_functions, pi_map)

    return missing_models


def check_router_model_functions_signature() -> List[str]:
    """Check if the router model functions have the correct signature."""
    expected_args = ["cc", "provider_choices", "standard_params", "extra_params"]
    expected_return_type = "OBBject"
    missing_args: List[str] = []
    missing_return_type: List[str] = []

    routers = collect_routers("extensions")
    loaded_routers = import_routers(routers)
    router_functions = collect_router_functions(loaded_routers)

    for router_name, functions in router_functions.items():
        for function in functions:
            decorator_filer = ["POST", "GET", None]
            decorator = find_decorator(
                os.path.join(*router_name.split(".")) + ".py",
                function.__name__,
            )
            if decorator:
                args = list(function.__code__.co_varnames)
                if args != expected_args and decorator not in decorator_filer:
                    missing_args.append(
                        f"{function.__name__} in {router_name} doesn't have the expected args: {expected_args}"
                    )
                if expected_return_type not in str(function.__annotations__["return"]):
                    missing_return_type.append(
                        f"{function.__name__} in {router_name}"
                        f"doesn't have the expected return type: {expected_return_type}"
                    )

    return missing_args + missing_return_type
