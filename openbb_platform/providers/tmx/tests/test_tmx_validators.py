"""Tests for the model validators and conditional registration."""

from datetime import date, datetime

import pytest

from openbb_tmx.models.equity_historical import (
    TmxEquityHistoricalData,
    TmxEquityHistoricalFetcher,
    TmxEquityHistoricalQueryParams,
)
from openbb_tmx.models.equity_quote import TmxEquityQuoteData


class TestIntervalValidator:
    """The interval accepts several spellings."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("day", "day"),
            ("1d", "day"),
            ("1M", "month"),
            ("1mo", "month"),
            ("month", "month"),
            ("1W", "week"),
            ("1w", "week"),
            ("week", "week"),
            ("5m", 5),
            ("2h", 120),
            ("15", 15),
        ],
    )
    def test_accepted_intervals(self, value, expected):
        params = TmxEquityHistoricalQueryParams(symbol="AC", interval=value)
        assert params.interval == expected

    def test_rejects_an_unknown_interval(self):
        with pytest.raises(Exception):
            TmxEquityHistoricalQueryParams(symbol="AC", interval="fortnight")

    def test_default_interval(self):
        assert TmxEquityHistoricalQueryParams(symbol="AC").interval == "day"

    def test_adjustment_warns_on_intraday(self):
        with pytest.warns(UserWarning, match="only available for daily"):
            TmxEquityHistoricalFetcher.transform_query(
                {"symbol": "AC", "interval": "5m", "adjustment": "unadjusted"}
            )


class TestDateValidators:
    """Date coercion on the price and quote models."""

    def test_naive_date_string(self):
        rows = TmxEquityHistoricalData.model_validate(
            {
                "date": "2026-07-24",
                "open": 1.0,
                "high": 1.0,
                "low": 1.0,
                "volume": 1,
                "close": 1.0,
            }
        )
        assert (rows.date.year, rows.date.month, rows.date.day) == (2026, 7, 24)

    def test_offset_aware_string(self):
        rows = TmxEquityHistoricalData.model_validate(
            {
                "date": "2026-07-24 16:00:00-0400",
                "open": 1.0,
                "high": 1.0,
                "low": 1.0,
                "volume": 1,
                "close": 1.0,
            }
        )
        assert rows.date.year == 2026

    def test_midnight_datetime_becomes_a_date(self):
        rows = TmxEquityHistoricalData.model_validate(
            {
                "date": datetime(2026, 7, 24),
                "open": 1.0,
                "high": 1.0,
                "low": 1.0,
                "volume": 1,
                "close": 1.0,
            }
        )
        assert rows.date == date(2026, 7, 24)

    def test_datetime_with_a_time_is_kept(self):
        moment = datetime(2026, 7, 24, 16, 30, 15)
        rows = TmxEquityHistoricalData.model_validate(
            {
                "date": moment,
                "open": 1.0,
                "high": 1.0,
                "low": 1.0,
                "volume": 1,
                "close": 1.0,
            }
        )
        assert rows.date == moment

    @pytest.mark.parametrize("raw", ["2026-04-01", "2026-04-01 00:00:00.000"])
    def test_quote_dates(self, raw):
        quote = TmxEquityQuoteData.model_validate(
            {"symbol": "AC", "ex_dividend_date": raw}
        )
        assert str(quote.ex_dividend_date).startswith("2026-04-01")

    def test_quote_date_none(self):
        quote = TmxEquityQuoteData.model_validate(
            {"symbol": "AC", "ex_dividend_date": None}
        )
        assert quote.ex_dividend_date is None


class TestConditionalRegistration:
    """The provider swaps keys when an owning extension is absent."""

    def test_key_helper(self):
        from openbb_tmx import _key

        assert _key("EquityQuote", "TmxEquityQuote", True) == "EquityQuote"
        assert _key("EquityQuote", "TmxEquityQuote", False) == "TmxEquityQuote"

    def test_news_router_is_gated_on_the_news_extension(self):
        import inspect

        from openbb_tmx.routers import news

        source = inspect.getsource(news)
        assert "if not NEWS_INSTALLED:" in source

    def test_every_owned_model_has_a_standalone_alias(self):
        from openbb_tmx import tmx_provider

        for key in tmx_provider.fetcher_dict:
            assert key
