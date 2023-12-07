"""Test if there are any missing providers for python interface integration tests."""
import importlib.util
import inspect
import os
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    get_type_hints,
)

from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap

from extensions.tests.utils.integration_tests_generator import (
    find_extensions,
    get_test_params_data_processing,
)


def get_integration_tests(
    test_type: Literal["api", "python"], filter_charting_ext: Optional[bool] = True
) -> List[Any]:
    """Get integration tests for the OpenBB Platform."""
    integration_tests: List[Any] = []

    if test_type == "python":
        file_end = "_python.py"
    elif test_type == "api":
        file_end = "_api.py"

    for extension in find_extensions(filter_charting_ext):
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
    command_params: Union[Dict[str, Dict[str, dict]], List[Tuple[Dict[str, str], str]]],
    function_params: List[dict],
    function,
    processing: bool = False,
) -> List[str]:
    """Check if there are any missing providers for a command."""
    if processing or not isinstance(command_params, dict):
        return []

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


def check_wrong_params(
    command_params: Union[Dict[str, Dict[str, dict]], List[Tuple[Dict[str, str], str]]],
    function_params: List[dict],
    function,
    processing: bool = False,
) -> List[str]:
    """Check if there are any wrong params passed to a command."""
    wrong_params = []
    if not processing:
        for i, test_params in enumerate(function_params):
            if "provider" in test_params and i != 0:
                provider = test_params["provider"]
                if provider in command_params:
                    for param in test_params:
                        if (
                            param
                            not in command_params[provider]["QueryParams"]["fields"]
                            and param
                            not in command_params["openbb"]["QueryParams"]["fields"]  # type: ignore
                            and param != "provider"
                        ):
                            wrong_params.append(
                                f"Wrong param {param} for provider {provider} in function {function}"
                            )
            elif isinstance(command_params, dict):
                providers = list(command_params.keys())
                providers.remove("openbb")
                for param in test_params:
                    is_wrong_param = True
                    for provider in providers:
                        if (
                            param in command_params[provider]["QueryParams"]["fields"]
                            or param
                            in command_params["openbb"]["QueryParams"]["fields"]
                            or param == "provider"
                        ):
                            is_wrong_param = False
                            break

                    if is_wrong_param:
                        wrong_params.append(
                            f"Wrong param {param} in function {function}"
                        )

    else:
        for test_params in function_params:
            if isinstance(command_params, list):
                try:
                    iter_commands_params = command_params[0][0]
                except KeyError:
                    iter_commands_params = command_params[0]  # type: ignore

                if isinstance(test_params, dict):
                    param_keys = test_params.keys()
                elif isinstance(test_params, tuple) and all(
                    isinstance(item, dict) for item in test_params
                ):
                    param_keys = [key for item in test_params for key in item]
                else:
                    continue  # Skip this iteration if test_params is neither a dict nor a tuple of dicts

                for key in param_keys:
                    if key not in iter_commands_params and key != "return":
                        wrong_params.append(f"Wrong param {key} in function {function}")
    return wrong_params


def check_missing_params(
    command_params: Union[Dict[str, Dict[str, dict]], List[Tuple[Dict[str, str], str]]],
    function_params: List[dict],
    function,
    processing: bool = False,
) -> List[str]:
    """Check if there are any missing params for a command."""
    missing_params = []
    if not processing:
        for i, test_params in enumerate(function_params):
            if "provider" in test_params and i != 0:
                provider = test_params["provider"]
                if provider in command_params:
                    for expected_param in command_params[provider]["QueryParams"][
                        "fields"
                    ]:
                        if expected_param not in test_params:
                            missing_params.append(
                                f"Missing param {expected_param} for provider {provider} in function {function}"
                            )
            elif isinstance(command_params, dict):
                for expected_param in command_params["openbb"]["QueryParams"]["fields"]:
                    if expected_param not in test_params:
                        missing_params.append(
                            f"Missing standard param {expected_param} in function {function}"
                        )
    else:
        for test_params in function_params:
            if isinstance(command_params, list):
                try:
                    iter_commands_params = command_params[0][0]
                except KeyError:
                    iter_commands_params = command_params[0]  # type: ignore

                for expected_param in iter_commands_params:
                    try:
                        used_params = test_params[0].keys()
                    except KeyError:
                        used_params = test_params.keys()
                    if expected_param not in used_params and expected_param != "return":
                        missing_params.append(
                            f"Missing param {expected_param} in function {function}"
                        )
    return missing_params


def check_integration_tests(
    functions: Dict[str, Any],
    check_function: Callable[
        [
            Union[Dict[str, Dict[str, dict]], List[Tuple[Dict[str, str], str]]],
            List[dict],
            str,
            bool,
        ],
        List[str],
    ],
) -> List[str]:
    """Check if there are any missing items for integration tests."""
    pi = ProviderInterface()
    provider_interface_map = pi.map
    cm = CommandMap(coverage_sep=".")

    function_params: List[dict] = []
    all_missing_items: List[str] = []
    used_functions: List[str] = []

    for command, model in cm.commands_model.items():
        for function in functions:
            if command[1:].replace(".", "_") == function.replace("test_", ""):
                command_params: Dict[str, Dict[str, dict]] = provider_interface_map[
                    model
                ]
                function_params = functions[function].pytestmark[1].args[1]

                missing_items = check_function(
                    command_params, function_params, function, False
                )
                all_missing_items.extend(missing_items)
                used_functions.append(function)

    # the processing commands are the ones that are left
    processing_functions = [
        function for function in functions if function not in used_functions
    ]

    for route, _ in cm.map.items():
        for function in processing_functions:
            if route.replace("/", "_")[1:] == function.replace("test_", ""):
                hints = get_type_hints(cm.map[route])
                processing_command_params = [
                    {k: "" for k in get_test_params_data_processing(hints)}
                ]
                function_params = functions[function].pytestmark[1].args[1]

                missing_items = check_function(
                    processing_command_params, function_params, function, True  # type: ignore
                )

                all_missing_items.extend(missing_items)

    return all_missing_items


def check_missing_integration_tests(test_type: Literal["api", "python"]) -> List[str]:
    """Check if all endpoints have integration tests."""
    cm = CommandMap(coverage_sep=".")
    routes = [route[1:].replace("/", "_") for route in cm.map]
    missing_integration_tests: List[str] = []

    if test_type == "api":
        functions = get_module_functions(get_integration_tests(test_type="api"))
    else:
        functions = get_module_functions(get_integration_tests(test_type="python"))

    tested_functions = [
        function.replace("test_", "", 1)
        for function in functions
        if function.startswith("test_")
    ]

    for route in routes:
        if route not in tested_functions:
            # TODO: See how to handle edge cases that are excluded from the schema
            # on purpose. This is currently on the econometrics router.
            if test_type == "api" and "econometrics" in route:
                continue
            missing_integration_tests.append(
                f"Missing {test_type} integration test for route {route}"
            )

    return missing_integration_tests


def check_missing_integration_test_providers(functions: Dict[str, Any]) -> List[str]:
    """Check if there are any missing providers for integration tests."""
    return check_integration_tests(functions, check_missing_providers)


def check_missing_integration_test_params(functions: Dict[str, Any]) -> List[str]:
    """Check if there are any missing params for integration tests."""
    return check_integration_tests(functions, check_missing_params)


def check_wrong_integration_test_params(functions: Dict[str, Any]) -> List[str]:
    """Check if there are any wrong params for integration tests."""
    return check_integration_tests(functions, check_wrong_params)
