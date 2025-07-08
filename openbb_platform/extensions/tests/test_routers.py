"""Test the routers."""

from .utils.router_testers import (
    check_router_command_examples,
    check_router_function_models,
    check_router_model_functions_signature,
)


def test_router_function_models() -> None:
    """Test if the models in the router functions exist in the provider interface map."""
    missing_models = check_router_function_models()
    assert not missing_models, "\n".join(missing_models)


def test_router_model_functions_signature() -> None:
    """Test if the router functions have the correct signature."""
    missing_args = check_router_model_functions_signature()
    assert not missing_args, "\n".join(missing_args)


def test_router_examples_rules() -> None:
    """Test if the router examples follow certain rules.

    Rules:
    - All endpoints should have examples.
    - At least one example using all required parameters.
    - All params are valid for the command.
    """
    invalid_examples = check_router_command_examples()
    assert not invalid_examples, "\n".join(sorted(invalid_examples))
