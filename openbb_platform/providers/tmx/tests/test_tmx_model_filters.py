"""Tests for the filters and transforms the TMX models apply to raw data."""

from datetime import date, datetime

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pandas import DataFrame

BONDS = DataFrame(
    [
        {
            "isin": "CA00206RGQ44",
            "bondType": "Corp",
            "issuer": "  Air Canada  ",
            "maturityDate": "2030-06-01",
            "lastTradedDate": "2026-07-24",
            "couponRate": 4.5,
            "securityId": 1,
            "secKey": "a",
        },
        {
            "isin": "CA135087U28",
            "bondType": "Govt",
            "issuer": " Government of Canada ",
            "maturityDate": "2035-06-01",
            "lastTradedDate": "2026-07-23",
            "couponRate": 3.25,
            "securityId": 2,
            "secKey": "b",
        },
        {
            "isin": "CA00206RGQ99",
            "bondType": "Corp",
            "issuer": " Bell ",
            "maturityDate": "2045-06-01",
            "lastTradedDate": "2020-01-02",
            "couponRate": 6.0,
            "securityId": 3,
            "secKey": "c",
        },
    ]
)


class TestBondPriceFilters:
    """The corporate bond screen filters on the loaded frame."""

    def _query(self, **kwargs):
        from openbb_tmx.models.bond_prices import TmxBondPricesFetcher

        return TmxBondPricesFetcher.transform_query(kwargs)

    @pytest.mark.parametrize(
        ("today", "expected"),
        [
            (datetime(2026, 7, 24, 12), "2026-07-23"),
            (datetime(2026, 7, 25, 12), "2026-07-23"),
            (datetime(2026, 7, 26, 12), "2026-07-23"),
        ],
    )
    def test_the_default_window_rolls_off_a_weekend(self, monkeypatch, today, expected):
        """The bond feed publishes on business days only."""
        from openbb_tmx.models import bond_prices

        class Clock(datetime):
            @classmethod
            def now(cls, tz=None):
                return today

        monkeypatch.setattr(bond_prices, "datetime", Clock)

        assert str(self._query().maturity_date_min) == expected

    def test_an_isin_selects_the_matching_bonds(self):
        from openbb_tmx.models.bond_prices import TmxBondPricesFetcher

        rows = TmxBondPricesFetcher.transform_data(
            self._query(isin="CA00206RGQ44"), BONDS.copy()
        )

        assert [r.isin for r in rows] == ["CA00206RGQ44"]

    def test_several_isins_are_accepted(self):
        from openbb_tmx.models.bond_prices import TmxBondPricesFetcher

        rows = TmxBondPricesFetcher.transform_data(
            self._query(isin="CA00206RGQ44,CA00206RGQ99"), BONDS.copy()
        )

        assert sorted(r.isin for r in rows) == ["CA00206RGQ44", "CA00206RGQ99"]

    def test_an_unmatched_isin_is_reported(self):
        from openbb_tmx.models.bond_prices import TmxBondPricesFetcher

        with pytest.raises(OpenBBError, match="No bonds found"):
            TmxBondPricesFetcher.transform_data(
                self._query(isin="CA0000000000"), BONDS.copy()
            )

    def test_the_maturity_ceiling_is_applied(self):
        from openbb_tmx.models.bond_prices import TmxBondPricesFetcher

        rows = TmxBondPricesFetcher.transform_data(
            self._query(
                maturity_date_min=date(2020, 1, 1), maturity_date_max=date(2035, 1, 1)
            ),
            BONDS.copy(),
        )

        assert [r.isin for r in rows] == ["CA00206RGQ44"]

    def test_the_last_traded_floor_is_applied(self):
        from openbb_tmx.models.bond_prices import TmxBondPricesFetcher

        rows = TmxBondPricesFetcher.transform_data(
            self._query(
                maturity_date_min=date(2020, 1, 1), last_traded_min=date(2026, 1, 1)
            ),
            BONDS.copy(),
        )

        assert [r.isin for r in rows] == ["CA00206RGQ44"]


class TestTreasuryPriceFilters:
    """The government bond screen filters on the loaded frame."""

    def _query(self, **kwargs):
        from openbb_tmx.models.treasury_prices import TmxTreasuryPricesFetcher

        return TmxTreasuryPricesFetcher.transform_query(kwargs)

    def test_rows_are_returned_without_the_internal_columns(self):
        from openbb_tmx.models.treasury_prices import TmxTreasuryPricesFetcher

        rows = TmxTreasuryPricesFetcher.transform_data(
            self._query(maturity_date_min=date(2020, 1, 1)), BONDS.copy()
        )

        assert [r.issuer_name for r in rows] == ["Government of Canada"]
        assert not hasattr(rows[0], "secKey")

    def test_the_maturity_ceiling_is_applied(self):
        from openbb_tmx.models.treasury_prices import TmxTreasuryPricesFetcher

        rows = TmxTreasuryPricesFetcher.transform_data(
            self._query(
                maturity_date_min=date(2020, 1, 1), maturity_date_max=date(2030, 1, 1)
            ),
            BONDS.copy(),
        )

        assert rows == []

    def test_the_last_traded_floor_is_applied(self):
        from openbb_tmx.models.treasury_prices import TmxTreasuryPricesFetcher

        rows = TmxTreasuryPricesFetcher.transform_data(
            self._query(
                maturity_date_min=date(2020, 1, 1), last_traded_min=date(2026, 7, 24)
            ),
            BONDS.copy(),
        )

        assert rows == []


DIRECTORY = DataFrame(
    [
        {
            "symbol": "AC",
            "name": "Air Canada",
            "marketCap": 8_000_000_000,
            "optionable": True,
            "exchange": "TSX",
            "symbolType": "equity",
            "country": "CA",
        },
        {
            "symbol": "ZZZ",
            "name": "Sleep Country",
            "marketCap": 500_000_000,
            "optionable": False,
            "exchange": "TSX",
            "symbolType": "equity",
            "country": "CA",
        },
    ]
)


class TestScreenerFilters:
    """The equity screen runs against the directory frame."""

    @pytest.fixture
    def directory(self, monkeypatch):
        """Serve a two-row directory."""

        async def frame(**kwargs):
            return DIRECTORY.copy()

        monkeypatch.setattr(
            "openbb_tmx.utils.directory.get_directory_frame", frame, raising=False
        )
        monkeypatch.setattr(
            "openbb_tmx.models.equity_screener.TmxEquityScreenerFetcher._fundamentals",
            None,
            raising=False,
        )

    def _query(self, **kwargs):
        from openbb_tmx.models.equity_screener import TmxEquityScreenerQueryParams

        return TmxEquityScreenerQueryParams(**kwargs)

    async def test_the_market_cap_floor_is_applied(self, directory):
        from openbb_tmx.models.equity_screener import TmxEquityScreenerFetcher

        rows = await TmxEquityScreenerFetcher.aextract_data(
            self._query(market_cap_min=1_000_000_000, fundamentals=False), {}
        )

        assert [r["symbol"] for r in rows] == ["AC"]

    async def test_the_market_cap_ceiling_is_applied(self, directory):
        from openbb_tmx.models.equity_screener import TmxEquityScreenerFetcher

        rows = await TmxEquityScreenerFetcher.aextract_data(
            self._query(market_cap_max=1_000_000_000, fundamentals=False), {}
        )

        assert [r["symbol"] for r in rows] == ["ZZZ"]

    async def test_the_optionable_flag_is_applied(self, directory):
        from openbb_tmx.models.equity_screener import TmxEquityScreenerFetcher

        rows = await TmxEquityScreenerFetcher.aextract_data(
            self._query(optionable=True, fundamentals=False), {}
        )

        assert [r["symbol"] for r in rows] == ["AC"]

    async def test_an_empty_screen_is_reported(self, directory):
        from openbb_tmx.models.equity_screener import TmxEquityScreenerFetcher

        with pytest.raises(EmptyDataError, match="No instruments matched"):
            await TmxEquityScreenerFetcher.aextract_data(
                self._query(market_cap_min=10**15, fundamentals=False), {}
            )


ETFS = [
    {
        "symbol": "XIU",
        "name": "iShares S&P/TSX 60 Index ETF",
        "short_name": "XIU",
        "investment_style": "Index",
        "investment_objectives": "Track the index",
        "dividend_frequency": "Quarterly",
        "regions": [{"name": "Canada", "percent": 98.0}],
        "sectors": [{"name": "Financials", "percent": 35.0}],
        "holdings_top10_summary": None,
        "holdings_top10": None,
        "additional_data": None,
        "website": None,
        "asset_class_id": None,
    },
    {
        "symbol": "ZEB",
        "name": "BMO Equal Weight Banks",
        "short_name": "ZEB",
        "investment_style": "Sector",
        "investment_objectives": "Bank exposure",
        "dividend_frequency": "Monthly",
        "regions": [],
        "sectors": [],
        "holdings_top10_summary": None,
        "holdings_top10": None,
        "additional_data": None,
        "website": None,
        "asset_class_id": None,
    },
]


@pytest.fixture
def etfs(monkeypatch):
    """Serve a two-entry ETF universe."""

    async def all_etfs(use_cache=True):
        return [dict(e) for e in ETFS]

    monkeypatch.setattr("openbb_tmx.utils.helpers.get_all_etfs", all_etfs)


class TestEtfSearchFilters:
    """The ETF search filters the loaded universe."""

    def _query(self, **kwargs):
        from openbb_tmx.models.etf_search import TmxEtfSearchQueryParams

        return TmxEtfSearchQueryParams(**kwargs)

    async def test_a_query_narrows_the_universe(self, etfs):
        from openbb_tmx.models.etf_search import TmxEtfSearchFetcher

        rows = await TmxEtfSearchFetcher.aextract_data(self._query(query="banks"), {})

        assert [r["symbol"] for r in rows] == ["ZEB"]

    async def test_the_dividend_frequency_narrows_the_universe(self, etfs):
        from openbb_tmx.models.etf_search import TmxEtfSearchFetcher

        rows = await TmxEtfSearchFetcher.aextract_data(
            self._query(div_freq="monthly"), {}
        )

        assert [r["symbol"] for r in rows] == ["ZEB"]


class TestEtfHoldingsBreakdowns:
    """The country and sector breakdowns skip ETFs that publish none."""

    async def test_a_suffixed_symbol_is_stripped(self, etfs):
        from openbb_tmx.models.etf_countries import (
            TmxEtfCountriesFetcher,
            TmxEtfCountriesQueryParams as Query,
        )

        rows = await TmxEtfCountriesFetcher.aextract_data(Query(symbol="XIU.TO"), {})

        assert rows[0]["symbol"] == "XIU"

    async def test_an_etf_with_an_empty_breakdown_warns(self, etfs):
        from openbb_tmx.models.etf_countries import (
            TmxEtfCountriesFetcher,
            TmxEtfCountriesQueryParams as Query,
        )

        with pytest.warns(UserWarning, match="No data found for NOPE"):
            rows = await TmxEtfCountriesFetcher.aextract_data(
                Query(symbol="XIU,NOPE"), {}
            )

        assert [r["symbol"] for r in rows] == ["XIU"]

    async def test_no_countries_at_all_is_reported(self, etfs):
        from openbb_tmx.models.etf_countries import (
            TmxEtfCountriesFetcher,
            TmxEtfCountriesQueryParams as Query,
        )

        with (
            pytest.warns(UserWarning),
            pytest.raises(EmptyDataError, match="No countries"),
        ):
            await TmxEtfCountriesFetcher.aextract_data(Query(symbol="NOPE"), {})

    async def test_an_etf_without_sectors_warns(self, etfs):
        from openbb_tmx.models.etf_sectors import (
            TmxEtfSectorsFetcher,
            TmxEtfSectorsQueryParams as Query,
        )

        with pytest.warns(UserWarning, match="No sectors info found"):
            rows = await TmxEtfSectorsFetcher.aextract_data(Query(symbol="XIU,ZEB"), {})

        assert [r["symbol"] for r in rows] == ["XIU"]

    async def test_no_sectors_at_all_is_reported(self, etfs):
        from openbb_tmx.models.etf_sectors import (
            TmxEtfSectorsFetcher,
            TmxEtfSectorsQueryParams as Query,
        )

        with (
            pytest.warns(UserWarning),
            pytest.raises(EmptyDataError, match="No data found"),
        ):
            await TmxEtfSectorsFetcher.aextract_data(Query(symbol="ZEB"), {})


class TestIndexConstituents:
    """An unknown index and an empty index are reported separately."""

    def _query(self, symbol):
        from openbb_tmx.models.index_constituents import (
            TmxIndexConstituentsQueryParams,
        )

        return TmxIndexConstituentsQueryParams(symbol=symbol)

    async def test_an_unknown_index_is_reported(self, monkeypatch):
        from openbb_tmx.models.index_constituents import TmxIndexConstituentsFetcher

        async def unknown(*args, **kwargs):
            return {"constituents": None}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", unknown)

        with pytest.raises(OpenBBError, match="was not found"):
            await TmxIndexConstituentsFetcher.aextract_data(self._query("^NOPE"), {})

    def test_an_index_without_constituents_is_reported(self):
        from openbb_tmx.models.index_constituents import TmxIndexConstituentsFetcher

        with pytest.raises(EmptyDataError, match="No constituents found"):
            TmxIndexConstituentsFetcher.transform_data(self._query("^TX60"), [])

    def test_only_the_published_fields_survive(self):
        from openbb_tmx.models.index_constituents import TmxIndexConstituentsFetcher

        rows = TmxIndexConstituentsFetcher.transform_data(
            self._query("^TX60"),
            [{"symbol": "RY", "longName": "Royal Bank", "shortName": "RBC"}],
        )

        assert "shortName" not in rows[0].model_dump()


class TestInsiderTradingSummary:
    """The summary view is returned when it is asked for."""

    def _query(self, summary):
        from openbb_tmx.models.insider_trading import TmxInsiderTradingQueryParams

        return TmxInsiderTradingQueryParams(symbol="AC", summary=summary)

    def test_the_summary_is_returned(self):
        from openbb_tmx.models.insider_trading import TmxInsiderTradingFetcher

        data = {
            "insiderActivities": [],
            "activitySummary": [
                {
                    "periodkey": "3 months",
                    "buyShares": 100,
                    "soldShares": 40,
                    "netActivity": 60,
                    "totalShares": 140,
                }
            ],
        }
        rows = TmxInsiderTradingFetcher.transform_data(self._query(True), data)

        assert [r.period for r in rows] == ["3_months"]
        assert rows[0].securities_bought == 100
