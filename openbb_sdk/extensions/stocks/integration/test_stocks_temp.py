import pytest
import uvicorn
from openbb import obb
from openbb_core.app.model.obbject import OBBject


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "fmp"}),
        ({"symbol": "AAPL", "provider": "yfinance"}),
        ({"symbol": "AAPL", "provider": "polygon"}),
    ],
)
def test_stocks_load(params):
    """Test load."""
    data = obb.stocks.load(params)
    assert data
    assert isinstance(data, OBBject)
    assert len(data.results) > 0


# we need to launch the api -> done on the script that collects every integration test

uvicorn.run("openbb_core.api.rest_api:app", reload=True, port=8086)

# get fastapi.json for parsing
# curl http://localhost:8086/openbb/fastapi.json > fastapi.json
# get it with python
# import requests
# r = requests.get('http://localhost:8086/openbb/fastapi.json')


def test_api_stocks_load(params):
    pass
