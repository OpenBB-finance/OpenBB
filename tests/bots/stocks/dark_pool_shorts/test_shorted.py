import pytest

try:
    from bots.stocks.dark_pool_shorts.shorted import shorted_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.vcr
def test_shorted_command(recorder):
    value = shorted_command()
    value["imagefile"] = value["imagefile"][-4:]

    recorder.capture(value)


@pytest.mark.bots
@pytest.mark.vcr
def test_shorted_command_invalid():
    with pytest.raises(Exception):
        shorted_command(-5)
