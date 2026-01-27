"""Test the Query class."""

# pylint: disable=redefined-outer-name

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Query as FastAPIQuery
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from pydantic import BaseModel, ConfigDict


class MockBaseModel(BaseModel):
    """Mock QueryParams class."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


def create_mock_query():
    """Mock query."""

    class EquityHistorical:
        """Mock EquityHistorical class."""

        start_date = "2020-01-01"
        end_date = "2020-01-05"
        symbol = "AAPL"

    return EquityHistorical()


def create_mock_extra_params():
    """Mock ExtraParams dataclass."""

    @dataclass
    class EquityHistorical:
        """Mock ExtraParams dataclass."""

        sort: FastAPIQuery = FastAPIQuery(default="desc", title="mock_provider")

    return EquityHistorical()


@pytest.fixture(scope="module")
def query():
    """Set up query."""
    return Query(
        cc=CommandContext(),
        provider_choices=ProviderChoices(provider="fmp"),
        standard_params=StandardParams(),
        extra_params=ExtraParams(),
    )


def test_init(query):
    """Test init."""
    assert query


@pytest.fixture
def mock_registry():
    """Mock registry."""
    with patch(
        "openbb_core.app.provider_interface.ProviderInterface"
    ) as mock_get_provider_interface:
        mock_registry = MagicMock()
        mock_get_provider_interface.return_value.build_registry.return_value = (
            mock_registry
        )
        yield mock_registry


@pytest.fixture
def query_instance():
    """Set up query."""
    standard_params = create_mock_query()
    extra_params = create_mock_extra_params()

    cc = CommandContext()
    setattr(
        cc.user_settings.credentials,
        "fmp_api_key",
        "1234",  # pylint: disable=no-member
    )

    return Query(
        cc=cc,
        provider_choices=ProviderChoices(provider="fmp"),
        standard_params=standard_params,
        extra_params=extra_params,
    )


def test_filter_extra_params(query):
    """Test filter_extra_params."""

    @dataclass
    class MockExtraFields:
        """Mock extra fields with same structure as extra_params."""

        sort: FastAPIQuery = FastAPIQuery(default="desc", title="mock_provider")

    # Mock the provider_interface.params property
    mock_provider_interface = MagicMock()
    mock_provider_interface.params = {"EquityHistorical": {"extra": MockExtraFields}}

    original_pi = query.provider_interface
    query.provider_interface = mock_provider_interface
    try:
        extra_params = create_mock_extra_params()
        extra_params = query.filter_extra_params(extra_params, "fmp")

        assert isinstance(extra_params, dict)
        # "sort" has default "desc" and value is also "desc", so it's not filtered
        # Also fmp is not in providers (only polygon), so it won't be included
        assert len(extra_params) == 0
    finally:
        query.provider_interface = original_pi


def test_filter_extra_params_wrong_param(query):
    """Test filter_extra_params filters out params not supported by provider."""

    @dataclass
    class EquityHistorical:
        """Mock ExtraParams dataclass."""

        # sort is only for polygon, not fmp - should be filtered out with warning
        sort: FastAPIQuery = FastAPIQuery(default="desc", title="mock_provider")
        # limit is for fmp - should be included if value differs from default
        limit: FastAPIQuery = FastAPIQuery(default=4, title="fmp")

    @dataclass
    class MockExtraFields:
        """Mock extra fields with same structure as extra_params."""

        sort: FastAPIQuery = FastAPIQuery(default="desc", title="mock_provider")
        limit: FastAPIQuery = FastAPIQuery(default=4, title="fmp")

    # Mock the provider_interface.params property
    mock_provider_interface = MagicMock()
    mock_provider_interface.params = {"EquityHistorical": {"extra": MockExtraFields}}

    original_pi = query.provider_interface
    query.provider_interface = mock_provider_interface
    try:
        # Create with non-default values to trigger filtering
        extra_params = EquityHistorical(
            sort=FastAPIQuery(
                default="asc", title="mock_provider"
            ),  # non-default value
            limit=FastAPIQuery(default=10, title="fmp"),  # non-default value
        )
        extra = query.filter_extra_params(extra_params, "fmp")
        assert isinstance(extra, dict)
        # Only limit should be included (fmp provider)
        # sort should be filtered out with warning (polygon only)
        assert "limit" in extra
        assert "sort" not in extra
    finally:
        query.provider_interface = original_pi


@pytest.mark.asyncio
async def test_execute_method_fake_credentials(query_instance: Query, mock_registry):
    """Test execute method without setting credentials."""
    mock_fetch_result = MockBaseModel()
    mock_registry.fetch.return_value = mock_fetch_result

    with pytest.raises(Exception):
        await query_instance.execute()
