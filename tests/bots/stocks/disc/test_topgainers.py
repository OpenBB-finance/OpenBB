import pytest

try:
    from bots.stocks.disc.topgainers import gainers_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.vcr
@pytest.mark.bots
def test_gainers_command(recorder):
    value = gainers_command()
    value["imagefile"] = str(type(value["imagefile"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
def test_gainers_command_invalid():
    with pytest.raises(Exception):
        gainers_command(-10)
