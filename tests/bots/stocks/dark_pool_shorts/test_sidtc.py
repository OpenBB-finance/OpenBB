import pytest

try:
    from bots.stocks.dark_pool_shorts.sidtc import sidtc_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.vcr
@pytest.mark.bots
def test_sidtc_command(recorder):
    value = sidtc_command()
    value["view"] = str(type(value["view"]))
    value["embed"] = str(type(value["embed"]))
    value["choices"] = str(type(value["choices"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("sort, num", [("float", -10), ("wffewfew", 10)])
def test_shorted_command_invalid(sort, num):
    with pytest.raises(Exception):
        sidtc_command(sort=sort, num=num)
