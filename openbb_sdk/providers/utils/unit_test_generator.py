"""The unit test generator for the fetchers."""
import os
from typing import Any, Dict, List

from openbb_core.app.provider_interface import ProviderInterface
from openbb_provider.abstract.fetcher import Fetcher
from pydantic.fields import ModelField

from openbb_sdk.providers.utils.credentials_schema import test_credentials


def get_provider_fetchers(
    available_providers: List[str],
) -> Dict[str, Dict[str, Fetcher]]:
    """Return a list of all fetchers in the provider."""
    fetchers: Dict[str, Dict[str, Fetcher]] = {}

    for provider in available_providers:
        provider_loaded = __import__(f"openbb_{provider}")
        provider_variable = getattr(provider_loaded, f"{provider}_provider")
        fetcher_dict = provider_variable.fetcher_dict
        for fetcher_name, fetcher_class in fetcher_dict.items():
            if provider not in fetchers:
                fetchers[provider] = {}
            fetchers[provider][fetcher_name] = fetcher_class

    return fetchers


def generate_fetcher_unit_tests(path: str) -> None:
    """Generate the fetcher unit tests in the provider test folders."""
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("import pytest\nfrom openbb import obb\n")


def get_test_params(param_fields: Dict[str, ModelField]) -> Dict[str, Any]:
    """Get the test params for the fetcher based on the requires standard params."""
    test_params: Dict[str, Any] = {}
    for field_name, field in param_fields.items():
        if field.required and field.default:
            test_params[field_name] = field.default
        elif field.required and not field.default:
            example_dict = {
                "symbol": "AAPL",
                "symbols": ["AAPL", "MSFT"],
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "country": "Portugal",
                "countries": ["Portugal", "Spain"],
            }
            if field_name in example_dict:
                test_params[field_name] = example_dict[field_name]

            # TODO: This should be refactored to handle edge cases better
            # For example, the Forex symbol will fail as it would be AAPL.
            elif field.type_ == str:
                test_params[field_name] = "test"
            elif field.type_ == int:
                test_params[field_name] = 1
            elif field.type_ == float:
                test_params[field_name] = 1.0
            elif field.type_ == bool:
                test_params[field_name] = True

    return test_params


def write_test_credentials(path: str, provider: str) -> None:
    """Write the mocked credentials to the provider test folders."""
    credentials: Dict[str, str] = test_credentials.get(provider, {})

    template = """
test_credentials = obb.user.credentials.__dict__


@pytest.fixture(scope="module")
def vcr_config():
    return {{
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
         {credentials_str},
        ],
    }}

"""
    with open(path, "a") as f:
        f.write(template.format(credentials_str=str(credentials)))


def write_fetcher_unit_tests() -> None:
    """Write the fetcher unit tests to the provider test folders."""
    provider_interface = ProviderInterface()
    available_providers = provider_interface.available_providers
    provider_interface_map = provider_interface.map

    test_template = """
@pytest.mark.record_http
def test_{fetcher_name}(credentials=test_credentials):
    params = {params}

    fetcher = {fetcher_name}()
    result = fetcher.test(params, credentials)
    assert result is True
"""
    fetchers = get_provider_fetchers(available_providers=available_providers)
    provider_fetchers: Dict[str, Dict[str, str]] = {}

    for provider, fetcher_dict in fetchers.items():
        path = os.path.join("..", f"{provider}", "tests", "test_fetchers.py")
        generate_fetcher_unit_tests(path)

        for model_name, fetcher in fetcher_dict.items():
            fetcher_loaded = fetcher()
            fetcher_path = fetcher_loaded.__module__
            fetcher_name = fetcher_loaded.__class__.__name__

            if model_name not in provider_fetchers:
                provider_fetchers[model_name] = {}
            provider_fetchers[model_name][fetcher_name] = path

            # Check if the test is already in the file
            with open(path) as f:
                lines = f.readlines()
                for line in lines:
                    if fetcher_path in line and fetcher_name in line:
                        return

            with open(path, "a") as f:
                f.write(f"from {fetcher_path} import {fetcher_name}\n")

    for model_name, fetcher_dict in provider_fetchers.items():
        for fetcher_name, path in fetcher_dict.items():
            test_params = get_test_params(
                param_fields=provider_interface_map[model_name]["openbb"][
                    "QueryParams"
                ]["fields"]
            )

            if "forex" in fetcher_name.lower() and "symbol" in test_params:
                test_params["symbol"] = "EUR/USD"
            if "crypto" in fetcher_name.lower() and "symbol" in test_params:
                test_params["symbol"] = "BTC/USD"
            if "indices" in fetcher_name.lower() and "symbol" in test_params:
                test_params["symbol"] = "SPY"

            with open(path, "a") as f:
                test_code = test_template.format(
                    fetcher_name=fetcher_name,
                    params=test_params,
                    credentials={},
                )
                f.write(test_code)
                f.write("\n\n")
