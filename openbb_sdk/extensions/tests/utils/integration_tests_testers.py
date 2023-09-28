"""Test if there are any missing providers for python interface integration tests."""
import importlib.util
import inspect
import os
from typing import Any, Dict, List

from extensions.tests.utils.integration_tests_generator import find_extensions
from sdk.core.openbb_core.app.provider_interface import ProviderInterface
from sdk.core.openbb_core.app.router import CommandMap


def get_python_integration_tests() -> List[Any]:
    """Get integration tests for the python interface."""
    integration_tests: List[Any] = []

    for extension in find_extensions():
        integration_folder = os.path.join(extension, "integration")
        for file in os.listdir(integration_folder):
            if file.endswith("_python.py"):
                file_path = os.path.join(integration_folder, file)
                module_name = file[:-3]  # Remove .py from file name

                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec:
                    module = importlib.util.module_from_spec(spec)
                    if spec.loader:
                        spec.loader.exec_module(module)
                        integration_tests.append(module)

    return integration_tests


def get_module_functions(module_list: List[Any]) -> Dict[str, Any]:
    """Get all functions from a list of modules."""
    functions = {}
    for module in module_list:
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                functions[name] = obj
    return functions


def check_missing_integration_test_providers(functions: Dict[str, Any]) -> List[str]:
    """Check if there are any missing providers for integration tests."""
    pi = ProviderInterface()
    provider_interface_map = pi.map
    cm = CommandMap(coverage_sep=".")

    missing_providers: List[str] = []

    for command, model in cm.commands_model.items():
        for function in functions:
            if command[1:].replace(".", "_") == function.replace("test_", ""):
                command_params: Dict[str, Dict[str, dict]] = provider_interface_map[
                    model
                ]
                function_params: List[dict] = functions[function].pytestmark[1].args[1]

                providers = list(command_params.keys())
                providers.remove("openbb")

                for test_params in function_params:
                    provider = test_params.get("provider", None)
                    if provider:
                        try:  # noqa
                            providers.remove(provider)
                        except ValueError:
                            pass

                if providers:
                    # if there is only one provider left and the length of the
                    #  test_params is 1, we can ignore because it is picked up by default
                    if len(providers) == 1 and len(function_params) == 1:
                        pass
                    else:
                        missing_providers.append(
                            f"Missing providers for {function}: {providers}"
                        )

    return missing_providers
