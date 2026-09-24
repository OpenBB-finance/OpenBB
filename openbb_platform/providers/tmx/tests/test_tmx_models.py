"""Offline tests for the TMX fetchers."""

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_tmx.models.calendar_earnings import TmxCalendarEarningsFetcher
from openbb_tmx.models.company_filings import TmxCompanyFilingsFetcher
from openbb_tmx.models.company_news import TmxCompanyNewsFetcher
from openbb_tmx.models.equity_historical import TmxEquityHistoricalFetcher
from openbb_tmx.models.equity_profile import TmxEquityProfileFetcher
from openbb_tmx.models.equity_quote import TmxEquityQuoteFetcher
from openbb_tmx.models.equity_short_interest import TmxShortInterestFetcher
from openbb_tmx.models.equity_trades import TmxEquityTradesFetcher
from openbb_tmx.models.gainers import TmxGainersFetcher
from openbb_tmx.models.historical_dividends import TmxHistoricalDividendsFetcher
from openbb_tmx.models.historical_splits import TmxHistoricalSplitsFetcher
from openbb_tmx.models.insider_trading import TmxInsiderTradingFetcher
from openbb_tmx.models.market_movers import TmxMarketMoversFetcher
from openbb_tmx.models.price_target_consensus import TmxPriceTargetConsensusFetcher

CREDS: dict = {}


class TestQuoteAndProfile:
    """Quote and profile come from the same operation."""

    @pytest.mark.asyncio
    async def test_quote(self, gql):
        rows = await TmxEquityQuoteFetcher.fetch_data({"symbol": "AC"}, CREDS)
        assert rows[0].symbol == "AC"
        assert rows[0].last_price == 23.27

    @pytest.mark.asyncio
    async def test_quote_accepts_many_symbols(self, gql):
        await TmxEquityQuoteFetcher.fetch_data({"symbol": "AC,BNS"}, CREDS)
        assert len(gql) == 2

    @pytest.mark.asyncio
    async def test_quote_warns_on_empty(self, monkeypatch):
        async def empty(*args, **kwargs):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", empty)

        with pytest.warns(UserWarning, match="Could not get data"):
            rows = await TmxEquityQuoteFetcher.fetch_data({"symbol": "ZZZZ"}, CREDS)

        assert rows == []

    @pytest.mark.asyncio
    async def test_profile(self, gql):
        rows = await TmxEquityProfileFetcher.fetch_data({"symbol": "AC"}, CREDS)
        assert rows[0].name == "Air Canada"


class TestHistories:
    """Price history models."""

    @pytest.mark.asyncio
    async def test_equity_historical(self, gql):
        rows = await TmxEquityHistoricalFetcher.fetch_data(
            {"symbol": "AC", "interval": "1d"}, CREDS
        )
        assert rows
        assert rows[-1].close == 23.27

    @pytest.mark.asyncio
    async def test_monthly_interval_uses_the_timeseries(self, gql):
        rows = await TmxEquityHistoricalFetcher.fetch_data(
            {"symbol": "AC", "interval": "1M"}, CREDS
        )
        assert rows


class TestCorporateRecords:
    """Dividends, splits, filings, insiders, and estimates."""

    @pytest.mark.asyncio
    async def test_dividends(self, gql):
        rows = await TmxHistoricalDividendsFetcher.fetch_data({"symbol": "BNS"}, CREDS)
        assert rows[0].amount == 1.06

    @pytest.mark.asyncio
    async def test_splits(self, gql):
        rows = await TmxHistoricalSplitsFetcher.fetch_data({"symbol": "BNS"}, CREDS)
        assert rows[0].ratio == 0.5

    @pytest.mark.asyncio
    async def test_splits_empty(self, monkeypatch):
        async def empty(*args, **kwargs):
            return {"getSplitsForSymbol": []}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", empty)

        with pytest.raises(EmptyDataError):
            await TmxHistoricalSplitsFetcher.fetch_data({"symbol": "AC"}, CREDS)

    @pytest.mark.asyncio
    async def test_a_symbol_that_never_split_is_reported_as_empty(self, monkeypatch):
        """The feed faults instead of answering for a symbol with no splits."""
        from openbb_core.app.model.abstract.error import OpenBBError

        async def faulting(*args, **kwargs):
            raise OpenBBError(
                "TMX GraphQL error for getSplitsForSymbol ->"
                + " Cannot read properties of undefined (reading 'length')"
            )

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", faulting)

        with pytest.raises(EmptyDataError, match="No splits were returned for AC"):
            await TmxHistoricalSplitsFetcher.fetch_data({"symbol": "AC"}, CREDS)

    @pytest.mark.asyncio
    async def test_any_other_split_fault_is_raised(self, monkeypatch):
        from openbb_core.app.model.abstract.error import OpenBBError

        async def faulting(*args, **kwargs):
            raise OpenBBError("TMX GraphQL error for getSplitsForSymbol -> Forbidden")

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", faulting)

        with pytest.raises(OpenBBError, match="Forbidden"):
            await TmxHistoricalSplitsFetcher.fetch_data({"symbol": "AC"}, CREDS)

    @pytest.mark.asyncio
    async def test_filings(self, gql):
        rows = await TmxCompanyFilingsFetcher.fetch_data({"symbol": "AC"}, CREDS)
        assert rows[0].report_type == "AIF"

    @pytest.mark.asyncio
    async def test_insider_trading(self, gql):
        rows = await TmxInsiderTradingFetcher.fetch_data({"symbol": "AC"}, CREDS)
        assert rows

    @pytest.mark.asyncio
    async def test_insider_trading_empty(self, monkeypatch):
        async def empty(*args, **kwargs):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", empty)

        with pytest.raises(EmptyDataError):
            await TmxInsiderTradingFetcher.fetch_data({"symbol": "AC"}, CREDS)

    @pytest.mark.asyncio
    async def test_price_target_consensus(self, gql):
        rows = await TmxPriceTargetConsensusFetcher.fetch_data({"symbol": "AC"}, CREDS)
        assert rows[0].total_analysts == 12

    @pytest.mark.asyncio
    async def test_calendar_earnings(self, gql):
        rows = await TmxCalendarEarningsFetcher.fetch_data(
            {"start_date": "2026-07-24", "end_date": "2026-07-24"}, CREDS
        )
        assert rows[0].symbol == "AC"

    @pytest.mark.asyncio
    async def test_a_day_with_nothing_scheduled_is_skipped(self, monkeypatch):
        """The feed faults rather than answering for an empty day."""
        from openbb_core.app.model.abstract.error import OpenBBError

        from .conftest import SAMPLES

        async def sometimes(operation, query, variables=None, **kwargs):
            if variables["date"] == "2026-07-24":
                raise OpenBBError(
                    "TMX GraphQL error for getEnhancedEarningsForDate ->"
                    + " Cannot read properties of undefined (reading 'map')"
                )

            return SAMPLES[operation]

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", sometimes)
        rows = await TmxCalendarEarningsFetcher.fetch_data(
            {"start_date": "2026-07-23", "end_date": "2026-07-24"}, CREDS
        )

        assert [str(r.report_date) for r in rows] == ["2026-07-23"]

    @pytest.mark.asyncio
    async def test_any_other_earnings_fault_is_raised(self, monkeypatch):
        from openbb_core.app.model.abstract.error import OpenBBError

        async def faulting(*args, **kwargs):
            raise OpenBBError(
                "TMX GraphQL error for getEnhancedEarningsForDate -> Forbidden"
            )

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", faulting)

        with pytest.raises(OpenBBError, match="Forbidden"):
            await TmxCalendarEarningsFetcher.fetch_data(
                {"start_date": "2026-07-23", "end_date": "2026-07-24"}, CREDS
            )

    @pytest.mark.asyncio
    async def test_company_news(self, gql):
        rows = await TmxCompanyNewsFetcher.fetch_data({"symbol": "AC"}, CREDS)
        assert rows[0].title.startswith("Air Canada")


class TestMarketWide:
    """Movers, curated lists, trades, and short interest."""

    @pytest.mark.asyncio
    async def test_market_movers(self, gql):
        rows = await TmxMarketMoversFetcher.fetch_data({}, CREDS)
        assert rows[0].symbol == "AC"
        assert rows[0].change_percent == pytest.approx(0.0274)

    @pytest.mark.asyncio
    async def test_market_movers_empty(self, monkeypatch):
        async def empty(*args, **kwargs):
            return {"getMarketMovers": []}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", empty)

        with pytest.raises(EmptyDataError):
            await TmxMarketMoversFetcher.fetch_data({}, CREDS)

    @pytest.mark.asyncio
    async def test_gainers(self, gql):
        rows = await TmxGainersFetcher.fetch_data({"category": "volume"}, CREDS)
        assert rows[0].symbol == "AC"

    @pytest.mark.asyncio
    async def test_gainers_empty(self, monkeypatch):
        async def empty(*args, **kwargs):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", empty)

        with pytest.raises(EmptyDataError):
            await TmxGainersFetcher.fetch_data({"category": "volume"}, CREDS)

    @pytest.mark.asyncio
    async def test_trades(self, gql):
        rows = await TmxEquityTradesFetcher.fetch_data({"symbol": "AC"}, CREDS)
        assert rows[0].buyer_name == "RBC"
        assert rows[0].seller_name == "CIBC"

    @pytest.mark.asyncio
    async def test_trades_empty(self, monkeypatch):
        async def empty(*args, **kwargs):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", empty)

        with pytest.raises(EmptyDataError):
            await TmxEquityTradesFetcher.fetch_data({"symbol": "AC"}, CREDS)

    @pytest.mark.asyncio
    async def test_short_interest(self, gql):
        rows = await TmxShortInterestFetcher.fetch_data({"symbol": "AC"}, CREDS)
        assert rows[0].short_interest == 6443193
        assert rows[0].short_interest_percent == pytest.approx(0.000231)

    @pytest.mark.asyncio
    async def test_short_interest_empty(self, monkeypatch):
        async def empty(*args, **kwargs):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", empty)

        with pytest.raises(EmptyDataError):
            await TmxShortInterestFetcher.fetch_data({"symbol": "AC"}, CREDS)
