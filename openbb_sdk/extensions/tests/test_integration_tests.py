"""Test the integration tests."""
from extensions.tests.utils.integration_tests_testers import (
    check_missing_integration_test_params,
    check_missing_integration_test_providers,
    get_module_functions,
    get_python_integration_tests,
)


def test_python_interface_integration_tests() -> None:
    """Test if there are any missing providers for integration tests."""
    integration_tests = get_python_integration_tests()
    functions = get_module_functions(integration_tests)
    missing_providers = check_missing_integration_test_providers(functions)

    assert not missing_providers, "\n".join(missing_providers)


def test_python_interface_integration_test_params() -> None:
    """Test if there are any missing params for integration tests."""
    integration_tests = get_python_integration_tests()
    functions = get_module_functions(integration_tests)
    missing_params = check_missing_integration_test_params(functions)

    assert not missing_params, "\n".join(missing_params)
