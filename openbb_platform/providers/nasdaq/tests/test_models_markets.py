"""Tests for the fund, index, and market-wide Nasdaq models."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_nasdaq.models.etf_equity_exposure import NasdaqEtfEquityExposureFetcher
from openbb_nasdaq.models.etf_holdings import NasdaqEtfHoldingsFetcher
from openbb_nasdaq.models.etf_info import NasdaqEtfInfoFetcher
from openbb_nasdaq.models.index_snapshots import NasdaqIndexSnapshotsFetcher
from openbb_nasdaq.models.market_movers import NasdaqMarketMoversFetcher
from openbb_nasdaq.models.market_status import (
    NasdaqMarketStatusFetcher,
    parse_eastern,
)
from openbb_nasdaq.models.price_quote import NasdaqPriceQuoteFetcher

from .conftest import patch_asset_class, patch_data


class TestEtfHoldings:
    """Cover the fund holdings model."""

    def test_etf_path(self, monkeypatch):
        """An ETF is served from the company holdings endpoint."""
        seen: list[str] = []
        patch_asset_class(monkeypatch, "etf")
        patch_data(
            monkeypatch,
            {
                "holdings": {
                    "rows": [
                        {
                            "symbol": "NVDA",
                            "companyname": "NVIDIA Corporation",
                            "weighting": "7.96%",
                        }
                    ]
                }
            },
            seen,
        )
        query = NasdaqEtfHoldingsFetcher.transform_query({"symbol": "spy"})
        raw = asyncio.run(NasdaqEtfHoldingsFetcher.aextract_data(query, None))
        rows = NasdaqEtfHoldingsFetcher.transform_data(query, raw)

        assert seen == ["company/spy/holdings?assetclass=etf"]
        assert rows[0].symbol == "NVDA"
        assert rows[0].weight == pytest.approx(0.0796)

    def test_mutual_fund_path(self, monkeypatch):
        """A mutual fund is served from the fund profile."""
        seen: list[str] = []
        patch_asset_class(monkeypatch, "mutualfunds")
        patch_data(
            monkeypatch,
            {
                "TopTenHoldings": {
                    "topTenHoldingsTable": {
                        "rows": [
                            {
                                "symbol": "GOOGL",
                                "name": "Alphabet Inc. Class A",
                                "assets": "2.935%",
                            }
                        ]
                    }
                }
            },
            seen,
        )
        query = NasdaqEtfHoldingsFetcher.transform_query({"symbol": "PRGFX"})
        raw = asyncio.run(NasdaqEtfHoldingsFetcher.aextract_data(query, None))
        rows = NasdaqEtfHoldingsFetcher.transform_data(query, raw)

        assert seen == ["funds/section/PRGFX"]
        assert rows[0].name == "Alphabet Inc. Class A"
        assert rows[0].weight == pytest.approx(0.02935)

    def test_missing_payload(self, monkeypatch):
        """An absent holdings block yields no rows."""
        patch_asset_class(monkeypatch, "etf")
        patch_data(monkeypatch, None)
        query = NasdaqEtfHoldingsFetcher.transform_query({"symbol": "SPY"})

        assert asyncio.run(NasdaqEtfHoldingsFetcher.aextract_data(query, None)) == []

    def test_empty_raises(self):
        """A fund with no published holdings is reported."""
        query = NasdaqEtfHoldingsFetcher.transform_query({"symbol": "SPY"})

        with pytest.raises(EmptyDataError, match="No holdings"):
            NasdaqEtfHoldingsFetcher.transform_data(query, [])


class TestEtfEquityExposure:
    """Cover the reverse fund-exposure model."""

    def test_parses_the_price_change(self, monkeypatch):
        """The combined change string is split into value and percent."""
        patch_asset_class(monkeypatch, "stocks")
        patch_data(
            monkeypatch,
            {
                "holdings": {
                    "rows": [
                        {
                            "symbol": "GXPT",
                            "companyname": "Global X PureCap",
                            "weighting": "20.07%",
                            "priceChange100Day": "+6.21 (+24.12%)",
                        }
                    ]
                }
            },
        )
        query = NasdaqEtfEquityExposureFetcher.transform_query({"symbol": "aapl"})
        raw = asyncio.run(NasdaqEtfEquityExposureFetcher.aextract_data(query, None))
        rows = NasdaqEtfEquityExposureFetcher.transform_data(query, raw)

        assert rows[0].equity_symbol == "AAPL"
        assert rows[0].etf_symbol == "GXPT"
        assert rows[0].price_change_100_day == pytest.approx(6.21)
        assert rows[0].price_change_100_day_percent == pytest.approx(0.2412)

    def test_without_a_price_change(self, monkeypatch):
        """A fund with no trailing change still resolves."""
        query = NasdaqEtfEquityExposureFetcher.transform_query({"symbol": "AAPL"})
        rows = NasdaqEtfEquityExposureFetcher.transform_data(
            query, [{"symbol": "X", "weighting": "1%", "priceChange100Day": None}]
        )

        assert rows[0].price_change_100_day is None

    def test_empty_raises(self):
        """An equity in no fund's top ten is reported."""
        query = NasdaqEtfEquityExposureFetcher.transform_query({"symbol": "AAPL"})

        with pytest.raises(EmptyDataError, match="top-ten"):
            NasdaqEtfEquityExposureFetcher.transform_data(query, [])


class TestEtfInfo:
    """Cover the fund key-data model."""

    def test_etf_summary(self, monkeypatch):
        """An ETF is read from the quote summary block."""
        patch_asset_class(monkeypatch, "etf")
        patch_data(
            monkeypatch,
            lambda path: (
                {"companyName": "Invesco QQQ"}
                if "info" in path
                else {
                    "summaryData": {
                        "AUM": {"value": "$1,000"},
                        "ExpenseRatio": {"value": "0.20%"},
                        "FiftTwoWeekHighLow": {"value": "$400/$700"},
                    }
                }
            ),
        )
        query = NasdaqEtfInfoFetcher.transform_query({"symbol": "QQQ"})
        raw = asyncio.run(NasdaqEtfInfoFetcher.aextract_data(query, None))
        rows = NasdaqEtfInfoFetcher.transform_data(query, raw)

        assert rows[0].name == "Invesco QQQ"
        assert rows[0].expense_ratio == pytest.approx(0.002)
        assert rows[0].year_high == 700
        assert rows[0].year_low == 400

    def test_mutual_fund_profile(self, monkeypatch):
        """A mutual fund is read from the fund profile sections."""
        patch_asset_class(monkeypatch, "mutualfunds")
        patch_data(
            monkeypatch,
            lambda path: (
                {"companyName": "Vanguard 500"}
                if "quote/" in path
                else {
                    "AboutTheFund": {
                        "inceptionDate": {"value": "Nov 13, 2000"},
                        "fundInvestmentCategory": {"value": "Not Assigned"},
                        "investmentFocus": {"value": "Large Cap"},
                    },
                    "FeesAndExpenses": {"totalExpenseRatio": {"value": "0.04%"}},
                    "PerformanceSummary": {"PreviousClose": {"value": "$683.89"}},
                }
            ),
        )
        query = NasdaqEtfInfoFetcher.transform_query({"symbol": "VFIAX"})
        raw = asyncio.run(NasdaqEtfInfoFetcher.aextract_data(query, None))
        rows = NasdaqEtfInfoFetcher.transform_data(query, raw)

        assert rows[0].inception_date.isoformat() == "2000-11-13"
        assert rows[0].investment_category is None
        assert rows[0].investment_focus == "Large Cap"
        assert rows[0].previous_close == pytest.approx(683.89)

    def test_warns_and_skips_a_failure(self, monkeypatch):
        """A symbol the endpoints reject warns rather than sinking the request."""
        patch_asset_class(monkeypatch, "etf")

        async def _data(path, **kwargs):
            raise OpenBBError("no such fund")

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        query = NasdaqEtfInfoFetcher.transform_query({"symbol": "NOPE"})

        with pytest.warns(UserWarning, match="NOPE"), pytest.raises(EmptyDataError):
            asyncio.run(NasdaqEtfInfoFetcher.aextract_data(query, None))


class TestMarketStatus:
    """Cover the market status model."""

    def test_parses_the_session(self, monkeypatch):
        """The status and session times are read."""
        patch_data(
            monkeypatch,
            {
                "country": "U.S.",
                "mrktStatus": "Closed",
                "marketIndicator": "Market Closed",
                "mrktCountDown": "Opens in 1D",
                "isBusinessDay": False,
                "previousTradeDate": "Jul 23, 2026",
                "nextTradeDate": "Jul 27, 2026",
                "marketOpeningTime": "Jul 27, 2026 09:30 AM ET",
                "marketClosingTime": "Jul 27, 2026 04:00 PM ET",
            },
        )
        query = NasdaqMarketStatusFetcher.transform_query({})
        raw = asyncio.run(NasdaqMarketStatusFetcher.aextract_data(query, None))
        rows = NasdaqMarketStatusFetcher.transform_data(query, raw)

        assert rows[0].status == "Closed"
        assert rows[0].is_business_day is False
        assert rows[0].market_open.hour == 9
        assert rows[0].market_close.hour == 16
        assert rows[0].pre_market_open is None

    def test_empty_raises(self):
        """No published status is reported."""
        query = NasdaqMarketStatusFetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="No market status"):
            NasdaqMarketStatusFetcher.transform_data(query, {})

    def test_missing_payload(self, monkeypatch):
        """An empty response degrades to an empty dict."""
        patch_data(monkeypatch, None)
        query = NasdaqMarketStatusFetcher.transform_query({})

        assert asyncio.run(NasdaqMarketStatusFetcher.aextract_data(query, None)) == {}

    @pytest.mark.parametrize(
        "value", [None, "", "   ", "not a timestamp", 42, "Jul 27, 2026"]
    )
    def test_unparseable_timestamps(self, value):
        """Anything that is not a session timestamp yields None."""
        assert parse_eastern(value) is None

    def test_parses_a_timestamp(self):
        """The ET suffix is stripped before parsing."""
        assert parse_eastern("Jul 27, 2026 04:00 PM ET").hour == 16


class TestMarketMovers:
    """Cover the market movers model."""

    @staticmethod
    def _payload(rows):
        """Wrap rows in the movers envelope."""
        return {"STOCKS": {"MostActiveByShareVolume": {"table": {"rows": rows}}}}

    def test_builds_the_request(self, monkeypatch):
        """The asset class, session, and limit are all sent."""
        seen: list[str] = []
        patch_data(monkeypatch, self._payload([{"symbol": "OMH"}]), seen)
        query = NasdaqMarketMoversFetcher.transform_query(
            {"limit": 20, "session": "pre_market"}
        )
        asyncio.run(NasdaqMarketMoversFetcher.aextract_data(query, None))

        assert seen == [
            "marketmovers?assetclass=STOCKS&exchangestatus=premarket&limit=20"
        ]

    def test_volume_list_carries_volume(self):
        """A most-active list reports volume and the published percent."""
        query = NasdaqMarketMoversFetcher.transform_query({})
        rows = NasdaqMarketMoversFetcher.transform_data(
            query,
            [
                {
                    "symbol": "OMH",
                    "name": "Ohmyhome",
                    "lastSalePrice": "$0.50",
                    "lastSaleChange": "+0.08",
                    "percentageChange": "+19.0%",
                    "change": "242,916,231",
                }
            ],
        )

        assert rows[0].volume == pytest.approx(242916231)
        assert rows[0].change_percent == pytest.approx(0.19)

    def test_advancer_percent_is_derived(self):
        """An advancers list without a percent derives one from the change."""
        query = NasdaqMarketMoversFetcher.transform_query({"category": "most_advanced"})
        rows = NasdaqMarketMoversFetcher.transform_data(
            query,
            [
                {
                    "symbol": "STAK",
                    "lastSalePrice": "$9.27",
                    "lastSaleChange": "+7.95",
                    "change": "",
                }
            ],
        )

        assert rows[0].volume is None
        assert rows[0].change_percent == pytest.approx(7.95 / 1.32, rel=1e-3)

    def test_zero_previous_close(self):
        """A previous close of zero yields no percent rather than dividing."""
        query = NasdaqMarketMoversFetcher.transform_query({"category": "most_advanced"})
        rows = NasdaqMarketMoversFetcher.transform_data(
            query,
            [{"symbol": "X", "lastSalePrice": "$1.00", "lastSaleChange": "1.00"}],
        )

        assert rows[0].change_percent is None

    def test_unknown_asset_class(self, monkeypatch):
        """An asset class Nasdaq does not rank is refused."""
        patch_data(monkeypatch, {})
        query = NasdaqMarketMoversFetcher.transform_query({"asset_class": "bonds"})

        with pytest.raises(OpenBBError, match="not a Nasdaq market-movers"):
            asyncio.run(NasdaqMarketMoversFetcher.aextract_data(query, None))

    def test_unpublished_list(self, monkeypatch):
        """A list the asset class does not publish is reported."""
        patch_data(monkeypatch, {"MUTUALFUNDS": {}})
        query = NasdaqMarketMoversFetcher.transform_query(
            {"asset_class": "mutualfunds", "category": "nasdaq_100"}
        )

        with pytest.raises(OpenBBError, match="does not publish"):
            asyncio.run(NasdaqMarketMoversFetcher.aextract_data(query, None))


class TestPriceQuote:
    """Cover the batch quote model."""

    def test_transforms_a_record(self, monkeypatch):
        """A batch record becomes a typed quote."""

        async def _quotes(symbols):
            return [
                {
                    "key": "OMXS30|INDEX",
                    "ticker": ["OMXS30", "Omx Stockholm 30 Index"],
                    "lastSale": "3,199.62",
                    "change": "+32.52",
                    "pctChange": "+1.03%",
                    "volume": "",
                    "assetclass": "INDEX",
                    "url": "/market-activity/index/omxs30",
                }
            ]

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_basic_quotes", _quotes)
        query = NasdaqPriceQuoteFetcher.transform_query({"symbol": "OMXS30"})
        raw = asyncio.run(NasdaqPriceQuoteFetcher.aextract_data(query, None))
        rows = NasdaqPriceQuoteFetcher.transform_data(query, raw)

        assert rows[0].symbol == "OMXS30"
        assert rows[0].name == "Omx Stockholm 30 Index"
        assert rows[0].last_price == pytest.approx(3199.62)
        assert rows[0].change_percent == pytest.approx(0.0103)
        assert rows[0].url == "https://www.nasdaq.com/market-activity/index/omxs30"

    def test_record_without_a_name_or_url(self):
        """A sparse record still resolves."""
        query = NasdaqPriceQuoteFetcher.transform_query({"symbol": "X"})
        rows = NasdaqPriceQuoteFetcher.transform_data(
            query, [{"key": "X|STOCKS", "ticker": ["X"]}]
        )

        assert rows[0].name is None
        assert rows[0].url is None


class TestIndexSnapshots:
    """Cover the index universe model."""

    def test_us_universe(self, monkeypatch):
        """A US region is read from the index screener."""
        seen: list[str] = []
        patch_data(
            monkeypatch,
            {
                "records": {
                    "data": {
                        "rows": [
                            {
                                "symbol": "COMP",
                                "companyName": "NASDAQ Composite",
                                "lastSalePrice": "24,975.82",
                                "netChange": "-161.87",
                                "percentageChange": "-0.64%",
                            },
                            {"symbol": None},
                        ]
                    }
                }
            },
            seen,
        )
        query = NasdaqIndexSnapshotsFetcher.transform_query({"region": "us"})
        raw = asyncio.run(NasdaqIndexSnapshotsFetcher.aextract_data(query, None))
        rows = NasdaqIndexSnapshotsFetcher.transform_data(query, raw)

        assert "indextype=US" in seen[0]
        assert len(rows) == 1
        assert rows[0].change_percent == pytest.approx(-0.0064)

    def test_nordic_universe(self, monkeypatch):
        """The Nordic region is read from the Nasdaq Nordic listing."""
        seen: list[str] = []
        patch_data(
            monkeypatch,
            {
                "instrumentListing": {
                    "rows": [
                        {
                            "symbol": "OMXS30",
                            "fullName": "OMX Stockholm 30",
                            "lastSalePrice": "3,199.62",
                            "percentageChange": "+1.03%",
                            "currency": "SEK",
                        }
                    ]
                }
            },
            seen,
        )
        query = NasdaqIndexSnapshotsFetcher.transform_query({"region": "nordic"})
        raw = asyncio.run(NasdaqIndexSnapshotsFetcher.aextract_data(query, None))
        rows = NasdaqIndexSnapshotsFetcher.transform_data(query, raw)

        assert seen[0].startswith("nordic/screener/indexes")
        assert rows[0].name == "OMX Stockholm 30"
        assert rows[0].currency == "SEK"

    def test_unknown_region(self, monkeypatch):
        """A region Nasdaq does not publish is refused."""
        patch_data(monkeypatch, {})
        query = NasdaqIndexSnapshotsFetcher.transform_query({"region": "mars"})

        with pytest.raises(OpenBBError, match="not a Nasdaq index region"):
            asyncio.run(NasdaqIndexSnapshotsFetcher.aextract_data(query, None))

    def test_empty_raises(self):
        """A region with no indexes is reported."""
        query = NasdaqIndexSnapshotsFetcher.transform_query({"region": "us"})

        with pytest.raises(EmptyDataError, match="No indexes"):
            NasdaqIndexSnapshotsFetcher.transform_data(query, [])

    def test_missing_payload(self, monkeypatch):
        """An empty screener response yields no rows."""
        patch_data(monkeypatch, None)
        query = NasdaqIndexSnapshotsFetcher.transform_query({"region": "all"})

        assert asyncio.run(NasdaqIndexSnapshotsFetcher.aextract_data(query, None)) == []
