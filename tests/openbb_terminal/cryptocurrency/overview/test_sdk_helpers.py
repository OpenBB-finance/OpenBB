import pytest
from pandas import DataFrame

from openbb_terminal.cryptocurrency.overview import sdk_helpers


@pytest.mark.record_http
@pytest.mark.parametrize(
    "source",
    [
        "CoinGecko",
        "CoinPaprika",
    ],
)
def test_globe(source):
    df = sdk_helpers.globe(source=source)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "source",
    [
        "CoinGecko",
        # "CoinPaprika",
    ],
)
def test_exchanges(source):
    df = sdk_helpers.exchanges(source=source)

    assert isinstance(df, DataFrame)
    assert not df.empty
