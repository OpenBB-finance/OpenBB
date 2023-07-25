"""Test the Query class."""
# pylint: disable=redefined-outer-name

from dataclasses import dataclass

import pytest
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query


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


def test_to_query_params(query):
    """Test to_query_params."""

    class StockEOD:
        """Mock StockEOD class."""

        open: float = 0.0
        high: float = 0.0

    standard_params = StockEOD()
    assert query.to_query_params(standard_params)


def test_filter_extra_params(query):
    """Test filter_extra_params."""

    @dataclass
    class StockEOD:
        """Mock ExtraParams dataclass."""

        sort: str = "desc"

    extra_params = StockEOD()
    extra_params = query.filter_extra_params(extra_params, "fmp")
    print(extra_params)
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


@pytest.mark.skip(reason="TODO: see how to properly mock the execute method")
def test_execute(query):
    """Test execute."""
    assert query.execute()
