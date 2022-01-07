import pytest

from gamestonk_terminal.cryptocurrency.overview import blockchaincenter_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_altcoin_index():
    blockchaincenter_view.get_altcoin_index(365, 1_601_596_800, 1_641_573_787)
