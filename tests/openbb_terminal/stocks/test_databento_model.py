import pytest

from openbb_terminal.stocks import databento_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("Authorization", "MOCK_AUTHORIZATION"),
        ],
    }


def test_databento_model():
    """Tests the DataBento model."""
    model = databento_model.DataBento(
        symbol="AAPL", start="2021-08-10", end="2021-08-11"
    )
    assert model.symbol == "AAPL"
    assert model.exchange == "XNAS.ITCH"
    assert model.stype == "raw_symbol"
    assert model.start == "2021-08-10"
    assert model.end == "2021-08-11"


@pytest.mark.vcr
def test_stock_load(recorder):
    """Tests the stock load function."""
    result = databento_model.get_historical_stock(
        symbol="AAPL", start_date="2022-08-01", end_date="2022-10-01"
    )
    assert result.empty is False
    recorder.capture(result)
