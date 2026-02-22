"""Root configuration for pytest."""

# flake8: noqa: S101
# pylint: disable=unused-argument,unused-import

import os
from pathlib import Path
from typing import Any

import pytest  # noqa: F401
import requests

ROOT_DIR = Path(__file__).parent


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _extract_provider_from_param(value: Any) -> str | None:
    if isinstance(value, dict):
        provider = value.get("provider")
        if isinstance(provider, str) and provider.strip():
            return provider.strip().lower()
        for nested in value.values():
            found = _extract_provider_from_param(nested)
            if found:
                return found
        return None
    if isinstance(value, (list, tuple, set)):
        for nested in value:
            found = _extract_provider_from_param(nested)
            if found:
                return found
    return None


def _load_provider_credentials() -> tuple[dict[str, list[str]], set[str]]:
    provider_requirements: dict[str, list[str]] = {}
    available_credentials: set[str] = set()

    try:
        # Imported lazily to avoid import-time cost for non-platform pytest runs.
        from openbb_core.app.model.credentials import Credentials
        from openbb_core.app.provider_interface import ProviderInterface

        provider_requirements = {
            provider.lower(): [cred.lower() for cred in creds]
            for provider, creds in ProviderInterface().credentials.items()
            if creds
        }

        credentials = Credentials()
        for field_name in Credentials.model_fields:
            value = getattr(credentials, field_name, None)
            if value is None:
                continue
            if hasattr(value, "get_secret_value"):
                if value.get_secret_value():
                    available_credentials.add(field_name.lower())
            elif isinstance(value, str):
                if value.strip():
                    available_credentials.add(field_name.lower())
            else:
                available_credentials.add(field_name.lower())
    except Exception:
        # If credential loading fails, do not block test collection.
        return {}, set()

    return provider_requirements, available_credentials


SKIP_MISSING_PROVIDER_CREDENTIALS = _bool_env(
    "OPENBB_SKIP_MISSING_PROVIDER_CREDENTIALS", default=True
)
PROVIDER_REQUIREMENTS, AVAILABLE_CREDENTIALS = _load_provider_credentials()


def pytest_configure():
    """Set environment variables for testing."""
    os.environ["OPENBB_AUTO_BUILD"] = "true"


def pytest_collection_modifyitems(config, items):
    """Modify test collection to ensure cleanup-dependent tests run first."""
    # Find tests that should run early (checking clean state)
    early_tests: list = []
    other_tests: list = []

    for item in items:
        # Tests that check repository state should run first
        if (
            "repository_state" in item.name.lower()
            or "extension_map" in item.name.lower()
            or "test_logging_service" in item.name.lower()
            or item.get_closest_marker("order")
        ):
            early_tests.append(item)
        else:
            other_tests.append(item)

        if (
            SKIP_MISSING_PROVIDER_CREDENTIALS
            and item.get_closest_marker("integration")
            and hasattr(item, "callspec")
            and PROVIDER_REQUIREMENTS
        ):
            provider = None
            callspec = getattr(item, "callspec", None)
            params = getattr(callspec, "params", {})
            for param_value in params.values():
                provider = _extract_provider_from_param(param_value)
                if provider:
                    break

            if provider and provider in PROVIDER_REQUIREMENTS:
                required = PROVIDER_REQUIREMENTS[provider]
                missing = [cred for cred in required if cred not in AVAILABLE_CREDENTIALS]
                if missing:
                    item.add_marker(
                        pytest.mark.skip(
                            reason=(
                                "Missing provider credentials for integration test "
                                f"({provider}: {', '.join(missing)})."
                            )
                        )
                    )

    # Sort early tests by their order marker if present
    early_tests.sort(
        key=lambda x: (
            getattr(x.get_closest_marker("order"), "args", [999])[0]
            if x.get_closest_marker("order")
            else 999
        )
    )

    # Reorder: early tests first, then others
    items[:] = early_tests + other_tests


@pytest.fixture(scope="session", autouse=True)
def normalize_integration_loopback_host():
    """Map hardcoded integration URLs to a configurable local API host/port."""
    api_host = (os.getenv("OPENBB_TEST_API_HOST") or "127.0.0.1").strip() or "127.0.0.1"
    api_port = (os.getenv("OPENBB_TEST_API_PORT") or "8000").strip() or "8000"
    target_prefix = f"://{api_host}:{api_port}"
    source_prefixes = (
        "://0.0.0.0:8000",
        "://127.0.0.1:8000",
        "://localhost:8000",
    )
    original_request = requests.sessions.Session.request

    def patched_request(self, method, url, *args, **kwargs):
        normalized_url = url
        if isinstance(url, str):
            for source_prefix in source_prefixes:
                if source_prefix in normalized_url:
                    normalized_url = normalized_url.replace(source_prefix, target_prefix)
        return original_request(self, method, normalized_url, *args, **kwargs)

    requests.sessions.Session.request = patched_request
    try:
        yield
    finally:
        requests.sessions.Session.request = original_request
