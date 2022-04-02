import pytest

try:
    from bots.stocks.dark_pool_shorts.pos import pos_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.vcr
@pytest.mark.bots
def test_pos_command(recorder):
    value = pos_command()
    value["imagefile"] = value["imagefile"][-4:]

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("sort, num", [("wefewef", 5), ("dpp_dollar", -5)])
def test_pos_command_invalid(sort, num):
    with pytest.raises(Exception):
        pos_command(sort=sort, num=num)
