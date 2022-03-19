# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import alphavantage_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("apikey", "MOCK_API_KEY")],
    }


@pytest.mark.default_cassette("test_realtime_performance_sector")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "raw",
    [True, True, False],
)
@pytest.mark.record_stdout
def test_realtime_performance_sector(mocker, raw):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.economy.alphavantage_view.export_data")

    alphavantage_view.realtime_performance_sector(
        raw=raw,
        export="",
    )
