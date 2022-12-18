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
    "fx_pair,start_date,end_date",
    [
        ("EURUSD", "2022-02-20", "2022-03-15"),
        ("USDEUR", "2022-02-20", "2022-03-15"),
    ],
)
def test_get_historical(fx_pair, start_date, end_date, recorder):
    result = polygon_model.get_historical(
        fx_pair=fx_pair, start_date=start_date, end_date=end_date
    )
    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "fx_pair,start_date,end_date",
    [
        ("BADTICKER", "2022-02-20", "2022-03-15"),
    ],
)
@pytest.mark.record_stdout
def test_bad_symbols(fx_pair, start_date, end_date):
    polygon_model.get_historical(
        fx_pair=fx_pair, start_date=start_date, end_date=end_date
    )
