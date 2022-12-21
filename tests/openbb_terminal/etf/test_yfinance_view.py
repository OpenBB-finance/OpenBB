# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.etf import yfinance_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
        ],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "name",
    ["ARKW", "ARKF"],
)
def test_display_etf_weightings(name, mocker):
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")
    yfinance_view.display_etf_weightings(
        name, raw=True, min_pct_to_display=5, export=""
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "name",
    ["ARKW", "ARKF"],
)
def test_display_etf_description(name, mocker):
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")
    yfinance_view.display_etf_description(name)
