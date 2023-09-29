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
                "year": 2023,
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "company_name": "Apple Inc",
                "company_name_search": "AAPL",
                "sic": "35719904",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "provider": "polygon",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_fa_balance(params):
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
def test_stocks_fa_balance_growth(params):
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
def test_stocks_fa_cal(params):
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
                "year": 2023,
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "company_name": "Apple Inc",
                "company_name_search": "AAPL",
                "sic": "35719904",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "provider": "polygon",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_fa_cash(params):
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
def test_stocks_fa_cash_growth(params):
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
def test_stocks_fa_comp(params):
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
def test_stocks_fa_comsplit(params):
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
def test_stocks_fa_divs(params):
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
def test_stocks_fa_earning(params):
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
def test_stocks_fa_emp(params):
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
def test_stocks_fa_est(params):
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
                "year": 2023,
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "company_name": "Apple Inc",
                "company_name_search": "AAPL",
                "sic": "35719904",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "provider": "polygon",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_fa_income(params):
    result = obb.stocks.fa.income(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 10, "period": "annual"}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_income_growth(params):
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
def test_stocks_fa_ins(params):
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
                "date": "2023-01-01",
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_fa_ins_own(params):
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
def test_stocks_fa_metrics(params):
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
def test_stocks_fa_mgmt(params):
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
def test_stocks_fa_overview(params):
    result = obb.stocks.fa.overview(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "date": "2023-01-01", "page": 1}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_own(params):
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
def test_stocks_fa_pt(params):
    result = obb.stocks.fa.pt(**params)
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
@pytest.mark.integration
def test_stocks_fa_pta(params):
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
def test_stocks_fa_ratios(params):
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
def test_stocks_fa_revgeo(params):
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
def test_stocks_fa_revseg(params):
    result = obb.stocks.fa.revseg(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "type": "1", "page": 1, "limit": 100}),
    ],
)
@pytest.mark.integration
def test_stocks_fa_sec(params):
    result = obb.stocks.fa.sec(**params)
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
def test_stocks_fa_shrs(params):
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
def test_stocks_fa_split(params):
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
def test_stocks_fa_transcript(params):
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
def test_stocks_ca_peers(params):
    result = obb.stocks.ca.peers(**params)
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
@pytest.mark.integration
def test_stocks_options_chains(params):
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
            }
        ),
        (
            {
                "period": "daily",
                "interval": "60min",
                "adjusted": True,
                "extended_hours": True,
                "month": "2023-03",
                "outputsize": "full",
                "provider": "alpha_vantage",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1m",
                "provider": "cboe",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
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
                "interval": "1min",
                "provider": "fmp",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
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
                "interval_size": "30m",
                "provider": "intrinio",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
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
                "end_date": "2023-01-02",
            }
        ),
        (
            {
                "multiplier": 1,
                "timespan": "minute",
                "sort": "desc",
                "limit": 49999,
                "adjusted": True,
                "provider": "polygon",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
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
                "interval": "1m",
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
                "end_date": "2023-01-02",
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
@pytest.mark.integration
def test_stocks_load(params):
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
    ],
)
@pytest.mark.integration
def test_stocks_news(params):
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
def test_stocks_multiples(params):
    result = obb.stocks.multiples(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "AAPL", "ticker": True}),
    ],
)
@pytest.mark.integration
def test_stocks_search(params):
    result = obb.stocks.search(**params)
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
@pytest.mark.integration
def test_stocks_quote(params):
    result = obb.stocks.quote(**params)
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
def test_stocks_info(params):
    result = obb.stocks.info(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
