"""Shared fixtures for the openbb-core test suite.

These fixtures intentionally avoid importing or relying on any non-core
OpenBB packages so the suite can be exercised against just the
``openbb-core`` distribution (optionally with the ``[pandas]`` extra).
"""

from typing import Any

import pytest

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.provider import Provider
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.registry import Registry
from openbb_core.provider.standard_models.available_indicators import (
    AvailableIndicatorsData,
    AvailableIndicesQueryParams,
)


class _FakeQueryParams(AvailableIndicesQueryParams):
    """Concrete query params for the primary fake provider."""


class _FakeData(AvailableIndicatorsData):
    """Provider-specific data model that adds a single extension field."""

    extra_field: str | None = None


class _FakeFetcher(Fetcher[_FakeQueryParams, list[_FakeData]]):
    """Minimal list-returning fetcher used by the primary fake provider."""

    require_credentials = True

    @staticmethod
    def transform_query(params: dict[str, Any]) -> _FakeQueryParams:
        return _FakeQueryParams(**params)

    @staticmethod
    def extract_data(
        query: _FakeQueryParams, credentials: dict[str, str] | None
    ) -> list[dict[str, Any]]:
        return [{"symbol": "FAKE"}]

    @staticmethod
    def transform_data(
        query: _FakeQueryParams, data: list[dict[str, Any]], **kwargs
    ) -> list[_FakeData]:
        return [_FakeData(**row) for row in data]


class _SecondFakeQueryParams(AvailableIndicesQueryParams):
    """Query params for the secondary fake provider — adds a provider-specific filter."""

    region: str | None = None


class _SecondFakeData(AvailableIndicatorsData):
    """Data model for the secondary fake provider — adds a different extension field."""

    second_extra: int | None = None


class _SecondFakeFetcher(Fetcher[_SecondFakeQueryParams, list[_SecondFakeData]]):
    """Fetcher used to test multi-provider model registration."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> _SecondFakeQueryParams:
        return _SecondFakeQueryParams(**params)

    @staticmethod
    def extract_data(
        query: _SecondFakeQueryParams, credentials: dict[str, str] | None
    ) -> list[dict[str, Any]]:
        return [{"symbol": "FAKE2"}]

    @staticmethod
    def transform_data(
        query: _SecondFakeQueryParams,
        data: list[dict[str, Any]],
        **kwargs,
    ) -> list[_SecondFakeData]:
        return [_SecondFakeData(**row) for row in data]


class _SingleResultFetcher(Fetcher[_FakeQueryParams, _FakeData]):
    """Fetcher whose return type is a single ``Data`` instance, not a list.

    Used to verify ``RegistryMap`` distinguishes list vs. scalar return types.
    """

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> _FakeQueryParams:
        return _FakeQueryParams(**params)

    @staticmethod
    def extract_data(
        query: _FakeQueryParams, credentials: dict[str, str] | None
    ) -> dict[str, Any]:
        return {"symbol": "ONE"}

    @staticmethod
    def transform_data(
        query: _FakeQueryParams, data: dict[str, Any], **kwargs
    ) -> _FakeData:
        return _FakeData(**data)


@pytest.fixture(scope="session")
def fake_provider_name() -> str:
    """Return the canonical primary fake provider name."""
    return "fake"


@pytest.fixture(scope="session")
def second_fake_provider_name() -> str:
    """Return the secondary fake provider name."""
    return "fake_two"


@pytest.fixture(scope="session")
def fake_model_name() -> str:
    """Return the standard model name registered by the fake providers."""
    return "AvailableIndicators"


@pytest.fixture(scope="session")
def single_result_model_name() -> str:
    """Return the model name registered by the single-result fetcher."""
    return "SingleResult"


@pytest.fixture(scope="session")
def fake_credential_names(fake_provider_name: str) -> list[str]:
    """Return the namespaced credential keys expected on the primary provider."""
    return [f"{fake_provider_name}_api_key", f"{fake_provider_name}_api_secret"]


@pytest.fixture
def fake_provider(
    fake_provider_name: str,
    fake_model_name: str,
    single_result_model_name: str,
) -> Provider:
    """Primary fake provider — multi-credential, list and single-result fetchers."""
    return Provider(
        name=fake_provider_name,
        description="Fake provider used to exercise core wiring without external deps.",
        website="https://example.invalid",
        credentials=["api_key", "api_secret"],
        fetcher_dict={
            fake_model_name: _FakeFetcher,
            single_result_model_name: _SingleResultFetcher,
        },
    )


@pytest.fixture
def second_fake_provider(
    second_fake_provider_name: str, fake_model_name: str
) -> Provider:
    """Second fake provider sharing the same standard model — no credentials."""
    return Provider(
        name=second_fake_provider_name,
        description="Second fake provider — exercises multi-provider model merging.",
        website="https://example.invalid",
        credentials=None,
        fetcher_dict={fake_model_name: _SecondFakeFetcher},
    )


@pytest.fixture
def fake_registry(fake_provider: Provider) -> Registry:
    """Registry containing only the primary fake provider."""
    registry = Registry()
    registry.include_provider(fake_provider)
    return registry


@pytest.fixture
def multi_provider_registry(
    fake_provider: Provider, second_fake_provider: Provider
) -> Registry:
    """Registry containing both fake providers — for multi-provider scenarios."""
    registry = Registry()
    registry.include_provider(fake_provider)
    registry.include_provider(second_fake_provider)
    return registry


@pytest.fixture
def standard_data_cls() -> type[Data]:
    """Re-export the standard ``Data`` subclass used as the model parent."""
    return AvailableIndicatorsData


@pytest.fixture
def standard_query_cls() -> type[QueryParams]:
    """Re-export the standard ``QueryParams`` subclass used as the model parent."""
    return AvailableIndicesQueryParams
