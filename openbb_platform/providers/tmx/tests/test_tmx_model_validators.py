"""Tests for the field validators on the TMX models."""

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic import ValidationError


class TestRequiredSymbol:
    """The models that cannot be queried without a symbol say so."""

    def test_company_filings_requires_one(self):
        from openbb_tmx.models.company_filings import TmxCompanyFilingsQueryParams

        with pytest.raises(ValidationError, match="Symbol is required"):
            TmxCompanyFilingsQueryParams(symbol="")

    def test_company_news_requires_one(self):
        from openbb_tmx.models.company_news import TmxCompanyNewsQueryParams

        with pytest.raises(OpenBBError, match="Symbol is a required field"):
            TmxCompanyNewsQueryParams(symbol=None)

    def test_price_target_consensus_requires_one(self):
        from openbb_tmx.models.price_target_consensus import (
            TmxPriceTargetConsensusQueryParams,
        )

        with pytest.raises(OpenBBError, match="Symbol is a required field"):
            TmxPriceTargetConsensusQueryParams(symbol="")


class TestIntervalValidator:
    """The historical interval is mapped onto the shapes the feed accepts."""

    @pytest.mark.parametrize(
        ("supplied", "expected"),
        [("1d", "day"), ("1W", "week"), ("1w", "week"), ("week", "week"), ("15", 15)],
    )
    def test_a_known_interval_is_mapped(self, supplied, expected):
        from openbb_tmx.models.equity_historical import (
            TmxEquityHistoricalQueryParams,
        )

        query = TmxEquityHistoricalQueryParams(symbol="AC", interval=supplied)

        assert query.interval == expected

    def test_an_unknown_interval_is_rejected(self):
        from openbb_tmx.models.equity_historical import (
            TmxEquityHistoricalQueryParams,
        )

        with pytest.raises(OpenBBError, match="Invalid interval"):
            TmxEquityHistoricalQueryParams(symbol="AC", interval="1year")


class TestQuoteDateValidator:
    """Dividend dates arrive in two shapes."""

    @pytest.mark.parametrize(
        "supplied",
        ["2026-07-31", "2026-07-31 00:00:00.000"],
    )
    def test_both_shapes_are_parsed(self, supplied):
        from openbb_tmx.models.equity_quote import TmxEquityQuoteData

        quote = TmxEquityQuoteData.model_validate(
            {"symbol": "AC", "exDividendDate": supplied}
        )

        assert quote.div_ex_date == date(2026, 7, 31)

    def test_an_absent_date_stays_none(self):
        from openbb_tmx.models.equity_quote import TmxEquityQuoteData

        quote = TmxEquityQuoteData.model_validate(
            {"symbol": "AC", "exDividendDate": None}
        )

        assert quote.div_ex_date is None


class TestPercentValidators:
    """Published percents are stored as normalized percentage points."""

    def test_index_constituent_weight(self):
        from openbb_tmx.models.index_constituents import TmxIndexConstituentsData

        assert TmxIndexConstituentsData.normalize_percent("25") == 0.25
        assert TmxIndexConstituentsData.normalize_percent(None) is None

    def test_treasury_price_yield(self):
        from openbb_tmx.models.treasury_prices import TmxTreasuryPricesData

        assert TmxTreasuryPricesData.normalize_percent("3.5") == 0.035
        assert TmxTreasuryPricesData.normalize_percent(0) is None

    def test_etf_management_fee(self):
        from openbb_tmx.models.etf_search import TmxEtfSearchData

        assert TmxEtfSearchData.normalize_percent("0.55") == pytest.approx(0.0055)
        assert TmxEtfSearchData.normalize_percent(None) is None


class TestGainersMetrics:
    """Missing metrics are zeroed, and the dividend yield is normalized."""

    def test_a_missing_metric_becomes_zero(self):
        from openbb_tmx.models.gainers import TmxGainersData

        values = TmxGainersData.check_metric({"symbol": "AC", "Volume": "-"})

        assert values["Volume"] == 0

    def test_the_dividend_yield_is_normalized(self):
        from openbb_tmx.models.gainers import TmxGainersData

        values = TmxGainersData.check_metric({"symbol": "AC", "Dividend Yield": "4.5"})

        assert values["Dividend Yield"] == 0.045

    def test_a_missing_dividend_yield_stays_none(self):
        from openbb_tmx.models.gainers import TmxGainersData

        values = TmxGainersData.check_metric({"symbol": "AC", "Dividend Yield": None})

        assert values["Dividend Yield"] is None
