"""Tests for the TMX helper functions."""

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_tmx.utils import helpers

ETF_JSON = [
    {
        "symbol": "XIU",
        "shortname": "iShares",
        "longname": "iShares S&P/TSX 60",
        "fundfamily": "BlackRock",
        "regions": [],
        "sectors": [],
        "currency": "CAD",
        "inceptiondate": "1999-09-28",
        "unitprice": 52.74,
        "prevClose": 52.5,
        "close": 52.74,
        "esg": False,
        "investmentstyle": "Index",
        "avgdailyvolume": 100000,
        "totalreturn1month": 1.0,
        "totalreturn3month": 2.0,
        "totalreturn1year": 10.0,
        "totalreturn3year": 8.0,
        "totalreturn5year": 7.0,
        "totalreturnytd": 5.0,
        "totalreturnsinceinception": 200.0,
        "distributionyeld": 2.6,
        "dividendfrequency": "Quarterly",
        "pricetoearnings": 18.0,
        "pricetobook": 2.0,
        "assetclass": "1",
        "prospectobjective": "Track",
        "avgvol30days": 90000,
        "aum": 1.5e10,
        "top10holdings": [],
        "top10holdingsummary": "",
        "totalreturn6month": 3.0,
        "totalreturn10year": 6.0,
        "managementfee": 0.15,
        "altData": {
            "fundfamilyen": "BlackRock",
            "assetclassen": "Equity",
            "regionen": "Canada",
            "mer": 0.18,
            "websitefactsheeten": "https://example.com",
        },
        **{f"beta{n}y": 1.0 for n in range(1, 21)},
    }
]


class TestSymbolAndDates:
    """Small helpers."""

    def test_check_weekday_passes_a_weekday(self):
        assert helpers.check_weekday("2026-07-24") == "2026-07-24"

    def test_check_weekday_rolls_a_weekend(self):
        assert helpers.check_weekday("2026-07-25") != "2026-07-25"

    def test_is_markup(self):
        assert helpers._is_markup("https://www.m-x.ca/en/trading/data/quotes")
        assert not helpers._is_markup("https://example.com/a.json")

    def test_replace_values_in_list_of_dicts(self):
        rows = [{"a": "NA", "b": "-", "c": 1, "d": {"e": "NA"}, "f": ["NA", 2]}]
        cleaned = helpers.replace_values_in_list_of_dicts(rows)
        assert cleaned[0]["a"] is None
        assert cleaned[0]["b"] is None
        assert cleaned[0]["d"]["e"] is None
        assert cleaned[0]["f"][0] is None


class TestEtfUniverse:
    """The ETF reference file."""

    async def test_get_all_etfs(self, monkeypatch):
        async def fake(url, use_cache=True, **kwargs):
            return ETF_JSON

        monkeypatch.setattr(helpers, "get_data_from_url", fake)
        rows = await helpers.get_all_etfs()
        assert rows[0]["symbol"] == "XIU"
        assert rows[0]["asset_class"] == "Equity"
        assert rows[0]["region"] == "Canada"

    async def test_get_all_etfs_empty(self, monkeypatch):
        async def fake(url, use_cache=True, **kwargs):
            return None

        monkeypatch.setattr(helpers, "get_data_from_url", fake)

        with pytest.raises(OpenBBError, match="Could not get ETFs"):
            await helpers.get_all_etfs()


class TestCompanyDirectory:
    """The TSX company directory."""

    async def test_tickers(self, monkeypatch):
        async def fake(url, use_cache=True, **kwargs):
            return {"results": [{"symbol": "AC", "name": "Air Canada"}]}

        monkeypatch.setattr(helpers, "get_data_from_url", fake)
        assert await helpers.get_tmx_tickers() == {"AC": "Air Canada"}

    async def test_all_companies_merges_both_boards(self, monkeypatch):
        async def fake(exchange="tsx", use_cache=True):
            return {"AC": "Air Canada"} if exchange == "tsx" else {"XYZ": "Venture Co"}

        monkeypatch.setattr(helpers, "get_tmx_tickers", fake)
        merged = await helpers.get_all_tmx_companies()
        assert set(merged) == {"AC", "XYZ"}


class TestGraphQlHelpers:
    """The helpers that wrap GraphQL operations."""

    async def test_company_filings(self, gql):
        rows = await helpers.get_company_filings("AC")
        assert rows[0]["name"] == "AIF"

    async def test_daily_price_history(self, gql):
        rows = await helpers.get_daily_price_history(
            "AC", "2026-07-01", date(2026, 7, 24)
        )
        assert rows

    async def test_daily_price_history_unadjusted(self, gql):
        rows = await helpers.get_daily_price_history(
            "AC", date(2026, 7, 1), date(2026, 7, 24), adjustment="unadjusted"
        )
        assert isinstance(rows, list)

    async def test_weekly_or_monthly(self, gql):
        rows = await helpers.get_weekly_or_monthly_price_history(
            "AC", "2026-01-01", "2026-07-24", "month"
        )
        assert rows

    async def test_timeseries_history_defaults(self, gql):
        assert await helpers.get_timeseries_history("AC")

    async def test_intraday_history(self, gql):
        rows = await helpers.get_intraday_price_history(
            "AC", date(2026, 7, 1), date(2026, 7, 24), 5
        )
        assert isinstance(rows, list)

    async def test_intraday_clamps_the_start(self, gql):
        rows = await helpers.get_intraday_price_history(
            "AC", date(2000, 1, 1), date(2026, 7, 24), 60
        )
        assert isinstance(rows, list)


class TestBondMaster:
    """The CIRO bond master."""

    def test_normalize_types_and_sorts(self):
        frame = helpers._normalize_bonds(
            [
                {
                    "secKey": "2",
                    "issuer": "-",
                    "cusip": "B",
                    "isin": "I2",
                    "figi": None,
                    "maturityDate": "2030-01-01",
                    "couponRate": "2.0",
                    "lastPrice": "99",
                    "lastYield": "2.1",
                    "totalTrades": "1",
                    "lastTradedDate": "2026-07-01",
                    "highestPrice": "100",
                    "lowestPrice": "98",
                    "bondType": "Corp",
                    "originalIssueDate": "2020-01-01",
                },
                {
                    "secKey": "1",
                    "issuer": "GOC",
                    "cusip": "A",
                    "isin": "I1",
                    "figi": None,
                    "maturityDate": "2036-06-01",
                    "couponRate": "3.25",
                    "lastPrice": "96",
                    "lastYield": "3.6",
                    "totalTrades": "441",
                    "lastTradedDate": "2026-07-23",
                    "highestPrice": "97",
                    "lowestPrice": "96",
                    "bondType": "Government",
                    "originalIssueDate": "2020-06-01",
                },
            ]
        )
        assert frame.iloc[0]["cusip"] == "A"
        assert frame.iloc[0]["totalTrades"] == 441
        assert frame.iloc[0]["lastPrice"] == 96.0

    def test_cache_path_is_dated(self):
        path = helpers._bonds_cache_path()
        assert path.name.startswith("ciro_bonds_")
        assert path.suffix == ".parquet"

    async def test_get_all_bonds_reads_the_cache(self, monkeypatch, tmp_path):
        from pandas import DataFrame

        target = tmp_path / "ciro_bonds_2026-07-26.parquet"
        DataFrame([{"cusip": "A"}]).to_parquet(target, index=False)
        monkeypatch.setattr(helpers, "_bonds_cache_path", lambda: target)
        frame = await helpers.get_all_bonds()
        assert list(frame["cusip"]) == ["A"]

    async def test_get_all_bonds_fetches_and_writes(self, monkeypatch, tmp_path):
        target = tmp_path / "ciro_bonds_2026-07-26.parquet"
        stale = tmp_path / "ciro_bonds_2020-01-01.parquet"
        stale.write_bytes(b"")

        async def fake(key, url, **kwargs):
            return [
                {
                    "secKey": "1",
                    "issuer": "GOC",
                    "cusip": "A",
                    "isin": "I1",
                    "figi": None,
                    "maturityDate": "2036-06-01",
                    "couponRate": "3.25",
                    "lastPrice": "96",
                    "lastYield": "3.6",
                    "totalTrades": "441",
                    "lastTradedDate": "2026-07-23",
                    "highestPrice": "97",
                    "lowestPrice": "96",
                    "bondType": "Government",
                    "originalIssueDate": "2020-06-01",
                }
            ]

        monkeypatch.setattr(helpers, "_bonds_cache_path", lambda: target)
        monkeypatch.setattr("openbb_tmx.utils.curl_session.get_json", fake)
        frame = await helpers.get_all_bonds()
        assert list(frame["cusip"]) == ["A"]
        assert target.exists()
        assert not stale.exists()

    async def test_get_all_bonds_without_cache(self, monkeypatch):
        async def fake(key, url, **kwargs):
            return [
                {
                    "secKey": "1",
                    "issuer": "GOC",
                    "cusip": "A",
                    "isin": "I1",
                    "figi": None,
                    "maturityDate": "2036-06-01",
                    "couponRate": "3.25",
                    "lastPrice": "96",
                    "lastYield": "3.6",
                    "totalTrades": "441",
                    "lastTradedDate": "2026-07-23",
                    "highestPrice": "97",
                    "lowestPrice": "96",
                    "bondType": "Government",
                    "originalIssueDate": "2020-06-01",
                }
            ]

        monkeypatch.setattr("openbb_tmx.utils.curl_session.get_json", fake)
        frame = await helpers.get_all_bonds(use_cache=False)
        assert not frame.empty


class TestUrlTransport:
    """The URL helper picks an accept type."""

    async def test_defaults_to_json(self, monkeypatch):
        seen: dict = {}

        async def fake(url, use_cache=True, accept_type="json", **kwargs):
            seen["accept"] = accept_type
            return {}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        await helpers.get_data_from_url("https://example.com/a.json")
        assert seen["accept"] == "json"

    async def test_markup_hosts_get_text(self, monkeypatch):
        seen: dict = {}

        async def fake(url, use_cache=True, accept_type="json", **kwargs):
            seen["accept"] = accept_type
            return ""

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        await helpers.get_data_from_url("https://www.m-x.ca/en/trading/data/quotes")
        assert seen["accept"] == "text"
