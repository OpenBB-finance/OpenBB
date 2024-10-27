"""Test crypto API endpoints."""

import base64

import pytest
import requests
from extensions.tests.conftest import parametrize
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def headers():
    """Get the headers for the API request."""
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


@parametrize(
    "params",
    [
        ({"query": "asd"}),
        ({"query": "btc", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_crypto_search(params, headers):
    """Test the crypto search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


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
def test_crypto_price_historical(params, headers):
    """Test the crypto historical price endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/price/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "provider": "defillama",
            "chain": "ethereum",
            "timestamp": "2024-01-01",
        },
        {
            "provider": "defillama",
            "chain": "ethereum",
            "timestamp": "2024-01-01T12:12:12",
        },
        {
            "provider": "defillama",
            "chain": "ethereum",
            "timestamp": "1729957601",
        },
        {
            "provider": "defillama",
            "chain": "ethereum",
            "timestamp": 1729957601,
        },
    ],
)
@pytest.mark.integration
def test_crypto_coins_block(params, headers):
    """Test the coins block timestamp endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/coins/block?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "search_width": "1D",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "search_width": "4H",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "search_width": "4m",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "search_width": "1W",
        },
    ],
)
@pytest.mark.integration
def test_crypto_coins_current(params, headers):
    """Test the coins current price endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/coins/current?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
        },
    ],
)
@pytest.mark.integration
def test_crypto_coins_first(params, headers):
    """Test the coins first record endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/coins/first?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "timestamp": "2024-01-01",
            "look_forward": False,
            "period": "24h",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "timestamp": "2024-01-01T12:12:12",
            "look_forward": False,
            "period": "1W",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "timestamp": "1729957601",
            "look_forward": True,
            "period": "7D",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "timestamp": 1729957601,
            "look_forward": True,
            "period": "24m",
        },
    ],
)
@pytest.mark.integration
def test_crypto_coins_change(params, headers):
    """Test the coins change endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/coins/change?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "start_date": "2024-09-01",
            "end_date": None,
            "span": 0,
            "period": "24h",
            "search_width": "2h",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "start_date": None,
            "end_date": "2024-10-01",
            "span": 0,
            "period": "24h",
            "search_width": "2h",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "start_date": 1725129000,
            "end_date": None,
            "span": 10,
            "period": "24h",
            "search_width": "2h",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "start_date": 1725129000,
            "end_date": None,
            "span": 100,
            "period": "1D",
            "search_width": "8h",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "start_date": None,
            "end_date": 1727721000,
            "span": 10,
            "period": "1W",
            "search_width": "1D",
        },
    ],
)
@pytest.mark.integration
def test_crypto_coins_chart(params, headers):
    """Test the coins chart endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/coins/chart?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "timestamp": "2024-01-01",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "timestamp": "2024-01-01T12:12:12",
            "search_width": "1W",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "timestamp": "1729957601",
            "search_width": "7D",
        },
        {
            "provider": "defillama",
            "token": "coingecko:ethereum",
            "timestamp": 1729957601,
            "search_width": "4m",
        },
    ],
)
@pytest.mark.integration
def test_crypto_coins_historical(params, headers):
    """Test the coins historical price endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/coins/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama"},
        {"provider": "defillama", "chain": None, "all": True},
        {"provider": "defillama", "chain": "ethereum", "all": False},
        {"provider": "defillama", "chain": "ethereum", "all": True},
    ],
)
@pytest.mark.integration
def test_crypto_fees_overview(params, headers):
    """Test the fees overview endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/fees/overview?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama", "protocol": "litecoin"},
    ],
)
@pytest.mark.integration
def test_crypto_fees_summary(params, headers):
    """Test the fees summary endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/fees/summary?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama"},
        {"provider": "defillama", "chain": None, "all": True},
        {"provider": "defillama", "chain": "ethereum", "all": False},
        {"provider": "defillama", "chain": "ethereum", "all": True},
    ],
)
@pytest.mark.integration
def test_crypto_revenue_overview(params, headers):
    """Test the revenue overview endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/revenue/overview?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama", "protocol": "litecoin"},
    ],
)
@pytest.mark.integration
def test_crypto_revenue_summary(params, headers):
    """Test the revenue summary endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/revenue/summary?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama"},
        {"provider": "defillama", "include_prices": True},
    ],
)
@pytest.mark.integration
def test_crypto_stablecoins_list(params, headers):
    """Test the stablecoins list endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/stablecoins/list?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama"},
    ],
)
@pytest.mark.integration
def test_crypto_stablecoins_current(params, headers):
    """Test the stablecoins current endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/stablecoins/current?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama"},
    ],
)
@pytest.mark.integration
def test_crypto_stablecoins_historical(params, headers):
    """Test the stablecoins historical endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/stablecoins/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama", "stablecoin": "1"},
    ],
)
@pytest.mark.integration
def test_crypto_stablecoins_distribution(params, headers):
    """Test the stablecoins distribution endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/stablecoins/distribution?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama"},
        {"provider": "defillama", "stablecoin": "1", "chain": None},
        {"provider": "defillama", "stablecoin": None, "chain": "ethereum"},
        {"provider": "defillama", "stablecoin": "1", "chain": "ethereum"},
    ],
)
@pytest.mark.integration
def test_crypto_stablecoins_charts(params, headers):
    """Test the stablecoins charts endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/stablecoins/charts?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama"},
    ],
)
@pytest.mark.integration
def test_crypto_tvl_chains(params, headers):
    """Test the TVL chains endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/tvl/chains?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama"},
        {"provider": "defillama", "symbol": "uniswap", "symbol_type": "protocol"},
        {"provider": "defillama", "symbol": None, "symbol_type": "chain"},
        {"provider": "defillama", "symbol": "ethereum", "symbol_type": "chain"},
    ],
)
@pytest.mark.integration
def test_crypto_tvl_historical(params, headers):
    """Test the TVL historical endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/tvl/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama", "symbol": "uniswap"},
    ],
)
@pytest.mark.integration
def test_crypto_tvl_current(params, headers):
    """Test the TVL current endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/tvl/current?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama"},
        {"provider": "defillama", "chain": None, "is_options": False, "all": True, "volume_type": "premium"},
        {"provider": "defillama", "chain": None, "is_options": True, "all": False, "volume_type": "premium"},
        {"provider": "defillama", "chain": "ethereum", "is_options": False, "all": False, "volume_type": "premium"},
        {"provider": "defillama", "chain": "ethereum", "is_options": True, "all": False, "volume_type": "premium"},
        {
            "provider": "defillama",
            "chain": "ethereum",
            "is_options": True,
            "all": False,
            "volume_type": "notional",
        },
    ],
)
@pytest.mark.integration
def test_crypto_volumes_overview(params, headers):
    """Test the volumes overview endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/volumes/overview?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama", "protocol": "uniswap", "is_options": False, "volume_type": "premium"},
        {
            "provider": "defillama",
            "protocol": "pancakeswap-options",
            "is_options": True,
            "volume_type": "premium",
        },
        {"provider": "defillama", "protocol": "uniswap", "is_options": False, "volume_type": "notional"},
    ],
)
@pytest.mark.integration
def test_crypto_volumes_summary(params, headers):
    """Test the volumes summary endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/volumes/summary?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {"provider": "defillama"},
    ],
)
@pytest.mark.integration
def test_crypto_yields_pools(params, headers):
    """Test the yields pools endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/yields/pools?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        {
            "provider": "defillama",
            "pool_id": "747c1d2a-c668-4682-b9f9-296708a3dd90",
        },
    ],
)
@pytest.mark.integration
def test_crypto_yields_historical(params, headers):
    """Test the yields historical endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/crypto/yields/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)

    assert isinstance(result, requests.Response)
    assert result.status_code == 200
