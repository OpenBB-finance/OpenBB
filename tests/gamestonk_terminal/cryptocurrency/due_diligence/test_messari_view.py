# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.due_diligence import messari_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("x-messari-api-key", "mock_x-messari-api-key")],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
def test_display_marketcap_dominance(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.due_diligence.messari_view.export_data"
    )

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    messari_view.display_marketcap_dominance(
        coin="BTC", start="2022-01-10", end="2022-03-08", interval="1d"
    )
