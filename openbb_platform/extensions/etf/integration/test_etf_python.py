"""Test etf extension."""
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


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "IOO",
                "date": "2023-01-01",
                "cik": None,
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "SPY",
                "date": "2023-04-20",
                "cik": None,
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "MISL",
                "date": "2023-04-20",
                "cik": "0001329377",
                "provider": "fmp",
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


@pytest.mark.parametrize(
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


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_disc_gainers(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.gainers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_disc_losers(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.losers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_etf_holdings_date(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.etf.holdings_date(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "limit": 10})],
)
@pytest.mark.integration
def test_etf_disc_active(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.disc.active(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
