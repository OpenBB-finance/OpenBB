"""Test the Query class."""
# pylint: disable=redefined-outer-name

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from pydantic import BaseModel


def create_mock_query():
    """Mock query."""

    class StockEOD:
        """Mock StockEOD class."""

        start_date = "2020-01-01"
        end_date = "2020-01-05"
        symbol = "AAPL"

    return StockEOD()


def create_mock_extra_params():
    """Mock ExtraParams dataclass."""

    @dataclass
    class StockEOD:
        """Mock ExtraParams dataclass."""

        sort: str = "desc"

    return StockEOD()


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


def test_filter_extra_params(query):
    """Test filter_extra_params."""
    extra_params = create_mock_extra_params()
    extra_params = query.filter_extra_params(extra_params, "fmp")

    assert isinstance(extra_params, dict)
    assert len(extra_params) == 0


def test_filter_extra_params_wrong_param(query):
    """Test filter_extra_params."""

    @dataclass
    class StockEOD:
        """Mock ExtraParams dataclass."""

        sort: str = "desc"
        limit: int = 4

    extra_params = StockEOD()

    assert not query.filter_extra_params(extra_params, "fmp")


@pytest.fixture
def mock_registry():
    """Mock registry."""
    with patch(
        "openbb_core.app.provider_interface.get_provider_interface"
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
    setattr(cc.user_settings.credentials, "fmp_api_key", "1234")

    return Query(
        cc=cc,
        provider_choices=ProviderChoices(provider="fmp"),
        standard_params=standard_params,
        extra_params=extra_params,
    )


def test_execute_method_fake_credentials(query_instance, mock_registry):
    """Test execute method without setting credentials."""
    mock_fetch_result = BaseModel()  # Replace with an actual instance of BaseModel
    mock_registry.fetch.return_value = mock_fetch_result

    with pytest.raises(Exception):
        query_instance.execute()
