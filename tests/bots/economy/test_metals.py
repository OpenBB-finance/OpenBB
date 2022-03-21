import pytest

from bots.economy.metals import metals_command


@pytest.mark.vcr
def test_metals_command(mocker, recorder):
    mocker.patch(target="bots.economy.metals.imps.save_image", return_value=None)
    value = metals_command()

    recorder.capture(value)
