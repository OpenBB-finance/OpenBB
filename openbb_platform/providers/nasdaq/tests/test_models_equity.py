"""Tests for the Nasdaq equity models."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_nasdaq.models.company_news import NasdaqCompanyNewsFetcher
from openbb_nasdaq.models.crypto_historical import NasdaqCryptoHistoricalFetcher
from openbb_nasdaq.models.equity_historical import NasdaqEquityHistoricalFetcher
from openbb_nasdaq.models.equity_info import NasdaqEquityInfoFetcher
from openbb_nasdaq.models.equity_quote import (
    NasdaqEquityQuoteFetcher,
    _split_range,
)
from openbb_nasdaq.models.equity_search import NasdaqEquitySearchFetcher
from openbb_nasdaq.models.equity_short_interest import (
    NasdaqEquityShortInterestFetcher,
)
from openbb_nasdaq.models.etf_historical import NasdaqEtfHistoricalFetcher
from openbb_nasdaq.models.index_historical import NasdaqIndexHistoricalFetcher

from .conftest import patch_asset_class, patch_data

SESSION = {
    "date": date(2026, 7, 24),
    "open": 1.0,
    "high": 2.0,
    "low": 0.5,
    "close": 1.0,
    "volume": 100.0,
}


class TestEquityQuote:
    """Cover the equity quote model."""

    @staticmethod
    def _payload():
        """Return an info and summary pair."""
        return [
            {
                "symbol": "AAPL",
                "info": {
                    "companyName": "Apple Inc. Common Stock",
                    "exchange": "NASDAQ-GS",
                    "stockType": "Common Stock",
                    "isNasdaq100": True,
                    "marketStatus": "Closed",
                    "primaryData": {
                        "lastSalePrice": "$333.02",
                        "netChange": "+11.36",
                        "percentageChange": "+3.53%",
                        "volume": "47,489,726",
                        "bidPrice": "$332.00",
                        "askPrice": "$334.00",
                        "bidSize": "100",
                        "askSize": "200",
                        "lastTradeTimestamp": "Jul 24, 2026",
                    },
                },
                "summary": {
                    "summaryData": {
                        "PreviousClose": {"value": "$321.66"},
                        "FiftTwoWeekHighLow": {"value": "$400.00/$200.00"},
                        "TodayHighLow": {"value": "$335.00 - $330.00"},
                        "Sector": {"value": "Technology"},
                        "Industry": {"value": "Computer Manufacturing"},
                        "MarketCap": {"value": "5,000,000"},
                        "AverageVolume": {"value": "50,000,000"},
                        "OneYrTarget": {"value": "$400.00"},
                        "AnnualizedDividend": {"value": "1.04"},
                        "Yield": {"value": "0.31%"},
                        "ExDividendDate": {"value": "Aug 8, 2026"},
                        "DividendPaymentDate": {"value": "Aug 15, 2026"},
                    }
                },
            }
        ]

    def test_transforms_the_quote(self):
        """Every summary block field resolves."""
        query = NasdaqEquityQuoteFetcher.transform_query({"symbol": "AAPL"})
        rows = NasdaqEquityQuoteFetcher.transform_data(query, self._payload())

        assert rows[0].name == "Apple Inc. Common Stock"
        assert rows[0].last_price == pytest.approx(333.02)
        assert rows[0].change_percent == pytest.approx(0.0353)
        assert rows[0].year_high == 400
        assert rows[0].year_low == 200
        assert rows[0].high == 335
        assert rows[0].low == 330
        assert rows[0].dividend_yield == pytest.approx(0.0031)
        assert rows[0].ex_dividend_date == date(2026, 8, 8)
        assert rows[0].is_nasdaq_100 is True

    def test_fetches_both_blocks(self, monkeypatch):
        """The info and summary endpoints are both requested."""
        seen: list[str] = []
        patch_data(monkeypatch, {"companyName": "Apple"}, seen)
        query = NasdaqEquityQuoteFetcher.transform_query({"symbol": "aapl"})
        raw = asyncio.run(NasdaqEquityQuoteFetcher.aextract_data(query, None))

        assert len(seen) == 2
        assert raw[0]["symbol"] == "AAPL"

    def test_warns_on_a_bad_symbol(self, monkeypatch):
        """A symbol the endpoints reject warns and is skipped."""

        async def _data(path, **kwargs):
            raise OpenBBError("unknown symbol")

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        query = NasdaqEquityQuoteFetcher.transform_query({"symbol": "NOPE"})

        with pytest.warns(UserWarning, match="NOPE"), pytest.raises(EmptyDataError):
            asyncio.run(NasdaqEquityQuoteFetcher.aextract_data(query, None))

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("$400.00/$200.00", (400.0, 200.0)),
            ("$200.00 - $400.00", (400.0, 200.0)),
            ("no separator", (None, None)),
            (None, (None, None)),
            ("$400.00/N/A", (None, None)),
        ],
    )
    def test_split_range(self, value, expected):
        """A display range splits into a high and a low."""
        assert _split_range(value) == expected


class TestEquityInfo:
    """Cover the company profile model."""

    def test_transforms_the_profile(self):
        """The profile block and quote header are merged."""
        query = NasdaqEquityInfoFetcher.transform_query({"symbol": "AAPL"})
        rows = NasdaqEquityInfoFetcher.transform_data(
            query,
            [
                {
                    "symbol": "AAPL",
                    "profile": {
                        "CompanyName": {"value": "Apple Inc."},
                        "CompanyDescription": {"value": "Designs phones."},
                        "Industry": {"value": "Computer Manufacturing"},
                        "Sector": {"value": "Technology"},
                        "Region": {"value": "North America"},
                        "Address": {"value": "One Apple Park Way"},
                        "Phone": {"value": "408 996 1010"},
                    },
                    "info": {
                        "companyName": "Apple Inc. Common Stock",
                        "exchange": "NASDAQ-GS",
                        "stockType": "Common Stock",
                        "isNasdaq100": True,
                    },
                }
            ],
        )

        assert rows[0].name == "Apple Inc."
        assert rows[0].long_description == "Designs phones."
        assert rows[0].sector == "Technology"
        assert rows[0].exchange == "NASDAQ-GS"

    def test_falls_back_to_the_quote_name(self):
        """A profile without a name uses the quote header."""
        query = NasdaqEquityInfoFetcher.transform_query({"symbol": "AAPL"})
        rows = NasdaqEquityInfoFetcher.transform_data(
            query,
            [{"symbol": "AAPL", "profile": {}, "info": {"companyName": "Apple Inc."}}],
        )

        assert rows[0].name == "Apple Inc."


class TestEquitySearch:
    """Cover the symbol directory search."""

    def test_reads_the_directory(self, monkeypatch, directory_text):
        """The directory is downloaded and test issues are dropped."""
        monkeypatch.setattr(
            "openbb_nasdaq.utils.helpers.get_nasdaq_directory",
            lambda *a: directory_text,
        )
        query = NasdaqEquitySearchFetcher.transform_query({})
        raw = NasdaqEquitySearchFetcher.extract_data(query, None)
        rows = NasdaqEquitySearchFetcher.transform_data(query, raw)

        assert {r.symbol for r in rows} == {"AAPL"}
        assert rows[0].cqs_symbol == "AAPL"

    def test_filters_by_etf(self, directory_text):
        """The ETF flag narrows the directory in both directions."""
        etfs = NasdaqEquitySearchFetcher.transform_data(
            NasdaqEquitySearchFetcher.transform_query({"is_etf": True}), directory_text
        )
        stocks = NasdaqEquitySearchFetcher.transform_data(
            NasdaqEquitySearchFetcher.transform_query({"is_etf": False}),
            directory_text,
        )

        assert [r.symbol for r in etfs] == ["QQQ"]
        assert [r.symbol for r in stocks] == ["AAPL"]

    def test_filters_by_query(self, directory_text):
        """A query matches the symbol or the security name."""
        rows = NasdaqEquitySearchFetcher.transform_data(
            NasdaqEquitySearchFetcher.transform_query({"query": "apple"}),
            directory_text,
        )

        assert [r.symbol for r in rows] == ["AAPL"]


class TestEquityShortInterest:
    """Cover the short interest model."""

    def test_derives_the_change(self):
        """The change and percent change are derived from the prior settlement."""
        query = NasdaqEquityShortInterestFetcher.transform_query({"symbol": "AAPL"})
        rows = NasdaqEquityShortInterestFetcher.transform_data(
            query,
            [
                {
                    "symbol": "AAPL",
                    "settlementDate": "07/15/2026",
                    "interest": "200",
                    "avgDailyShareVolume": "50",
                    "daysToCover": "4",
                },
                {
                    "symbol": "AAPL",
                    "settlementDate": "06/30/2026",
                    "interest": "100",
                    "avgDailyShareVolume": "50",
                    "daysToCover": "2",
                },
            ],
        )

        assert rows[0].settlement_date == date(2026, 7, 15)
        assert rows[0].previous_short_position == 100
        assert rows[0].change == 100
        assert rows[0].change_pct == pytest.approx(1.0)
        assert rows[1].change is None

    def test_first_settlement_has_no_change(self):
        """The oldest settlement has nothing to compare against."""
        query = NasdaqEquityShortInterestFetcher.transform_query({"symbol": "AAPL"})
        rows = NasdaqEquityShortInterestFetcher.transform_data(
            query,
            [
                {
                    "symbol": "AAPL",
                    "settlementDate": "06/30/2026",
                    "interest": "0",
                    "avgDailyShareVolume": "50",
                    "daysToCover": "2",
                },
                {
                    "symbol": "AAPL",
                    "settlementDate": "07/15/2026",
                    "interest": "100",
                    "avgDailyShareVolume": "50",
                    "daysToCover": "4",
                },
            ],
        )

        assert rows[-1].previous_short_position is None
        assert rows[0].change == 100
        assert rows[0].change_pct is None


class TestCompanyNews:
    """Cover the company news model."""

    @staticmethod
    def _rows():
        """Return two articles, one duplicated."""
        return [
            {
                "url": "/articles/a",
                "created": "Jul 25, 2026",
                "title": "Chip sell-off",
                "description": "Semis fall.",
                "publisher": "Barchart",
                "primarytopic": "Markets|topic",
                "image": "https://img/a.png",
                "related_symbols": ["spy|etf", "qqq|etf"],
                "requested_symbol": "SPY",
            },
            {
                "url": "/articles/a",
                "created": "Jul 25, 2026",
                "title": "Duplicate",
                "requested_symbol": "SPY",
            },
            {
                "url": "https://x/b",
                "created": "N/A",
                "title": "Undated",
                "requested_symbol": "SPY",
            },
        ]

    def test_deduplicates_and_qualifies_urls(self):
        """Repeat and undated articles drop, and relative URLs are qualified."""
        query = NasdaqCompanyNewsFetcher.transform_query({"symbol": "SPY"})
        rows = NasdaqCompanyNewsFetcher.transform_data(query, self._rows())

        assert len(rows) == 1
        assert rows[0].url == "https://www.nasdaq.com/articles/a"
        assert rows[0].symbols == "SPY,QQQ"
        assert rows[0].topic == "Markets"
        assert rows[0].images[0]["url"] == "https://img/a.png"

    def test_falls_back_to_the_requested_symbol(self):
        """An article without related symbols is tagged with the request."""
        query = NasdaqCompanyNewsFetcher.transform_query({"symbol": "SPY"})
        rows = NasdaqCompanyNewsFetcher.transform_data(
            query,
            [
                {
                    "url": "/a",
                    "created": "Jul 25, 2026",
                    "title": "Untagged",
                    "requested_symbol": "SPY",
                }
            ],
        )

        assert rows[0].symbols == "SPY"

    def test_filters_by_window(self):
        """Articles outside the requested window are dropped."""
        query = NasdaqCompanyNewsFetcher.transform_query(
            {"symbol": "SPY", "start_date": date(2026, 8, 1)}
        )

        assert NasdaqCompanyNewsFetcher.transform_data(query, self._rows()) == []

        query = NasdaqCompanyNewsFetcher.transform_query(
            {"symbol": "SPY", "end_date": date(2026, 1, 1)}
        )

        assert NasdaqCompanyNewsFetcher.transform_data(query, self._rows()) == []

    def test_requests_the_resolved_asset_class(self, monkeypatch):
        """The asset class is resolved per symbol and the fallback is requested."""
        seen: list[str] = []
        patch_asset_class(monkeypatch, "etf")
        patch_data(monkeypatch, {"rows": [{"url": "/a"}]}, seen)
        query = NasdaqCompanyNewsFetcher.transform_query({"symbol": "spy"})
        raw = asyncio.run(NasdaqCompanyNewsFetcher.aextract_data(query, None))

        assert "q=SPY%7Cetf" in seen[0]
        assert "fallback=true" in seen[0]
        assert raw[0]["requested_symbol"] == "SPY"

    def test_warns_on_a_failing_symbol(self, monkeypatch):
        """A symbol with no news warns and is skipped."""
        patch_asset_class(monkeypatch, "stocks")

        async def _data(path, **kwargs):
            raise OpenBBError("no news")

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        query = NasdaqCompanyNewsFetcher.transform_query({"symbol": "NOPE"})

        with pytest.warns(UserWarning, match="NOPE"), pytest.raises(EmptyDataError):
            asyncio.run(NasdaqCompanyNewsFetcher.aextract_data(query, None))


class TestPriceHistoryModels:
    """Cover the models that delegate to the shared price helper."""

    @pytest.mark.parametrize(
        ("fetcher", "asset_class"),
        [
            (NasdaqEquityHistoricalFetcher, "stocks"),
            (NasdaqEtfHistoricalFetcher, None),
            (NasdaqCryptoHistoricalFetcher, "crypto"),
        ],
        ids=["equity", "etf", "crypto"],
    )
    def test_delegates_with_its_asset_class(self, fetcher, asset_class, monkeypatch):
        """Each model requests its own asset class; funds resolve per symbol."""
        seen: list[tuple] = []

        async def _gather(symbols, klass, start, end):
            seen.append((symbols, klass))

            return [SESSION]

        monkeypatch.setattr(
            "openbb_nasdaq.utils.helpers.gather_historical_prices", _gather
        )
        query = fetcher.transform_query({"symbol": "X"})
        raw = asyncio.run(fetcher.aextract_data(query, None))
        rows = fetcher.transform_data(query, raw)

        assert seen[0][1] == asset_class
        assert rows[0].close == 1.0


class TestIndexHistorical:
    """Cover the index history model and its intraday interval."""

    def test_daily_delegates(self, monkeypatch):
        """The daily interval uses the shared price helper."""
        seen: list[tuple] = []

        async def _gather(symbols, klass, start, end):
            seen.append((symbols, klass))

            return [SESSION]

        monkeypatch.setattr(
            "openbb_nasdaq.utils.helpers.gather_historical_prices", _gather
        )
        query = NasdaqIndexHistoricalFetcher.transform_query({"symbol": "COMP"})
        raw = asyncio.run(NasdaqIndexHistoricalFetcher.aextract_data(query, None))
        rows = NasdaqIndexHistoricalFetcher.transform_data(query, raw)

        assert seen[0][1] == "index"
        assert rows[0].close == 1.0

    def test_intraday_reads_the_chart(self, monkeypatch):
        """The one-minute interval reads the chart series."""
        seen: list[str] = []
        patch_data(
            monkeypatch,
            [
                {
                    "symbol": "COMP",
                    "indexCharts": [
                        {
                            "z": {"dateTime": "7/24/2026 9:30:58 AM"},
                            "y": 25120.13,
                        },
                        {"z": {"dateTime": "bad"}, "y": 1},
                    ],
                }
            ],
            seen,
        )
        query = NasdaqIndexHistoricalFetcher.transform_query(
            {"symbol": "COMP", "interval": "1m"}
        )
        raw = asyncio.run(NasdaqIndexHistoricalFetcher.aextract_data(query, None))
        rows = NasdaqIndexHistoricalFetcher.transform_data(query, raw)

        assert "chartFor=COMP" in seen[0]
        assert len(rows) == 1
        assert rows[0].date.hour == 9
        assert rows[0].close == pytest.approx(25120.13)

    def test_intraday_without_a_series(self, monkeypatch):
        """An index with no session series is reported."""
        patch_data(monkeypatch, None)
        query = NasdaqIndexHistoricalFetcher.transform_query(
            {"symbol": "COMP", "interval": "1m"}
        )
        raw = asyncio.run(NasdaqIndexHistoricalFetcher.aextract_data(query, None))

        with pytest.raises(EmptyDataError, match="No intraday series"):
            NasdaqIndexHistoricalFetcher.transform_data(query, raw)


class TestEquityInfoExtract:
    """Cover the company profile request."""

    def test_fetches_both_blocks(self, monkeypatch):
        """The profile and quote header are both requested."""
        seen: list[str] = []
        patch_data(
            monkeypatch,
            lambda path: (
                {"companyName": "Apple Inc."}
                if "/info" in path
                else {"CompanyName": {"value": "Apple Inc."}}
            ),
            seen,
        )
        query = NasdaqEquityInfoFetcher.transform_query({"symbol": "aapl"})
        raw = asyncio.run(NasdaqEquityInfoFetcher.aextract_data(query, None))

        assert len(seen) == 2
        assert raw[0]["symbol"] == "AAPL"

    def test_warns_on_a_bad_symbol(self, monkeypatch):
        """A symbol with no profile warns and is skipped."""

        async def _data(path, **kwargs):
            raise OpenBBError("unknown symbol")

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        query = NasdaqEquityInfoFetcher.transform_query({"symbol": "NOPE"})

        with (
            pytest.warns(UserWarning, match="NOPE"),
            pytest.raises(EmptyDataError, match="No company profiles"),
        ):
            asyncio.run(NasdaqEquityInfoFetcher.aextract_data(query, None))


class TestShortInterestExtract:
    """Cover the short interest request."""

    def test_labels_each_row(self, monkeypatch):
        """Each settlement row is tagged with its symbol."""
        patch_data(
            monkeypatch,
            {
                "shortInterestTable": {
                    "rows": [{"settlementDate": "07/15/2026", "interest": "100"}]
                }
            },
        )
        query = NasdaqEquityShortInterestFetcher.transform_query({"symbol": "aapl"})
        raw = asyncio.run(NasdaqEquityShortInterestFetcher.aextract_data(query, None))

        assert raw[0]["symbol"] == "AAPL"

    def test_empty_raises(self, monkeypatch):
        """A symbol with no short interest is reported."""
        patch_data(monkeypatch, {})
        query = NasdaqEquityShortInterestFetcher.transform_query({"symbol": "AAPL"})

        with pytest.raises(EmptyDataError):
            asyncio.run(NasdaqEquityShortInterestFetcher.aextract_data(query, None))


class TestParserGuards:
    """Cover the guards for unparseable upstream values."""

    @pytest.mark.parametrize("value", [None, "", "   ", 42])
    def test_index_chart_time(self, value):
        """Anything that is not a chart timestamp yields None."""
        from openbb_nasdaq.models.index_historical import parse_chart_time

        assert parse_chart_time(value) is None

    def test_dividend_amount_placeholder(self):
        """A dividend amount of N/A yields None before validation."""
        from openbb_nasdaq.models.historical_dividends import (
            NasdaqHistoricalDividendsData,
        )

        assert NasdaqHistoricalDividendsData.validate_amount("N/A") is None
