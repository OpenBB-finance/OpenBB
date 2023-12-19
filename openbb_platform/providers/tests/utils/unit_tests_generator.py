"""The unit test generator for the fetchers."""
from datetime import date
from pathlib import Path
from typing import Any, Dict, Tuple

from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.registry import RegistryLoader
from openbb_core.provider.utils.helpers import to_snake_case
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from providers.tests.utils.credentials_schema import test_credentials

PROVIDERS_PATH = Path(__file__).parent.parent.parent.resolve()


def get_provider_fetchers() -> Dict[str, Dict[str, Fetcher]]:
    """Get the fetchers from the provider registry."""
    registry = RegistryLoader.from_extensions()
    provider_fetcher_map: Dict[str, Dict[str, Fetcher]] = {}
    for provider_name, provider_cls in registry.providers.items():
        provider_fetcher_map[provider_name] = {}
        for fetcher_name, fetcher_cls in provider_cls.fetcher_dict.items():
            provider_fetcher_map[provider_name][fetcher_name] = fetcher_cls
    return provider_fetcher_map


def generate_fetcher_unit_tests(path: Path) -> None:
    """Generate the fetcher unit tests in the provider test folders."""
    if not path.exists():
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(
                "from datetime import datetime\n"
                "import pytest\nfrom openbb_core.app.service.user_service import UserService\n"
            )


def get_test_params(param_fields: Dict[str, FieldInfo]) -> Dict[str, Any]:
    """Get the test params for the fetcher based on the requires standard params."""
    test_params: Dict[str, Any] = {}
    for field_name, field in param_fields.items():
        if field.is_required() and field.default is not PydanticUndefined:
            test_params[field_name] = field.default
        elif field.is_required() or field.default is PydanticUndefined:
            example_dict = {
                "symbol": "AAPL",
                "symbols": "AAPL,MSFT",
                "start_date": date(2023, 1, 1),
                "end_date": date(2023, 6, 6),
                "country": "Portugal",
                "date": date(2023, 1, 1),
                "countries": ["portugal", "spain"],
            }
            if field_name in example_dict:
                test_params[field_name] = example_dict[field_name]
            elif field.annotation == str:
                test_params[field_name] = "test"
            elif field.annotation == int:
                test_params[field_name] = 1
            elif field.annotation == float:
                test_params[field_name] = 1.0
            elif field.annotation == bool:
                test_params[field_name] = True

        # This makes sure that the unit test are reproducible by fixing the date
        elif not field.is_required() and field_name in [
            "start_date",
            "end_date",
            "date",
        ]:
            if field_name == "start_date":
                test_params[field_name] = date(2023, 1, 1)
            elif field_name == "end_date":
                test_params[field_name] = date(2023, 6, 6)
            elif field_name == "date":
                test_params[field_name] = date(2023, 1, 1)
    return test_params


def write_test_credentials(path: str, provider: str) -> None:
    """Write the mocked credentials to the provider test folders."""
    credentials: Tuple[str, str] = test_credentials.get(
        provider, ("token", "MOCK_TOKEN")
    )

    template = """
test_credentials = UserService().default_user_settings.credentials.model_dump(mode="json")


@pytest.fixture(scope="module")
def vcr_config():
    return {{
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            {credentials_str},
        ],
    }}
"""
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(template.format(credentials_str=str(credentials)))


def check_pattern_in_file(file_path: str, pattern: str) -> bool:
    """Check if a pattern is in a file."""
    with open(file_path, encoding="utf-8", newline="\n") as f:
        lines = f.readlines()
        for line in lines:
            if pattern in line:
                return True
    return False


def write_fetcher_unit_tests() -> None:
    """Write the fetcher unit tests to the provider test folders."""
    provider_interface = ProviderInterface()
    provider_interface_map = provider_interface.map

    fetchers = get_provider_fetchers()
    provider_fetchers: Dict[str, Dict[str, str]] = {}

    for provider, fetcher_dict in fetchers.items():
        path = PROVIDERS_PATH / provider / "tests" / f"test_{provider}_fetchers.py"
        generate_fetcher_unit_tests(path)

        for model_name, fetcher in fetcher_dict.items():
            fetcher_loaded = fetcher()
            fetcher_path = fetcher_loaded.__module__
            fetcher_name = fetcher_loaded.__class__.__name__

            if model_name not in provider_fetchers:
                provider_fetchers[model_name] = {}
            provider_fetchers[model_name][fetcher_name] = path

            pattern = f"from {fetcher_path}"
            if not check_pattern_in_file(path, pattern):
                with open(path, "a", encoding="utf-8", newline="\n") as f:
                    f.write(f"{pattern} import {fetcher_name}\n")

        pattern = "vcr_config"
        if not check_pattern_in_file(path, pattern):
            write_test_credentials(path, provider)

    test_template = """
@pytest.mark.record_http
def test_{fetcher_name_snake}(credentials=test_credentials):
    params = {params}

    fetcher = {fetcher_name}()
    result = fetcher.test(params, credentials)
    assert result is None
"""

    for model_name, fetcher_dict in provider_fetchers.items():
        for fetcher_name, path in fetcher_dict.items():
            pattern = f"{fetcher_name}()"
            if check_pattern_in_file(path, pattern):
                continue

            # Add logic here to grab the necessary standardized params and credentials
            test_params = get_test_params(
                param_fields=provider_interface_map[model_name]["openbb"][
                    "QueryParams"
                ]["fields"]
            )

            if "currency" in fetcher_name.lower() and "symbol" in test_params:
                test_params["symbol"] = "EUR/USD"
            if "crypto" in fetcher_name.lower() and "symbol" in test_params:
                test_params["symbol"] = "BTC/USD"
            if "indices" in fetcher_name.lower() and "symbol" in test_params:
                test_params["symbol"] = "DJI"
            if "future" in fetcher_name.lower() and "symbol" in test_params:
                test_params["symbol"] = "ES"
            if (
                "european" in fetcher_name.lower()
                and "symbol" in test_params
                and "index" in fetcher_name.lower()
            ):
                test_params["symbol"] = "BUKBUS"
            if "european" in fetcher_name.lower() and "symbol" in test_params:
                test_params["symbol"] = "BUKBUS"

            with open(path, "a", encoding="utf-8", newline="\n") as f:
                test_code = test_template.format(
                    fetcher_name_snake=to_snake_case(fetcher_name),
                    fetcher_name=fetcher_name,
                    params=test_params,
                    credentials={},
                )
                f.write(test_code)
                f.write("\n\n")


if __name__ == "__main__":
    write_fetcher_unit_tests()
