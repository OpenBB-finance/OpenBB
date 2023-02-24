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
def test_display_etf_weightings(name, mocker):
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")
    fmp_view.display_etf_weightings(name, raw=True, export="")
