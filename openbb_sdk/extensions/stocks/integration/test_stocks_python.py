"""Test stocks extension."""
import pytest
from openbb import obb
from openbb_core.app.model.obbject import OBBject


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12}),
        (
            {
                "type": "reported",
                "year": 1,
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "company_name": "TEST_STRING",
                "company_name_search": "TEST_STRING",
                "sic": "TEST_STRING",
                "include_sources": True,
                "provider": "polygon",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
    ],
)
def test_stocks_fa_balance(params):
    result = obb.stocks.fa.balance(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 10}),
    ],
)
def test_stocks_fa_balance_growth(params):
    result = obb.stocks.fa.balance_growth(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
    ],
)
def test_stocks_fa_cal(params):
    result = obb.stocks.fa.cal(params)
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
                "year": 1,
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "company_name": "TEST_STRING",
                "company_name_search": "TEST_STRING",
                "sic": "TEST_STRING",
                "include_sources": True,
                "provider": "polygon",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
    ],
)
def test_stocks_fa_cash(params):
    result = obb.stocks.fa.cash(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 10}),
    ],
)
def test_stocks_fa_cash_growth(params):
    result = obb.stocks.fa.cash_growth(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_fa_comp(params):
    result = obb.stocks.fa.comp(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
    ],
)
def test_stocks_fa_comsplit(params):
    result = obb.stocks.fa.comsplit(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_fa_divs(params):
    result = obb.stocks.fa.divs(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 50}),
    ],
)
def test_stocks_fa_earning(params):
    result = obb.stocks.fa.earning(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_fa_emp(params):
    result = obb.stocks.fa.emp(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 30}),
    ],
)
def test_stocks_fa_est(params):
    result = obb.stocks.fa.est(params)
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
                "year": 1,
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "company_name": "TEST_STRING",
                "company_name_search": "TEST_STRING",
                "sic": "TEST_STRING",
                "include_sources": True,
                "provider": "polygon",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
    ],
)
def test_stocks_fa_income(params):
    result = obb.stocks.fa.income(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 10, "period": "annual"}),
    ],
)
def test_stocks_fa_income_growth(params):
    result = obb.stocks.fa.income_growth(params)
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
def test_stocks_fa_ins(params):
    result = obb.stocks.fa.ins(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "include_current_quarter": True, "date": "2023-01-01"}),
    ],
)
def test_stocks_fa_ins_own(params):
    result = obb.stocks.fa.ins_own(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 100}),
    ],
)
def test_stocks_fa_metrics(params):
    result = obb.stocks.fa.metrics(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_fa_mgmt(params):
    result = obb.stocks.fa.mgmt(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_fa_overview(params):
    result = obb.stocks.fa.overview(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "date": "2023-01-01", "page": 1}),
    ],
)
def test_stocks_fa_own(params):
    result = obb.stocks.fa.own(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_fa_pt(params):
    result = obb.stocks.fa.pt(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"with_grade": True, "provider": "fmp", "symbol": "AAPL"}),
    ],
)
def test_stocks_fa_pta(params):
    result = obb.stocks.fa.pta(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12}),
    ],
)
def test_stocks_fa_ratios(params):
    result = obb.stocks.fa.ratios(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "structure": "flat"}),
    ],
)
def test_stocks_fa_revgeo(params):
    result = obb.stocks.fa.revgeo(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "structure": "flat"}),
    ],
)
def test_stocks_fa_revseg(params):
    result = obb.stocks.fa.revseg(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "page": 1, "limit": 100}),
    ],
)
def test_stocks_fa_sec(params):
    result = obb.stocks.fa.sec(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_fa_shrs(params):
    result = obb.stocks.fa.shrs(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_fa_split(params):
    result = obb.stocks.fa.split(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "year": 1, "quarter": 1}),
    ],
)
def test_stocks_fa_transcript(params):
    result = obb.stocks.fa.transcript(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_ca_peers(params):
    result = obb.stocks.ca.peers(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"date": "2023-01-01", "provider": "intrinio", "symbol": "AAPL"}),
    ],
)
def test_stocks_options_chains(params):
    result = obb.stocks.options.chains(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "period": "daily",
                "interval": "60min",
                "adjusted": True,
                "extended_hours": True,
                "month": "TEST_STRING",
                "outputsize": "full",
                "provider": "alpha_vantage",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "provider": "cboe",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1day",
                "provider": "fmp",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "timezone": "UTC",
                "source": "realtime",
                "interval_size": "60m",
                "provider": "intrinio",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "multiplier": 1,
                "timespan": "day",
                "sort": "desc",
                "limit": 49999,
                "adjusted": True,
                "provider": "polygon",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "period": "max",
                "prepost": True,
                "actions": True,
                "auto_adjust": True,
                "back_adjust": True,
                "progress": True,
                "ignore_tz": True,
                "rounding": True,
                "repair": True,
                "keepna": True,
                "group_by": "column",
                "provider": "yfinance",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
def test_stocks_load(params):
    result = obb.stocks.load(params)
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
                "isin": "TEST_STRING",
                "cusip": "TEST_STRING",
                "channels": "TEST_STRING",
                "topics": "TEST_STRING",
                "authors": "TEST_STRING",
                "content_types": "TEST_STRING",
                "provider": "benzinga",
                "symbols": "AAPL,MSFT",
                "limit": 20,
            }
        ),
        (
            {
                "published_utc": "TEST_STRING",
                "order": "desc",
                "provider": "polygon",
                "symbols": "AAPL,MSFT",
                "limit": 20,
            }
        ),
    ],
)
def test_stocks_news(params):
    result = obb.stocks.news(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 100}),
    ],
)
def test_stocks_multiples(params):
    result = obb.stocks.multiples(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "TEST_STRING", "ticker": True}),
    ],
)
def test_stocks_search(params):
    result = obb.stocks.search(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"source": "iex", "provider": "intrinio", "symbol": "AAPL"}),
    ],
)
def test_stocks_quote(params):
    result = obb.stocks.quote(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_info(params):
    result = obb.stocks.info(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
