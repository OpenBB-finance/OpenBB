"""Tests for the equity short interest model."""

import asyncio

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_finra.models.equity_short_interest import (
    FinraShortInterestData,
    FinraShortInterestFetcher,
)


def _fetch(params):
    """Run the fetcher."""
    return asyncio.run(FinraShortInterestFetcher.fetch_data(params, {}))


class TestShortInterest:
    """Consolidated short interest is read for every symbol in one request."""

    def test_history(self, fake_session, response):
        """Every cycle of every symbol is returned in symbol and date order."""
        fake_session("short_interest")
        result = _fetch({"symbol": "AAPL,BRK.B"})

        assert all(isinstance(row, FinraShortInterestData) for row in result)
        assert {row.symbol for row in result} == {"AAPL", "BRKB"}

        apple = [row for row in result if row.symbol == "AAPL"]
        dates = [row.settlement_date for row in apple]

        assert dates == sorted(dates)
        assert all(isinstance(row.revised, bool) for row in result)
        assert all(isinstance(row.stock_split, bool) for row in result)
        assert {row.market_class for row in apple} == {
            "Nasdaq Global Select and Global Market"
        }

    def test_split_cycle_is_flagged(self, fake_session, response):
        """The cycle of the 2020 AAPL split carries the split flag."""
        fake_session("short_interest")
        result = _fetch({"symbol": "AAPL,BRK.B"})

        assert any(row.stock_split for row in result if row.symbol == "AAPL")

    def test_request_shape(self, fake_session, response):
        """Class shares are sent in the dataset's punctuation-free form."""
        session = fake_session("short_interest")
        _fetch({"symbol": "AAPL,BRK.B"})

        assert session.calls[0]["json"]["domainFilters"] == [
            {"fieldName": "symbolCode", "values": ["AAPL", "BRKB"]}
        ]

    def test_empty(self, fake_session, response):
        """An unknown symbol is empty."""
        fake_session(responder=lambda call: response(204))

        with pytest.raises(EmptyDataError, match="no short interest for ZZZZ"):
            _fetch({"symbol": "ZZZZ"})
