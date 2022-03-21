import pytest

from bots.economy.glbonds import glbonds_command


@pytest.mark.vcr
def test_glbonds_command(mocker, recorder):
    mocker.patch(target="bots.economy.glbonds.imps.save_image", return_value=None)
    value = glbonds_command()

    recorder.capture(value)
