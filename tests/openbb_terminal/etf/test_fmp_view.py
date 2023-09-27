# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.etf import fmp_view


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
    ["VTI"],
)
def test_display_etf_weightings(name):
    fmp_view.display_etf_weightings(name, raw=True, export="")


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
def test_view_etf_holdings_performance(ticker, start_date, end_date):
    fmp_view.view_etf_holdings_performance(
        ticker, start_date, end_date, raw=True, export=""
    )
