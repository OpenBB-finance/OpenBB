"""Tests for YFinance fetchers."""

from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_yfinance.models.active import YFActiveFetcher
from openbb_yfinance.models.aggressive_small_caps import YFAggressiveSmallCapsFetcher
from openbb_yfinance.models.available_indices import YFinanceAvailableIndicesFetcher
from openbb_yfinance.models.balance_sheet import YFinanceBalanceSheetFetcher
from openbb_yfinance.models.cash_flow import YFinanceCashFlowStatementFetcher
from openbb_yfinance.models.company_news import YFinanceCompanyNewsFetcher
from openbb_yfinance.models.crypto_historical import YFinanceCryptoHistoricalFetcher
from openbb_yfinance.models.currency_historical import YFinanceCurrencyHistoricalFetcher
from openbb_yfinance.models.equity_historical import YFinanceEquityHistoricalFetcher
from openbb_yfinance.models.equity_profile import YFinanceEquityProfileFetcher
from openbb_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher
from openbb_yfinance.models.equity_screener import YFinanceEquityScreenerFetcher
from openbb_yfinance.models.etf_info import YFinanceEtfInfoFetcher
from openbb_yfinance.models.futures_curve import YFinanceFuturesCurveFetcher
from openbb_yfinance.models.futures_historical import YFinanceFuturesHistoricalFetcher
from openbb_yfinance.models.gainers import YFGainersFetcher
from openbb_yfinance.models.growth_tech_equities import YFGrowthTechEquitiesFetcher
from openbb_yfinance.models.historical_dividends import (
    YFinanceHistoricalDividendsFetcher,
)
from openbb_yfinance.models.income_statement import YFinanceIncomeStatementFetcher
from openbb_yfinance.models.index_historical import (
    YFinanceIndexHistoricalFetcher,
)
from openbb_yfinance.models.key_executives import YFinanceKeyExecutivesFetcher
from openbb_yfinance.models.key_metrics import YFinanceKeyMetricsFetcher
from openbb_yfinance.models.losers import YFLosersFetcher
from openbb_yfinance.models.options_chains import YFinanceOptionsChainsFetcher
from openbb_yfinance.models.price_target_consensus import (
    YFinancePriceTargetConsensusFetcher,
)
from openbb_yfinance.models.share_statistics import YFinanceShareStatisticsFetcher
from openbb_yfinance.models.undervalued_growth_equities import (
    YFUndervaluedGrowthEquitiesFetcher,
)
from openbb_yfinance.models.undervalued_large_caps import YFUndervaluedLargeCapsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


def scrub_string(key, value):
    """Scrub a string from the response."""

    def before_record_response(response):
        if key == "<!doctype html>":
            response_body = response["body"]["string"]
            if isinstance(response_body, bytes):
                response_body = response_body.decode("utf-8", errors="ignore")

            # Check if the key (HTML doctype) is in the response body
            if key.lower() in response_body.lower():
                response["body"]["string"] = bytes("MOCK_RESPONSE", "utf-8")

        if key in response["headers"]:
            response["headers"][key] = value
        return response

    return before_record_response


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("Cookie", "MOCK_COOKIE"),
            ("crumb", "MOCK_CRUMB"),
        ],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("crumb", "MOCK_CRUMB"),
            ("date", "MOCK_DATE"),
            ("corsDomain", "MOCK_CORS"),
        ],
        "before_record_response": [
            scrub_string("Set-Cookie", "MOCK_COOKIE"),
            scrub_string("X-Envoy-Decorator-Operation", "MOCK_OPERATION"),
            scrub_string("Y-Rid", "MOCK_RID"),
            scrub_string("Content-Security-Policy", "MOCK_CSP"),
            scrub_string("<!doctype html>", "MOCK_RESPONSE"),
            scrub_string("Link", "MOCK_LINK"),
            scrub_string("Report-To", "MOCK_REPORT"),
            scrub_string("Expect-Ct", "MOCK_EXPECT_CT"),
        ],
    }


@pytest.mark.record_curl
def test_y_finance_crypto_historical_fetcher(credentials=test_credentials):
    """Test YFinanceCryptoHistoricalFetcher."""
    params = {
        "symbol": "BTCUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
    }

    fetcher = YFinanceCryptoHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_currency_historical_fetcher(credentials=test_credentials):
    """Test YFinanceCurrencyHistoricalFetcher."""
    params = {
        "symbol": "EURUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceCurrencyHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_index_historical_fetcher(credentials=test_credentials):
    """Test YFinanceIndexHistoricalFetcher."""
    params = {
        "symbol": "^GSPC",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceIndexHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_equity_historical_fetcher(credentials=test_credentials):
    """Test YFinanceEquityHistoricalFetcher."""
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
    }

    fetcher = YFinanceEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_historical_dividends_fetcher(credentials=test_credentials):
    """Test YFinanceHistoricalDividendsFetcher."""
    params = {"symbol": "IBM"}

    fetcher = YFinanceHistoricalDividendsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_futures_historical_fetcher(credentials=test_credentials):
    """Test YFinanceFuturesHistoricalFetcher."""
    params = {
        "symbol": "ES=F",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceFuturesHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_options_chains_fetcher(credentials=test_credentials):
    """Test YFinanceOptionsChainsFetcher."""

    params = {"symbol": "OXY"}

    fetcher = YFinanceOptionsChainsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.skip("Unreliable amount of data while recording test.")
@pytest.mark.record_curl
def test_y_finance_futures_curve_fetcher(credentials=test_credentials):
    """Test YFinanceFuturesCurveFetcher."""
    params = {"symbol": "ES"}

    fetcher = YFinanceFuturesCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_company_news_fetcher(credentials=test_credentials):
    """Test YFinanceCompanyNewsFetcher."""
    params = {"symbol": "AAPL,MSFT", "limit": 2}

    fetcher = YFinanceCompanyNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_balance_sheet_fetcher(credentials=test_credentials):
    """Test YFinanceBalanceSheetFetcher."""
    params = {"symbol": "AAPL"}

    fetcher = YFinanceBalanceSheetFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_cash_flow_statement_fetcher(credentials=test_credentials):
    """Test YFinanceCashFlowStatementFetcher."""
    params = {"symbol": "AAPL"}

    fetcher = YFinanceCashFlowStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_income_statement_fetcher(credentials=test_credentials):
    """Test YFinanceIncomeStatementFetcher."""
    params = {"symbol": "AAPL"}

    fetcher = YFinanceIncomeStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


def test_y_finance_available_fetcher(credentials=test_credentials):
    """Test YFinanceAvailableIndicesFetcher."""
    params = {}

    fetcher = YFinanceAvailableIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_active_fetcher(credentials=test_credentials):
    """Test YFActiveFetcher."""
    params = {"limit": 10}

    fetcher = YFActiveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_gainers_fetcher(credentials=test_credentials):
    """Test YFGainersFetcher."""
    params = {"limit": 10}

    fetcher = YFGainersFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_losers_fetcher(credentials=test_credentials):
    """Test YFLosersFetcher."""
    params = {"limit": 10}

    fetcher = YFLosersFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_undervalued_large_caps_fetcher(credentials=test_credentials):
    """Test YFUndervaluedLargeCapsFetcher."""
    params = {"limit": 10}

    fetcher = YFUndervaluedLargeCapsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_undervalued_growth_equities_fetcher(credentials=test_credentials):
    """Test YFUndervaluedGrowthEquitiesFetcher."""
    params = {"limit": 10}

    fetcher = YFUndervaluedGrowthEquitiesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_aggressive_small_caps_fetcher(credentials=test_credentials):
    """Test YFAggressiveSmallCapsFetcher."""
    params = {"limit": 10}

    fetcher = YFAggressiveSmallCapsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_growth_tech_equities_fetcher(credentials=test_credentials):
    """Test YFGrowthTechEquitiesFetcher."""
    params = {"limit": 10}

    fetcher = YFGrowthTechEquitiesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_equity_profile_fetcher(credentials=test_credentials):
    """Test YFinanceEquityProfileFetcher."""
    params = {"symbol": "AAPL"}

    fetcher = YFinanceEquityProfileFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_equity_quote_fetcher(credentials=test_credentials):
    """Test YFinanceEquityQuoteFetcher."""
    params = {"symbol": "AAPL"}

    fetcher = YFinanceEquityQuoteFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_price_target_consensus_fetcher(credentials=test_credentials):
    """Test YFinancePriceTargetConsensusFetcher."""
    params = {"symbol": "AAPL"}

    fetcher = YFinancePriceTargetConsensusFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_share_statistics_fetcher(credentials=test_credentials):
    """Test YFinanceShareStatisticsFetcher."""
    params = {"symbol": "AAPL"}

    fetcher = YFinanceShareStatisticsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_key_executives_fetcher(credentials=test_credentials):
    """Test YFinanceKeyExecutivesFetcher."""
    params = {"symbol": "AAPL"}

    fetcher = YFinanceKeyExecutivesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_key_metrics_fetcher(
    credentials=test_credentials,
):
    """Test YFinanceKeyMetricsFetcher."""
    params = {"symbol": "AAPL"}

    fetcher = YFinanceKeyMetricsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_etf_info_fetcher(credentials=test_credentials):
    """Test YFinanceEtfInfoFetcher."""
    params = {"symbol": "QQQ"}

    fetcher = YFinanceEtfInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_curl
def test_y_finance_equity_screener_fetcher(credentials=test_credentials):
    """Test YFinanceEquityScreener."""
    params = {
        "country": "us",
        "sector": "consumer_cyclical",
        "industry": "auto_manufacturers",
        "mktcap_min": 60000000000,
        "volume_min": 5000000,
        "price_min": 10,
    }

    fetcher = YFinanceEquityScreenerFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


def test_equity_quote_no_session_parameter():
    """Test that YFinanceEquityQuoteFetcher does not pass session to Ticker."""
    from unittest.mock import patch, MagicMock
    from openbb_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher

    with patch("yfinance.Ticker") as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.get_info.return_value = {"symbol": "AAPL", "currentPrice": 150.0}
        mock_ticker.return_value = mock_instance

        import asyncio
        fetcher = YFinanceEquityQuoteFetcher()
        query = fetcher.transform_query({"symbol": "AAPL"})
        
        asyncio.run(fetcher.aextract_data(query, {}))

        # Verify Ticker was called without session parameter
        assert mock_ticker.called
        for call in mock_ticker.call_args_list:
            call_kwargs = call[1] if len(call) > 1 and call[1] else {}
            assert "session" not in call_kwargs, "Ticker should not be called with session parameter"


def test_company_news_no_session_parameter():
    """Test that YFinanceCompanyNewsFetcher does not pass session to Ticker."""
    from unittest.mock import patch, MagicMock
    from openbb_yfinance.models.company_news import YFinanceCompanyNewsFetcher

    with patch("yfinance.Ticker") as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.get_news.return_value = [
            {
                "id": "test-id-123",
                "content": {
                    "title": "Test",
                    "canonicalUrl": {"url": "http://test.com"},
                    "pubDate": "2025-01-01T00:00:00Z",
                    "provider": {"displayName": "TestSource"}
                }
            }
        ]
        mock_ticker.return_value = mock_instance

        import asyncio
        fetcher = YFinanceCompanyNewsFetcher()
        query = fetcher.transform_query({"symbol": "AAPL", "limit": 1})
        
        asyncio.run(fetcher.aextract_data(query, {}))

        # Verify Ticker was called without session parameter
        assert mock_ticker.called
        for call in mock_ticker.call_args_list:
            call_kwargs = call[1] if len(call) > 1 and call[1] else {}
            assert "session" not in call_kwargs, "Ticker should not be called with session parameter"


def test_equity_profile_no_session_parameter():
    """Test that YFinanceEquityProfileFetcher does not pass session to Ticker."""
    from unittest.mock import patch, MagicMock
    from openbb_yfinance.models.equity_profile import YFinanceEquityProfileFetcher

    with patch("yfinance.Ticker") as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.get_info.return_value = {"symbol": "AAPL", "longName": "Apple Inc."}
        mock_ticker.return_value = mock_instance

        import asyncio
        fetcher = YFinanceEquityProfileFetcher()
        query = fetcher.transform_query({"symbol": "AAPL"})
        
        asyncio.run(fetcher.aextract_data(query, {}))

        # Verify Ticker was called without session parameter
        assert mock_ticker.called
        for call in mock_ticker.call_args_list:
            call_kwargs = call[1] if len(call) > 1 and call[1] else {}
            assert "session" not in call_kwargs, "Ticker should not be called with session parameter"


def test_historical_dividends_no_session_parameter():
    """Test that YFinanceHistoricalDividendsFetcher does not pass session to Ticker."""
    from unittest.mock import patch, MagicMock
    from openbb_yfinance.models.historical_dividends import YFinanceHistoricalDividendsFetcher
    import pandas as pd

    with patch("yfinance.Ticker") as mock_ticker:
        mock_instance = MagicMock()
        mock_series = pd.Series([0.5, 0.6], index=pd.to_datetime(["2023-01-01", "2023-06-01"]))
        mock_instance.get_dividends.return_value = mock_series
        mock_ticker.return_value = mock_instance

        fetcher = YFinanceHistoricalDividendsFetcher()
        query = fetcher.transform_query({"symbol": "AAPL"})
        
        fetcher.extract_data(query, {})

        # Verify Ticker was called without session parameter
        assert mock_ticker.called
        for call in mock_ticker.call_args_list:
            call_kwargs = call[1] if len(call) > 1 and call[1] else {}
            assert "session" not in call_kwargs, "Ticker should not be called with session parameter"