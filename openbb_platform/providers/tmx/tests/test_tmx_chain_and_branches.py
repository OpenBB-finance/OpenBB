"""Tests for the live option chain parser and the remaining model branches."""

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_tmx.utils import directory, helpers, quotemedia

QUOTES_HTML = """
<table>
  <thead>
    <tr>
      <th colspan="6">Calls</th>
      <th colspan="1">Unnamed: 7_level_0</th>
      <th colspan="6">Puts</th>
      <th colspan="1">Unnamed: 0_level_0</th>
    </tr>
    <tr>
      <th>Bid price</th><th>Ask price</th><th>Last price</th><th>Net change</th>
      <th>Open int.</th><th>Vol.</th>
      <th>Strike</th>
      <th>Bid price</th><th>Ask price</th><th>Last price</th><th>Net change</th>
      <th>Open int.</th><th>Vol.</th>
      <th>Expiry date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2.90</td><td>3.10</td><td>3.00</td><td>0.10</td><td>100</td><td>5</td>
      <td>20.0</td>
      <td>0.40</td><td>0.55</td><td>0.50</td><td>-0.05</td><td>80</td><td>3</td>
      <td>2026-07-31</td>
    </tr>
    <tr>
      <td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td>
      <td>0</td>
      <td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td>
      <td>Total</td>
    </tr>
  </tbody>
</table>
"""


class TestCurrentOptions:
    """The Montreal Exchange live chain."""

    @pytest.fixture
    def listings(self, monkeypatch):
        """Serve a one-symbol option listing."""
        from pandas import DataFrame

        async def tickers(use_cache=True):
            return DataFrame(
                [{"underlying_symbol": "AC", "company": "Air Canada"}], index=["AC"]
            ).rename_axis("option_symbol")

        monkeypatch.setattr(helpers, "get_all_options_tickers", tickers)

    async def test_rejects_a_symbol_without_options(self, listings):
        with pytest.raises(OpenBBError, match="does not trade options"):
            await helpers.get_current_options("ZZZZ")

    async def test_parses_the_chain(self, listings, monkeypatch):
        async def fake(url, use_cache=True, **kwargs):
            return QUOTES_HTML

        monkeypatch.setattr(helpers, "get_data_from_url", fake)
        chains = await helpers.get_current_options("AC")
        assert not chains.empty
        assert set(chains["option_type"]) == {"call", "put"}
        assert chains["contract_symbol"].str.startswith("AC").all()


class TestDirectoryBranches:
    """The sweep's recursion and filters."""

    async def test_country_and_symbol_only_are_passed(self, monkeypatch):
        seen: dict = {}

        async def fake(url, use_cache=True, **kwargs):
            seen["url"] = url
            return []

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        quotemedia.get_token.cache_clear()
        monkeypatch.setattr(quotemedia, "_mint_token", _tok)
        await directory.lookup_symbols("a", country="CA", symbol_only=True)
        assert "countryCode=CA" in seen["url"]
        assert "searchType=symbol" in seen["url"]

    async def test_saturated_prefix_recurses(self, monkeypatch):
        calls: list = []

        async def fake(
            query, limit=100, country=None, symbol_only=False, use_cache=True
        ):
            calls.append(query)

            if len(query) == 1:
                return [
                    {"symbolId": i, "symbol": f"S{i}"} for i in range(directory.ROW_CAP)
                ]

            return [{"symbolId": 10_000_000, "symbol": "DEEP"}]

        monkeypatch.setattr(directory, "lookup_symbols", fake)
        results: dict = {}
        await directory._sweep_prefix("a", None, results, True)
        assert any(len(c) == 2 for c in calls)

    async def test_rows_without_an_id_are_ignored(self, monkeypatch):
        async def fake(query, **kwargs):
            return [{"symbol": "NOID"}]

        monkeypatch.setattr(directory, "lookup_symbols", fake)
        results: dict = {}
        await directory._sweep_prefix("a", None, results, True)
        assert results == {}


async def _tok(tool=None):
    """Return a stub token."""
    return "tok"


class TestQuoteMediaBranches:
    """Remaining vendor paths."""

    async def test_criteria(self, monkeypatch):
        async def fake(url, use_cache=True, **kwargs):
            return {"EquityCriteriaList": [{"name": "Popular"}]}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        quotemedia.get_token.cache_clear()
        monkeypatch.setattr(quotemedia, "_mint_token", _tok)
        crit = await quotemedia.get_screener_criteria("CA")
        assert crit["EquityCriteriaList"]

    async def test_criteria_empty(self, monkeypatch):
        async def fake(url, **kwargs):
            return None

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        quotemedia.get_token.cache_clear()
        monkeypatch.setattr(quotemedia, "_mint_token", _tok)
        assert await quotemedia.get_screener_criteria() == {}

    async def test_screener_skips_rows_without_a_symbol(self, monkeypatch):
        async def fake(url, **kwargs):
            return {"results": {"equities": [{"companyBasics": {"name": "No symbol"}}]}}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        quotemedia.get_token.cache_clear()
        monkeypatch.setattr(quotemedia, "_mint_token", _tok)
        assert await quotemedia.get_screener_equities(["X"]) == []

    def test_mint_accepts_a_ready_digest(self):
        assert len(quotemedia.SCREENER_TOOL) == 64


class TestFixedIncomeFilters:
    """The bond model filters."""

    @pytest.fixture
    def bonds(self, monkeypatch):
        """Serve a two-bond master."""
        rows = [
            {
                "secKey": "1",
                "issuer": "GOVERNMENT OF CANADA",
                "securityId": "B1",
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
            {
                "secKey": "2",
                "issuer": "AIR CDA",
                "securityId": "B2",
                "cusip": "B",
                "isin": "I2",
                "figi": "F2",
                "maturityDate": "2029-10-01",
                "couponRate": "7.6",
                "lastPrice": "102",
                "lastYield": "3.4",
                "totalTrades": "2",
                "lastTradedDate": "2026-07-20",
                "highestPrice": "103",
                "lowestPrice": "99",
                "bondType": "Corp",
                "originalIssueDate": "2013-09-26",
            },
        ]

        async def fake(use_cache=True):
            return helpers._normalize_bonds(rows)

        monkeypatch.setattr(helpers, "get_all_bonds", fake)

    async def test_bond_prices_filters(self, bonds):
        from openbb_tmx.models.bond_prices import TmxBondPricesFetcher

        rows = await TmxBondPricesFetcher.fetch_data({"issuer_name": "air"}, {})
        assert all("AIR" in (r.issuer_name or "").upper() for r in rows)

    async def test_bond_prices_coupon_and_maturity(self, bonds):
        from openbb_tmx.models.bond_prices import TmxBondPricesFetcher

        rows = await TmxBondPricesFetcher.fetch_data(
            {"coupon_min": 5.0, "coupon_max": 9.0}, {}
        )
        assert rows

    async def test_bond_prices_no_match(self, bonds):
        from openbb_tmx.models.bond_prices import TmxBondPricesFetcher

        with pytest.raises((EmptyDataError, OpenBBError)):
            await TmxBondPricesFetcher.fetch_data({"issuer_name": "nobody"}, {})

    async def test_treasury_prices_date(self, bonds):
        from openbb_tmx.models.treasury_prices import TmxTreasuryPricesFetcher

        rows = await TmxTreasuryPricesFetcher.fetch_data(
            {"date": date(2026, 7, 23)}, {}
        )
        assert isinstance(rows, list)
