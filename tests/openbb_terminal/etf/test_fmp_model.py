# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.etf import fmp_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "name",
    [
        "VTI",
    ],
)
def test_get_etf_sector_weightings(recorder, name):
    result = fmp_model.get_etf_sector_weightings(name)

    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "ticker",
    [
        "ARKK",
    ],
)
def test_get_etf_holdings(recorder, ticker):
    result = fmp_model.get_etf_holdings(ticker)

    assert result.count != 0
    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "ticker",
    [
        "TSLA",
    ],
)
@pytest.mark.parametrize(
    "start_date",
    [
        "2022-09-01",
    ],
)
@pytest.mark.parametrize(
    "end_date",
    [
        "2023-09-01",
    ],
)
def test_get_stock_price_change(recorder, ticker: str, start_date: str, end_date: str):
    result = fmp_model.get_holdings_pct_change(ticker, start_date, end_date)

    recorder.capture(result)
