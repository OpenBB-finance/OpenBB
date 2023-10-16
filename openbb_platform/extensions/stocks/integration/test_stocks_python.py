"""Test stocks extension."""
from datetime import time

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12}),
        (
            {
                "type": "reported",
                "year": 2022,
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "company_name": "Apple Inc.",
                "company_name_search": "Apple Inc.",
                "sic": "3571",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "provider": "polygon",
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
def test_stocks_fa_balance(params, obb):
    result = obb.stocks.fa.balance(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 10}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_balance_growth(params, obb):
    result = obb.stocks.fa.balance_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_fa_cal(params, obb):
    result = obb.stocks.fa.cal(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12}),
        (
            {
                "type": "reported",
                "year": 2022,
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "company_name": "Apple Inc.",
                "company_name_search": "Apple Inc.",
                "sic": "3571",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "provider": "polygon",
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
def test_stocks_fa_cash(params, obb):
    result = obb.stocks.fa.cash(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 10}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_cash_growth(params, obb):
    result = obb.stocks.fa.cash_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_comp(params, obb):
    result = obb.stocks.fa.comp(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_fa_comsplit(params, obb):
    result = obb.stocks.fa.comsplit(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_divs(params, obb):
    result = obb.stocks.fa.divs(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 50}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_earning(params, obb):
    result = obb.stocks.fa.earning(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_emp(params, obb):
    result = obb.stocks.fa.emp(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 30}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_est(params, obb):
    result = obb.stocks.fa.est(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12}),
        (
            {
                "type": "reported",
                "year": 2022,
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "company_name": "Apple Inc.",
                "company_name_search": "Apple Inc.",
                "sic": "3571",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "provider": "polygon",
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
def test_stocks_fa_income(params, obb):
    result = obb.stocks.fa.income(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10, "period": "annual"})],
)
@pytest.mark.integration
def test_stocks_fa_income_growth(params, obb):
    result = obb.stocks.fa.income_growth(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "transactionType": ["P-Purchase"],
                "reportingCik": 1,
                "companyCik": 1,
                "page": 1,
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_fa_ins(params, obb):
    result = obb.stocks.fa.ins(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "include_current_quarter": True,
                "date": "2021-09-30",
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_fa_ins_own(params, obb):
    result = obb.stocks.fa.ins_own(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 100}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_metrics(params, obb):
    result = obb.stocks.fa.metrics(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_mgmt(params, obb):
    result = obb.stocks.fa.mgmt(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_overview(params, obb):
    result = obb.stocks.fa.overview(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "date": "2023-01-01", "page": 1}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_own(params, obb):
    result = obb.stocks.fa.own(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_pt(params, obb):
    result = obb.stocks.fa.pt(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"with_grade": True, "provider": "fmp", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_pta(params, obb):
    result = obb.stocks.fa.pta(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_ratios(params, obb):
    result = obb.stocks.fa.ratios(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "structure": "flat"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_revgeo(params, obb):
    result = obb.stocks.fa.revgeo(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "structure": "flat"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_revseg(params, obb):
    result = obb.stocks.fa.revseg(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "type": "1", "page": 1, "limit": 100, "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_filings(params, obb):
    result = obb.stocks.fa.filings(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_shrs(params, obb):
    result = obb.stocks.fa.shrs(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_split(params, obb):
    result = obb.stocks.fa.split(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "year": 2023, "quarter": 1}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_transcript(params, obb):
    result = obb.stocks.fa.transcript(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_ca_peers(params, obb):
    result = obb.stocks.ca.peers(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"date": "2023-01-25", "provider": "intrinio", "symbol": "AAPL"}),
        ({"provider": "cboe", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_options_chains(params, obb):
    result = obb.stocks.options.chains(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "interval": "1m",
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
                "end_date": "2023-01-02",
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
                "back_adjust": False,
                "ignore_tz": True,
                "provider": "yfinance",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "interval": "1m",
            }
        ),
        (
            {
                "prepost": False,
                "include": True,
                "adjusted": False,
                "back_adjust": False,
                "ignore_tz": True,
                "provider": "yfinance",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_load(params, obb):
    result = obb.stocks.load(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbols": "AAPL,MSFT", "limit": 20}),
        (
            {
                "display": "full",
                "date": "2023-01-01",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "updated_since": 1,
                "published_since": 1,
                "sort": "created",
                "order": "desc",
                "isin": "US0378331005",
                "cusip": "037833100",
                "channels": "General",
                "topics": "AAPL",
                "authors": "Benzinga Insights",
                "content_types": "headline",
                "provider": "benzinga",
                "symbols": "AAPL,MSFT",
                "limit": 20,
            }
        ),
        (
            {
                "published_utc": "2023-01-01",
                "order": "desc",
                "provider": "polygon",
                "symbols": "AAPL",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "fmp",
                "symbols": "AAPL",
                "limit": 20,
                "page": 1,
            }
        ),
        (
            {
                "provider": "yfinance",
                "symbols": "AAPL",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbols": "AAPL",
                "limit": 20,
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_news(params, obb):
    result = obb.stocks.news(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 100}),
    ],
)
@pytest.mark.integration
def test_stocks_multiples(params, obb):
    result = obb.stocks.multiples(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "AAPL", "is_symbol": True}),
    ],
)
@pytest.mark.integration
def test_stocks_search(params, obb):
    result = obb.stocks.search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"source": "iex", "provider": "intrinio", "symbol": "AAPL"}),
        ({"symbol": "AAPL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_stocks_quote(params, obb):
    result = obb.stocks.quote(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_info(params, obb):
    result = obb.stocks.info(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
