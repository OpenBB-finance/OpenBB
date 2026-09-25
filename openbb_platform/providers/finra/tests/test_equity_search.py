"""Tests for the equity search model."""

import asyncio
import json
from urllib.parse import urlparse

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_finra.models.equity_search import (
    FinraEquitySearchData,
    FinraEquitySearchFetcher,
)


def _fetch(params):
    """Run the fetcher."""
    return asyncio.run(FinraEquitySearchFetcher.fetch_data(params, {}))


class TestSearch:
    """Securities are searched in the Market Data Center."""

    def test_keyword(self, fake_session, response):
        """A keyword returns distinct listings with their identifiers."""
        fake_session("equity_search")
        result = _fetch({"query": "apple"})

        assert all(isinstance(row, FinraEquitySearchData) for row in result)
        apple = result[0]

        assert apple.symbol == "AAPL"
        assert apple.isin == "US0378331005"
        assert apple.exchange == "XNAS"
        assert apple.security_type == "Stock"
        assert apple.listing_market == "NASDAQ"
        assert apple.composite_market == "USCOMP"
        assert urlparse(apple.url or "").query == "query=19:0P000000GY"
        assert len({row.quote_symbol for row in result}) == len(result)

    def test_is_symbol(self, fake_session, response):
        """Only exact symbol matches are kept."""
        fake_session("equity_search")
        result = _fetch({"query": "apple", "is_symbol": True})

        assert result == []

    def test_condition(self, fake_session, response):
        """The security type selects the search condition."""
        session = fake_session(
            responder=lambda call: response(
                200,
                "\n"
                if urlparse(call["url"]).path == "/finralogin.jsp"
                else '{"id": "1"}',
            )
        )

        with pytest.raises(EmptyDataError, match="No security matched 'SPY'"):
            _fetch({"query": " SPY ", "security_type": "etf"})

        assert session.calls[1]["params"]["condition"] == "FE"

    def test_blank_query(self, fake_session, response):
        """A blank query is refused before any request."""
        session = fake_session(responder=lambda call: response(500))

        with pytest.raises(OpenBBError, match="Enter a symbol"):
            _fetch({"query": "  "})

        assert session.calls == []

    def test_duplicates_and_missing_ids(self, fake_session, response):
        """Repeated listings are dropped and missing ids leave no URL."""
        records = [
            {"AC001": "ZZZ", "Ticker": "126.1.ZZZ", "LS01Z": "EXTP$$$LTS"},
            {"AC001": "ZZZ", "Ticker": "126.1.ZZZ"},
        ]
        fake_session(
            responder=lambda call: response(
                200,
                "\n"
                if urlparse(call["url"]).path == "/finralogin.jsp"
                else json.dumps({"result": records}),
            )
        )
        result = _fetch({"query": "ZZZ"})

        assert len(result) == 1
        assert result[0].symbol == "ZZZ"
        assert result[0].url is None
        assert result[0].exchange == "EXTP$$$LTS"
