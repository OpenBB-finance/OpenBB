"""Router testers."""

import ast
import os
from typing import Any, Dict, List, Optional

from openbb_core.app.provider_interface import ProviderInterface

from extensions.tests.utils.helpers import (
    collect_router_functions,
    collect_routers,
    find_decorator,
    find_missing_router_function_models,
    get_all_fields,
    get_decorator_details,
    get_required_fields,
    import_routers,
    parse_example_string,
)


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
            decorator = find_decorator(
                os.path.join(*router_name.split(".")) + ".py",
                function.__name__,
            )
            if decorator:
                if "POST" in decorator or "GET" in decorator:
                    continue
                args = list(function.__code__.co_varnames)
                if args != expected_args and "model" in decorator:
                    missing_args.append(
                        f"{function.__name__} in {router_name} missing expected args: {expected_args}"
                    )
                if expected_return_type not in str(function.__annotations__["return"]):
                    missing_return_type.append(
                        f"{function.__name__} in {router_name} "
                        f"doesn't have the expected return type: {expected_return_type}"
                    )

    return missing_args + missing_return_type


def check_general(
    keywords: Dict, examples: List, router_name: str, function: Any
) -> List[str]:
    """Check for general violations in the router command examples."""
    general_violation: List[str] = []

    # Check if the endpoint has examples
    if "examples" not in keywords or not examples:
        general_violation.append(
            f"'{router_name}' > '{function.__name__}': missing examples"
        )
        return general_violation

    return general_violation


def check_api(
    examples: str, router_name: str, model: Optional[str], function: Any
) -> List[str]:
    """Check for API examples."""
    api_example_violation: List[str] = []
    parsed_examples = parse_example_string(examples)
    if model and "APIEx" in parsed_examples:
        required_fields = set(get_required_fields(model.strip("'")))
        all_fields = get_all_fields(model.strip("'"))
        all_fields.append("provider")
        required_fields_met = False

        for api_example in parsed_examples["APIEx"]:
            params = ast.literal_eval(api_example.get("params", "{}"))
            if not required_fields_met and required_fields.issubset(params.keys()):
                required_fields_met = True

            # Check for unsupported parameters
            for param in params:
                if param not in all_fields:
                    api_example_violation.append(
                        f"'{router_name}' > '{function.__name__}': param '{param}' is not supported by the command."
                    )

        # If after checking all examples, required fields are still not met
        if not required_fields_met:
            api_example_violation.append(
                f"'{router_name}' > '{function.__name__}': missing example with required fields only > {required_fields}"
            )

    return api_example_violation


def check_router_command_examples() -> List[str]:
    """Check if the router command examples satisfy criteria."""
    general_violation: List[str] = []
    api_example_violation: List[str] = []
    python_example_violation: List[str] = []

    routers = collect_routers("extensions")
    loaded_routers = import_routers(routers)
    router_functions = collect_router_functions(loaded_routers)

    for router_name, functions in router_functions.items():
        for function in functions:
            if (
                "basemodel_to_df" in function.__name__
                or "router" not in function.__module__
            ):
                continue
            decorator = find_decorator(
                os.path.join(*router_name.split(".")) + ".py",
                function.__name__,
            )
            if decorator:
                decorator_details = get_decorator_details(function)
                if decorator_details and decorator_details.name == "router.command":
                    keywords = decorator_details.kwargs or {}
                    examples = keywords.get("examples", [])
                    # General checks
                    general_violation += check_general(
                        keywords, examples, router_name, function
                    )
                    if examples:
                        # API example checks
                        model = keywords.get("model", None)
                        api_example_violation += check_api(
                            examples, router_name, model, function
                        )

    return general_violation + api_example_violation + python_example_violation
