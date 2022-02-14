# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import smartstake_view


@pytest.mark.vcr()
@pytest.mark.record_stdout
def test_display_luna_circ_supply_change(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="gamestonk_terminal.cryptocurrency.defi.smartstake_view.export_data"
    )

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    smartstake_view.display_luna_circ_supply_change(days=30, export="")
