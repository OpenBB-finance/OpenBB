import pytest

from bots.economy.futures import futures_command


@pytest.mark.vcr
def test_futures_command(mocker, recorder):
    value = futures_command()
    value.pop("embed")
    for x in ["view", "choices", "embeds_img"]:
        value[x] = str(value[x])
    recorder.capture(value)
