import pytest

from openbb_terminal.cryptocurrency.overview import blockchaincenter_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_altcoin_index(mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")
    blockchaincenter_view.get_altcoin_index(365, "2010-01-01", "2022-11-10")
