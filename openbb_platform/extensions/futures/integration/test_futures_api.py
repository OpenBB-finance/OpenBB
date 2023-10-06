import base64

import pytest
import requests
from openbb_core.env import Env
from openbb_provider.utils.helpers import get_querystring


@pytest.fixture(scope="session")
def headers():
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "ES",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "expiration": "2024-06",
            }
        ),
        (
            {
                "interval": "1d",
                "period": "1d",
                "prepost": True,
                "adjust": True,
                "back_adjust": True,
                "provider": "yfinance",
                "symbol": "ES",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "expiration": "2024-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_futures_load(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/futures/load?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "date": "2023-01-01"}),
        ({"provider": "cboe", "symbol": "AAPL", "date": "2023-01-01"}),
        ({"provider": "yfinance", "symbol": "AAPL", "date": "2023-01-01"}),
    ],
)
@pytest.mark.integration
def test_futures_curve(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/futures/curve?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
