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
