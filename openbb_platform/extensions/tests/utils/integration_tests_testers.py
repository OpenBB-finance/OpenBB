"""Test if there are any missing providers for python interface integration tests."""
import importlib.util
import inspect
import os
from typing import Any, Callable, Dict, List, Literal

from extensions.tests.utils.integration_tests_generator import find_extensions
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap


def get_integration_tests(test_type: Literal["integration", "unit"]) -> List[Any]:
    """Get integration tests for the OpenBB Platform."""
    integration_tests: List[Any] = []

    if test_type == "unit":
        file_end = "_python.py"
    elif test_type == "integration":
        file_end = "_api.py"

    for extension in find_extensions():
        integration_folder = os.path.join(extension, "integration")
        for file in os.listdir(integration_folder):
            if file.endswith(file_end):
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


def check_missing_providers(
    command_params: Dict[str, Dict[str, dict]],
    function_params: List[dict],
    function,
) -> List[str]:
    """Check if there are any missing providers for a command."""
    missing_providers: List[str] = []
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
            missing_providers.append(f"Missing providers for {function}: {providers}")

    return missing_providers


def check_missing_params(
    command_params: Dict[str, Dict[str, dict]], function_params: List[dict], function
) -> List[str]:
    """Check if there are any missing params for a command."""
    missing_params = []
    for test_params in function_params:
        if "provider" in test_params:
            provider = test_params["provider"]
            if provider in command_params:
                for expected_param in command_params[provider]["QueryParams"]["fields"]:
                    if expected_param not in test_params.keys():
                        missing_params.append(
                            f"Missing param {expected_param} for provider {provider} in function {function}"
                        )
        else:
            for expected_param in command_params["openbb"]["QueryParams"]["fields"]:
                if expected_param not in test_params.keys():
                    missing_params.append(
                        f"Missing standard param {expected_param} in function {function}"
                    )

    return missing_params


def check_integration_tests(
    functions: Dict[str, Any],
    check_function: Callable[[Dict[str, Dict[str, dict]], List[dict], str], List[str]],
) -> List[str]:
    """Check if there are any missing items for integration tests."""
    pi = ProviderInterface()
    provider_interface_map = pi.map
    cm = CommandMap(coverage_sep=".")

    all_missing_items: List[str] = []

    for command, model in cm.commands_model.items():
        for function in functions:
            if command[1:].replace(".", "_") == function.replace("test_", ""):
                command_params: Dict[str, Dict[str, dict]] = provider_interface_map[
                    model
                ]
                function_params: List[dict] = functions[function].pytestmark[1].args[1]

                missing_items = check_function(
                    command_params, function_params, function
                )
                all_missing_items.extend(missing_items)

    return all_missing_items


def check_missing_integration_test_providers(functions: Dict[str, Any]) -> List[str]:
    """Check if there are any missing providers for integration tests."""
    return check_integration_tests(functions, check_missing_providers)


def check_missing_integration_test_params(functions: Dict[str, Any]) -> List[str]:
    """Check if there are any missing params for integration tests."""
    return check_integration_tests(functions, check_missing_params)
