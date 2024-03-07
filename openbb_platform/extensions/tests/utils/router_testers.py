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


def check_general_example_violations(
    keywords: Dict, examples: List, router_name: str, function: Any
) -> List[str]:
    """Check for general violations in the router command examples.

    Criteria
    --------
    - All endpoints should have examples.
    - If any endpoint is excluded from the schema it only needs to contain a Python example.
    - POST method examples should have both API and Python examples,
      unless they are excluded from the schema.
    """
    general_violation: List[str] = []

    # Check if the endpoint has examples
    if "examples" not in keywords or not examples:
        general_violation.append(
            f"'{router_name}' > '{function.__name__}': missing examples"
        )
        return general_violation
    # Check if a POST method has both API and Python examples
    if (
        "POST" in keywords.get("methods", "")
        and keywords.get("include_in_schema", "") != "False"
    ):
        if "APIEx" not in examples:
            general_violation.append(
                f"'{router_name}' > '{function.__name__}': missing API example"
            )
        if "PythonEx" not in examples:
            general_violation.append(
                f"'{router_name}' > '{function.__name__}': missing Python example"
            )
    # Check if a POST endpoint excluded from the schema has a Python example
    if (
        (keywords.get("include_in_schema", "") == "False")
        and ("POST" in keywords.get("methods", ""))
        and ("PythonEx" not in examples)
    ):
        general_violation.append(
            f"'{router_name}' > '{function.__name__}': is excluded from the"
            "api schema but doesn't have a Python example."
        )
        if "APIEx" in examples:
            general_violation.append(
                f"'{router_name}' > '{function.__name__}': endpoint excluded from the"
                "api schema but has an API example."
            )

    return general_violation


def check_api_example_violations(
    examples: str, router_name: str, model: Optional[str], function: Any
) -> List[str]:
    """Check for API example violations in the router command examples.

    Criteria
    --------
    - When using models, at least one example using all required standard parameters.
    - It cannot use any provider specific parameters here.
    - It should not specify the provider field.
    """
    api_example_violation: List[str] = []

    parsed_examples = parse_example_string(examples)

    # Check model endpoint example criteria
    if model and "APIEx" in parsed_examples:
        required_fields = get_required_fields(model.strip("'"))
        for api_example in parsed_examples["APIEx"]:
            params = ast.literal_eval(api_example.get("params", "{}"))
            if set(params.keys()) == set(required_fields):
                break
        else:
            api_example_violation.append(
                f"'{router_name}' > '{function.__name__}': missing example with required fields only > {required_fields}"
            )

    return api_example_violation


def check_router_command_examples() -> List[str]:
    """Check if the router command examples satisfy criteria.

    Criteria
    --------
    General:
    - All endpoints should have examples.
    - If any endpoint is excluded from the schema it only needs to contain a Python example.
    - POST method examples should have both API and Python examples,
      unless they are excluded from the schema.

    API examples:
    - At least one example using all required parameters.
    - It cannot use any provider specific parameters here.
    - It should not specify the provider field.
    """
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
                if decorator_details["decorator"] == "router.command":
                    keywords = decorator_details["keywords"]
                    examples = keywords.get("examples", [])
                    ### General checks ###
                    general_violation += check_general_example_violations(
                        keywords, examples, router_name, function
                    )
                    if examples:
                        ### API example checks ###
                        model = keywords.get("model", None)
                        api_example_violation += check_api_example_violations(
                            examples, router_name, model, function
                        )

    return general_violation + api_example_violation + python_example_violation
