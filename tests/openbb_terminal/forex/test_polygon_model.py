import pytest

# IMPORTATION INTERNAL
from openbb_terminal.forex import polygon_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("apiKey", "MOCK_API_KEY"),
        ]
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "fx_pair",
    [("EURUSD"), ("USDEUR")],
)
def test_get_historical(fx_pair, recorder):
    result = polygon_model.get_historical(fx_pair)
    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_bad_symbols():
    polygon_model.get_historical("GCUYGCYUFGDCUTYFCYUF")
