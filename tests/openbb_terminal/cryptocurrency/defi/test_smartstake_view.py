# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.defi import smartstake_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
            ("key", "MOCK_API_KEY"),
        ]
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
def test_display_luna_circ_supply_change(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.cryptocurrency.defi.smartstake_view.export_data"
    )

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    smartstake_view.display_luna_circ_supply_change(days=30, export="")
