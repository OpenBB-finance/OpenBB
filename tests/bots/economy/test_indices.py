import pytest

from bots.economy.indices import indices_command


@pytest.mark.vcr
def test_indices_command(mocker, recorder):
    mocker.patch(target="bots.economy.indices.imps.save_image", return_value=None)
    value = indices_command()

    recorder.capture(value)
