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
    "fx_pair,from_date,to_date",
    [
        ("EURUSD", "2022-02-20", "2022-03-15"),
        ("USDEUR", "2022-02-20", "2022-03-15"),
    ],
)
def test_get_historical(fx_pair, from_date, to_date, recorder):
    result = polygon_model.get_historical(
        fx_pair=fx_pair, from_date=from_date, to_date=to_date
    )
    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "fx_pair,from_date,to_date",
    [
        ("BADTICKER", "2022-02-20", "2022-03-15"),
    ],
)
@pytest.mark.record_stdout
def test_bad_symbols(fx_pair, from_date, to_date):
    polygon_model.get_historical(fx_pair=fx_pair, from_date=from_date, to_date=to_date)
