import pytest

from bots.economy.overview import overview_command


@pytest.mark.vcr
def test_overview_command(mocker, recorder):
    mocker.patch(target="bots.economy.overview.imps.save_image", return_value=None)
    value = overview_command()

    recorder.capture(value)
