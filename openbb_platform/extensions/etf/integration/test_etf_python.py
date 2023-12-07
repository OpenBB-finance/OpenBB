"""Test etf extension."""
import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


# pylint: disable=redefined-outer-name


@parametrize(
    "params",
    [
        ({"query": None, "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_search(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "IOO",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "yfinance",
            }
        ),
        (
            {
                "symbol": "MISL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "provider": "yfinance",
            }
        ),
    ],
)
@pytest.mark.integration
def test_etf_historical(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "IOO", "provider": "fmp"}),
        ({"symbol": "MISL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_info(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.info(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "IOO", "provider": "fmp"}),
        ({"symbol": "MISL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_sectors(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.sectors(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "QQQ", "cik": None, "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_holdings_date(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.holdings_date(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "symbol": "IOO",
                "date": "2023-03-31",
                "cik": None,
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "SILJ",
                "date": "2019-12-31",
                "cik": None,
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "TQQQ",
                "date": None,
                "provider": "sec",
                "use_cache": False,
            }
        ),
        (
            {
                "symbol": "QQQ",
                "date": "2021-06-30",
                "provider": "sec",
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_etf_holdings(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.holdings(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"symbol": "SPY,VOO,QQQ,IWM,IWN,GOVT,JNK", "provider": "fmp"})],
)
@pytest.mark.integration
def test_etf_price_performance(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.price_performance(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"symbol": "IOO"})],
)
@pytest.mark.integration
def test_etf_countries(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.countries(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_discovery_gainers(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.discovery.gainers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_discovery_losers(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.discovery.losers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_discovery_active(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.discovery.active(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"symbol": "SPY", "provider": "fmp"}),
        ({"symbol": "QQQ", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_etf_holdings_performance(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.holdings_performance(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_discovery_gainers2(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.discovery.gainers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_discovery_losers2(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.discovery.losers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_discovery_active2(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.discovery.active(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
