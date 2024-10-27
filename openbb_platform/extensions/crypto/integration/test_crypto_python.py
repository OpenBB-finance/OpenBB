"""Test crypto extension."""

import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


@parametrize(
    "params",
    [
        ({"query": "asd"}),
        ({"query": "btc", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_crypto_search(params, obb):
    """Test the crypto search endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.crypto.search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "interval": "1d",
                "provider": "fmp",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
            }
        ),
        (
            {
                "interval": "1h",
                "provider": "fmp",
                "symbol": "BTCUSD,ETHUSD",
                "start_date": None,
                "end_date": None,
            }
        ),
        (
            {
                "interval": "1m",
                "sort": "desc",
                "limit": 49999,
                "provider": "polygon",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
            }
        ),
        (
            {
                "interval": "1d",
                "sort": "desc",
                "limit": 49999,
                "provider": "polygon",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "interval": "1d",
                "provider": "yfinance",
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-04",
            }
        ),
        (
            {
                "provider": "tiingo",
                "interval": "1d",
                "exchanges": None,
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "provider": "tiingo",
                "interval": "1h",
                "exchanges": ["POLONIEX", "GDAX"],
                "symbol": "BTCUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
            }
        ),
    ],
)
@pytest.mark.integration
def test_crypto_price_historical(params, obb):
    """Test crypto price historical."""
    result = obb.crypto.price.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama"}),
        ({"provider": "defillama", "all": True}),
        ({"provider": "defillama", "chain": "ethereum"}),
        ({"provider": "defillama", "chain": "ethereum", "all": True}),
    ],
)
@pytest.mark.integration
def test_fees_overview(params, obb):
    """Test fees overview endpoint."""
    result = obb.crypto.fees.overview(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama", "protocol": "litecoin"}),
    ],
)
@pytest.mark.integration
def test_fees_summary(params, obb):
    """Test fees summary endpoint."""
    result = obb.crypto.fees.summary(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama"}),
    ],
)
@pytest.mark.integration
def test_tvl_chains(params, obb):
    """Test TVL chains endpoint."""
    result = obb.crypto.tvl.chains(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama"}),
        ({"provider": "defillama", "symbol": "uniswap"}),
        ({"provider": "defillama", "symbol_type": "chain"}),
        ({"provider": "defillama", "symbol": "ethereum", "symbol_type": "chain"}),
    ],
)
@pytest.mark.integration
def test_tvl_historical(params, obb):
    """Test TVL historical endpoint."""
    result = obb.crypto.tvl.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama", "symbol": "uniswap"}),
    ],
)
@pytest.mark.integration
def test_tvl_current(params, obb):
    """Test TVL current endpoint."""
    result = obb.crypto.tvl.current(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama"}),
    ],
)
@pytest.mark.integration
def test_yields_pools(params, obb):
    """Test yields pools endpoint."""
    result = obb.crypto.yields.pools(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "defillama",
                "pool_id": "747c1d2a-c668-4682-b9f9-296708a3dd90",
            }
        ),
    ],
)
@pytest.mark.integration
def test_yields_historical(params, obb):
    """Test yields historical endpoint."""
    result = obb.crypto.yields.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama"}),
        ({"provider": "defillama", "include_prices": True}),
    ],
)
@pytest.mark.integration
def test_stablecoins_list(params, obb):
    """Test stablecoins list endpoint."""
    result = obb.crypto.stablecoins.list(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama"}),
    ],
)
@pytest.mark.integration
def test_stablecoins_current(params, obb):
    """Test stablecoins current endpoint."""
    result = obb.crypto.stablecoins.current(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama"}),
    ],
)
@pytest.mark.integration
def test_stablecoins_historical(params, obb):
    """Test stablecoins historical endpoint."""
    result = obb.crypto.stablecoins.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama", "stablecoin": "1"}),
    ],
)
@pytest.mark.integration
def test_stablecoins_distribution(params, obb):
    """Test stablecoins distribution endpoint."""
    result = obb.crypto.stablecoins.distribution(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama"}),
        ({"provider": "defillama", "stablecoin": "1"}),
        ({"provider": "defillama", "chain": "ethereum"}),
        ({"provider": "defillama", "stablecoin": "1", "chain": "ethereum"}),
    ],
)
@pytest.mark.integration
def test_stablecoins_charts(params, obb):
    """Test stablecoins charts endpoint."""
    result = obb.crypto.stablecoins.charts(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "search_width": "1D",
            }
        ),
        (
            {
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "search_width": "4H",
            }
        ),
        (
            {
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "search_width": "4m",
            }
        ),
        (
            {
                "provider": "defillama",
                "token": "coingecko:ethereum",
                "search_width": "1W",
            }
        ),
    ],
)
@pytest.mark.integration
def test_coins_current(params, obb):
    """Test coins current endpoint."""
    result = obb.crypto.coins.current(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama"}),
        ({"provider": "defillama", "all": True}),
        ({"provider": "defillama", "is_options": True}),
        ({"provider": "defillama", "chain": "ethereum"}),
        ({"provider": "defillama", "chain": "ethereum", "is_options": True}),
        (
            {
                "provider": "defillama",
                "chain": "ethereum",
                "is_options": True,
                "volume_type": "notional",
            }
        ),
    ],
)
@pytest.mark.integration
def test_volumes_overview(params, obb):
    """Test volumes overview endpoint."""
    result = obb.crypto.volumes.overview(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama", "protocol": "litecoin"}),
        (
            {
                "provider": "defillama",
                "protocol": "pancakeswap-options",
                "is_options": True,
            }
        ),
        ({"provider": "defillama", "protocol": "uniswap", "volume_type": "notional"}),
    ],
)
@pytest.mark.integration
def test_volumes_summary(params, obb):
    """Test volumes summary endpoint."""
    result = obb.crypto.volumes.summary(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama"}),
        ({"provider": "defillama", "all": True}),
        ({"provider": "defillama", "chain": "ethereum"}),
        ({"provider": "defillama", "chain": "ethereum", "all": True}),
    ],
)
@pytest.mark.integration
def test_revenue_overview(params, obb):
    """Test revenue overview endpoint."""
    result = obb.crypto.revenue.overview(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"provider": "defillama", "protocol": "litecoin"}),
    ],
)
@pytest.mark.integration
def test_revenue_summary(params, obb):
    """Test revenue summary endpoint."""
    result = obb.crypto.revenue.summary(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
