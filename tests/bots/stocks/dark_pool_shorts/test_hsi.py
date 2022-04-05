import pytest

try:
    from bots.stocks.dark_pool_shorts.hsi import hsi_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.vcr
@pytest.mark.bots
def test_hsi_command(recorder):
    value = hsi_command()
    value["view"] = str(type(value["view"]))
    value["embed"] = str(type(value["embed"]))
    value["choices"] = str(type(value["choices"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
def test_hsi_command_invalid():
    with pytest.raises(Exception):
        hsi_command(-1)
