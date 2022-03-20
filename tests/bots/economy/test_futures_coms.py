import pytest

from bots.economy.futures_coms import futures_coms_command


@pytest.mark.vcr
def test_futures_coms_command(mocker, recorder):
    mocker.patch(target="bots.economy.futures_coms.save_image", return_value=None)
    value = futures_coms_command()

    recorder.capture(value)
