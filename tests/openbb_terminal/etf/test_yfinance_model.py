# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.etf import yfinance_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "name",
    [
        "ARKW",
        "ARKK",
    ],
)
def test_get_etfs_by_name(recorder, name):
    result = yfinance_model.get_etf_sector_weightings(name)

    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "name",
    [
        "ARKW",
        "ARKK",
    ],
)
def test_get_etf_summary_description(recorder, name):
    result = yfinance_model.get_etf_summary_description(name)

    recorder.capture(result)
