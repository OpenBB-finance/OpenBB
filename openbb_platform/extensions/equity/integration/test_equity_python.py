"""Python interface integration tests for the equity extension."""
from datetime import time

import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject

# pylint: disable=too-many-lines,redefined-outer-name


# pylint: disable=import-outside-toplevel,inconsistent-return-statements
@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12}),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "provider": "polygon",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "filing_date": "2022-10-27",
                "filing_date_lt": "2022-11-01",
                "filing_date_lte": "2022-11-01",
                "filing_date_gt": "2022-10-10",
                "filing_date_gte": "2022-10-10",
                "period_of_report_date": "2022-09-24",
                "period_of_report_date_lt": "2022-11-01",
                "period_of_report_date_lte": "2022-11-01",
                "period_of_report_date_gt": "2022-10-10",
                "period_of_report_date_gte": "2022-10-10",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "fmp",
                "cik": "0000320193",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "yfinance",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_balance(params, obb):
    result = obb.equity.fundamental.balance(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 10, "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_balance_growth(params, obb):
    result = obb.equity.fundamental.balance_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-11-05", "end_date": "2023-11-10", "provider": "fmp"}),
        ({"start_date": "2023-11-05", "end_date": "2023-11-10", "provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_equity_calendar_dividend(params, obb):
    result = obb.equity.calendar.dividend(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-11-05", "end_date": "2023-11-10", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_calendar_splits(params, obb):
    result = obb.equity.calendar.splits(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"start_date": "2023-11-09", "end_date": "2023-11-10", "provider": "fmp"}),
        ({"start_date": "2023-11-09", "end_date": "2023-11-10", "provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_equity_calendar_earnings(params, obb):
    result = obb.equity.calendar.earnings(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12}),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "provider": "polygon",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "filing_date": "2022-10-27",
                "filing_date_lt": "2022-11-01",
                "filing_date_lte": "2022-11-01",
                "filing_date_gt": "2022-10-10",
                "filing_date_gte": "2022-10-10",
                "period_of_report_date": "2022-09-24",
                "period_of_report_date_lt": "2022-11-01",
                "period_of_report_date_lte": "2022-11-01",
                "period_of_report_date_gt": "2022-10-10",
                "period_of_report_date_gte": "2022-10-10",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "fmp",
                "cik": "0000320193",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "yfinance",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_cash(params, obb):
    result = obb.equity.fundamental.cash(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 10, "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_cash_growth(params, obb):
    result = obb.equity.fundamental.cash_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_management_compensation(params, obb):
    result = obb.equity.fundamental.management_compensation(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_historical_splits(params, obb):
    result = obb.equity.fundamental.historical_splits(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"symbol": "AAPL", "provider": "fmp"}),
        (
            {
                "symbol": "AAPL",
                "limit": 100,
                "provider": "intrinio",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_dividends(params, obb):
    result = obb.equity.fundamental.dividends(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_employee_count(params, obb):
    result = obb.equity.fundamental.employee_count(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 30}),
    ],
)
@pytest.mark.integration
def test_equity_estimates_historical(params, obb):
    result = obb.equity.estimates.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12}),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "provider": "polygon",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "filing_date": "2022-10-27",
                "filing_date_lt": "2022-11-01",
                "filing_date_lte": "2022-11-01",
                "filing_date_gt": "2022-10-10",
                "filing_date_gte": "2022-10-10",
                "period_of_report_date": "2022-09-24",
                "period_of_report_date_lt": "2022-11-01",
                "period_of_report_date_lte": "2022-11-01",
                "period_of_report_date_gt": "2022-10-10",
                "period_of_report_date_gte": "2022-10-10",
            }
        ),
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "limit": 12,
                "period": "annual",
                "cik": "0000320193",
            }
        ),
        (
            {
                "provider": "yfinance",
                "symbol": "AAPL",
                "limit": 12,
                "period": "annual",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_income(params, obb):
    result = obb.equity.fundamental.income(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10, "period": "annual", "provider": "fmp"})],
)
@pytest.mark.integration
def test_equity_fundamental_income_growth(params, obb):
    result = obb.equity.fundamental.income_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "limit": 10,
            }
        ),
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "limit": 10,
                "transaction_type": None,
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "limit": 10,
                "start_date": "2021-01-01",
                "end_date": "2023-06-06",
                "ownership_type": None,
                "sort_by": "updated_on",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_ownership_insider_trading(params, obb):
    result = obb.equity.ownership.insider_trading(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "include_current_quarter": True,
                "date": "2021-09-30",
                "provider": "fmp",
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "limit": 100,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_ownership_institutional(params, obb):
    result = obb.equity.ownership.institutional(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "limit": 100,
                "provider": "intrinio",
            }
        ),
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-11-01",
                "status": "priced",
                "provider": "nasdaq",
                "is_spo": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_calendar_ipo(params, obb):
    result = obb.equity.calendar.ipo(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 100}),
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 100,
                "with_ttm": False,
            }
        ),
        ({"provider": "intrinio", "symbol": "AAPL", "period": "annual", "limit": 100}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_metrics(params, obb):
    result = obb.equity.fundamental.metrics(**params)
    assert result
    assert isinstance(result, OBBject)
    if isinstance(result.results, list):
        assert len(result.results) > 0
    else:
        assert result.results is not None


@parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_management(params, obb):
    result = obb.equity.fundamental.management(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_overview(params, obb):
    result = obb.equity.fundamental.overview(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "date": "2023-01-01", "page": 1, "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_ownership_major_holders(params, obb):
    result = obb.equity.ownership.major_holders(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_estimates_price_target(params, obb):
    result = obb.equity.estimates.price_target(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


@parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_estimates_consensus(params, obb):
    result = obb.equity.estimates.consensus(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_ratios(params, obb):
    result = obb.equity.fundamental.ratios(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "structure": "flat",
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_revenue_per_geography(params, obb):
    result = obb.equity.fundamental.revenue_per_geography(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "structure": "flat",
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_revenue_per_segment(params, obb):
    result = obb.equity.fundamental.revenue_per_segment(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "form_type": "1", "limit": 100, "provider": "fmp"}),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "start_date": "2021-01-01",
                "end_date": "2023-11-01",
                "form_type": None,
                "limit": 100,
                "thea_enabled": None,
            }
        ),
        (
            {
                "symbol": "AAPL",
                "limit": 3,
                "type": "8-K",
                "cik": None,
                "provider": "sec",
                "use_cache": False,
            }
        ),
        (
            {
                "cik": "0001067983",
                "limit": 3,
                "type": "10-Q",
                "symbol": None,
                "provider": "sec",
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_filings(params, obb):
    result = obb.equity.fundamental.filings(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"symbol": "AAPL", "provider": "fmp"}),
        ({"symbol": "AAPL", "provider": "intrinio"}),
    ],
)
@pytest.mark.integration
def test_equity_ownership_share_statistics(params, obb):
    result = obb.equity.ownership.share_statistics(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "year": 2023}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_transcript(params, obb):
    result = obb.equity.fundamental.transcript(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_equity_compare_peers(params, obb):
    result = obb.equity.compare.peers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "adjusted": True,
                "extended_hours": True,
                "month": "2023-01",
                "output_size": "full",
                "provider": "alpha_vantage",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "interval": "1m",
            }
        ),
        (
            {
                "adjusted": True,
                "extended_hours": False,
                "output_size": "full",
                "month": "2023-01",
                "provider": "alpha_vantage",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "provider": "cboe",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "interval": "1m",
            }
        ),
        (
            {
                "provider": "cboe",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "limit": "30",
                "provider": "fmp",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "interval": "1m",
            }
        ),
        (
            {
                "limit": "30",
                "provider": "fmp",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "timezone": "UTC",
                "source": "realtime",
                "start_time": time(5, 30, 0),
                "end_time": time(12, 0, 0),
                "provider": "intrinio",
                "symbol": "AAPL",
                "start_date": "2023-06-01",
                "end_date": "2023-06-03",
                "interval": "1h",
            }
        ),
        (
            {
                "timezone": "UTC",
                "source": "realtime",
                "start_time": time(5, 30, 0),
                "end_time": time(12, 0, 0),
                "provider": "intrinio",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "sort": "desc",
                "limit": "49999",
                "adjusted": "True",
                "provider": "polygon",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-03",
                "interval": "1m",
            }
        ),
        (
            {
                "sort": "desc",
                "limit": "49999",
                "adjusted": "True",
                "provider": "polygon",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "prepost": False,
                "include": True,
                "adjusted": False,
                "ignore_tz": True,
                "provider": "yfinance",
                "symbol": "AAPL",
                "start_date": "2023-06-01",
                "end_date": "2023-06-03",
                "interval": "1h",
            }
        ),
        (
            {
                "prepost": False,
                "include": True,
                "adjusted": False,
                "ignore_tz": True,
                "provider": "yfinance",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "provider": "tiingo",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "provider": "tiingo",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1M",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_price_historical(params, obb):
    if params.get("provider") == "alpha_vantage":
        pytest.skip("skipping alpha_vantage")

    result = obb.equity.price.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_multiples(params, obb):
    result = obb.equity.fundamental.multiples(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"query": "ebit", "limit": 100, "provider": "intrinio"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_search_attributes(params, obb):
    result = obb.equity.fundamental.search_attributes(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "tag": "ebit",
                "frequency": "yearly",
                "limit": 1000,
                "type": None,
                "start_date": "2013-01-01",
                "end_date": "2023-01-01",
                "sort": "desc",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_historical_attributes(params, obb):
    result = obb.equity.fundamental.historical_attributes(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "tag": "ceo",
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "tag": "ceo",
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "MSFT",
                "tag": "ebitda",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_latest_attributes(params, obb):
    result = obb.equity.fundamental.latest_attributes(**params)
    assert result
    assert isinstance(result, OBBject)
    if isinstance(result.results, list):
        assert len(result.results) > 0
    else:
        assert result.results is not None


@parametrize(
    "params",
    [
        ({"query": "AAPL", "is_symbol": True, "provider": "cboe"}),
        ({"query": "Apple", "provider": "sec", "use_cache": False, "is_fund": False}),
        ({"query": "", "provider": "nasdaq", "use_cache": False, "is_etf": True}),
        ({"query": "gold", "provider": "intrinio", "active": True, "limit": 100}),
    ],
)
@pytest.mark.integration
def test_equity_search(params, obb):
    result = obb.equity.search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "industry": "REIT",
                "sector": "Real Estate",
                "mktcap_min": None,
                "mktcap_max": None,
                "price_min": None,
                "price_max": None,
                "volume_min": None,
                "volume_max": None,
                "dividend_min": None,
                "dividend_max": None,
                "is_active": True,
                "is_etf": False,
                "beta_min": None,
                "beta_max": None,
                "country": "US",
                "exchange": "nyse",
                "limit": None,
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_screener(params, obb):
    result = obb.equity.screener(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"source": "iex", "provider": "intrinio", "symbol": "AAPL"}),
        ({"symbol": "AAPL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_price_quote(params, obb):
    result = obb.equity.price.quote(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results is not None


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "cboe"}),
        ({"provider": "intrinio", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_equity_profile(params, obb):
    result = obb.equity.profile(**params)
    assert result
    assert isinstance(result, OBBject)
    if isinstance(result.results, list):
        assert len(result.results) > 0
    else:
        assert result.results is not None


@parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_equity_discovery_gainers(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.discovery.gainers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_equity_discovery_losers(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.discovery.losers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_equity_discovery_active(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.discovery.active(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_price_performance(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.price.performance(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_undervalued_large_caps(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.discovery.undervalued_large_caps(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_undervalued_growth(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.discovery.undervalued_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_aggressive_small_caps(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.discovery.aggressive_small_caps(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_growth_tech(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.discovery.growth_tech(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"limit": 10, "provider": "nasdaq"})],
)
@pytest.mark.integration
def test_equity_discovery_top_retail(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.discovery.top_retail(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"provider": "seeking_alpha"})],
)
@pytest.mark.integration
def test_equity_discovery_upcoming_release_days(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.discovery.upcoming_release_days(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "start_date": None,
                "end_date": None,
                "limit": 10,
                "form_type": None,
                "is_done": None,
                "provider": "fmp",
            }
        ),
        (
            {
                "start_date": "2023-11-06",
                "end_date": "2023-11-07",
                "limit": 50,
                "form_type": "10-Q",
                "is_done": "true",
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_discovery_filings(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.discovery.filings(**params)
    assert result
    assert isinstance(result, OBBject)
    if isinstance(result.results, list):
        assert len(result.results) > 0
    else:
        assert result.results is not None


@parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"limit": 24, "provider": "sec", "symbol": "AAPL", "skip_reports": 1}),
    ],
)
@pytest.mark.integration
def test_equity_shorts_fails_to_deliver(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.shorts.fails_to_deliver(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "stockgrid"})],
)
@pytest.mark.integration
def test_equity_shorts_short_volume(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.shorts.short_volume(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "finra"})],
)
@pytest.mark.integration
def test_equity_shorts_short_interest(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.shorts.short_interest(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "CLOV",
                "provider": "polygon",  # premium endpoint
                "timestamp_gt": "2023-10-26T15:20:00.000000000-04:00",
                "timestamp_lt": "2023-10-26T15:30:00.000000000-04:00",
                "limit": 5000,
                "timestamp_gte": None,
                "timestamp_lte": None,
                "date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_price_nbbo(params, obb):
    result = obb.equity.price.nbbo(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"tier": "T1", "is_ats": True, "provider": "finra", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_equity_darkpool_otc(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.darkpool.otc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "fmp", "market": "EURONEXT"}),
        ({"provider": "polygon"}),  # premium endpoint
    ],
)
@pytest.mark.integration
def test_equity_market_snapshots(params, obb):
    result = obb.equity.market_snapshots(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 5, "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_historical_eps(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.fundamental.historical_eps(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"provider": "tiingo", "symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_fundamental_trailing_dividend_yield(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.fundamental.trailing_dividend_yield(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
