"""Test economy extension."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


# pylint: disable=redefined-outer-name


@pytest.mark.parametrize(
    "params",
    [
        ({"index": "dowjones"}),
    ],
)
@pytest.mark.integration
def test_economy_const(params, obb):
    result = obb.economy.const(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "countries": ["portugal", "spain"],
                "units": "growth_same",
                "frequency": "monthly",
                "harmonized": True,
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_cpi(params, obb):
    result = obb.economy.cpi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAVE100",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1m",
                "provider": "cboe",
                "symbol": "AAVE100",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "provider": "cboe",
                "symbol": "AAVE100",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1min",
                "provider": "fmp",
                "symbol": "^DJI",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "timeseries": 1,
            }
        ),
        (
            {
                "interval": "1day",
                "provider": "fmp",
                "symbol": "^DJI",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "timeseries": 1,
            }
        ),
        (
            {
                "timespan": "minute",
                "sort": "desc",
                "limit": 49999,
                "adjusted": True,
                "multiplier": 1,
                "provider": "polygon",
                "symbol": "NDX",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "timespan": "day",
                "sort": "desc",
                "limit": 49999,
                "adjusted": True,
                "multiplier": 1,
                "provider": "polygon",
                "symbol": "NDX",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "period": "max",
                "prepost": True,
                "rounding": True,
                "provider": "yfinance",
                "symbol": "DJI",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_index(params, obb):
    result = obb.economy.index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "BUKBUS",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1m",
                "provider": "cboe",
                "symbol": "BUKBUS",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "provider": "cboe",
                "symbol": "BUKBUS",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_european_index(params, obb):
    result = obb.economy.european_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "BUKBUS"}),
    ],
)
@pytest.mark.integration
def test_economy_european_index_constituents(params, obb):
    result = obb.economy.european_index_constituents(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({}),
        ({"europe": True, "provider": "cboe"}),
        ({"provider": "fmp"}),
        ({"provider": "yfinance"}),
    ],
)
@pytest.mark.integration
def test_economy_available_indices(params, obb):
    result = obb.economy.available_indices(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({}),
    ],
)
@pytest.mark.integration
def test_economy_risk(params, obb):
    result = obb.economy.risk(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "D", "is_symbol": True}),
        ({"europe": True, "provider": "cboe", "query": "A", "is_symbol": False}),
    ],
)
@pytest.mark.integration
def test_economy_index_search(params, obb):
    result = obb.economy.index_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"region": "US"}),
    ],
)
@pytest.mark.integration
def test_economy_index_snapshots(params, obb):
    result = obb.economy.index_snapshots(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "grain"}),
    ],
)
@pytest.mark.integration
def test_economy_cot_search(params, obb):
    result = obb.economy.cot_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({}),
        (
            {
                "code": "13874P",
                "data_type": "FO",
                "legacy_format": True,
                "report_type": "ALL",
                "measure": "CR",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "transform": "diff",
                "provider": "quandl",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_cot(params, obb):
    result = obb.economy.cot(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "series_name": "PE Ratio by Month",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "collapse": "monthly",
                "transform": "diff",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_sp500_multiples(params, obb):
    result = obb.economy.sp500_multiples(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "$GDP",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "limit": 100,
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_fred_index(params, obb):
    result = obb.economy.fred_index(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"units": "usd", "start_date": "2021-01-01", "end_date": "2023-06-06"}),
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "units": "usd",
                "start_date": "2021-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_gdpnom(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.gdpnom(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"units": "yoy", "start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "units": "yoy",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_gdpreal(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.gdpreal(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "period": "annual",
                "start_date": "2023-01-01",
                "end_date": "2025-06-06",
                "type": "real",
            }
        ),
        (
            {
                "country": "united_states",
                "provider": "oecd",
                "period": "annual",
                "start_date": "2023-01-01",
                "end_date": "2025-06-06",
                "type": "real",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_gdpforecast(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.gdpforecast(**params)
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
                "country": "mexico,sweden",
            }
        ),
        (
            {
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_economy_econcal(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.economy.econcal(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
