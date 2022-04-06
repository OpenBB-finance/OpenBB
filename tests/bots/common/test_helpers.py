import pytest

try:
    from bots.common.helpers import get_arguments, get_syntax, non_slash, send_options
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.record_stdout
def test_send_options():
    send_options("Commands", ["Option1", "Option2", "Option3"], lambda x: print(x))


@pytest.mark.bots
def test_get_syntax():
    value = get_syntax({"required": ["Option1", "Option2", "Option3"]}, "Command")
    expected = "Command/Option1/Option2/Option3"
    assert value == expected


@pytest.mark.bots
@pytest.mark.parametrize(
    "dictionary, cmd",
    [
        ({}, "ticker"),
        ({}, "past_transactions_days"),
        ({}, "raw"),
        ({"required": {"Command": ["Option1", "Option2"]}}, "Command"),
        ({}, "expiry"),
    ],
)
@pytest.mark.record_stdout
def test_get_arguments(dictionary, cmd):
    get_arguments(dictionary, cmd, lambda x: print(x))


@pytest.mark.bots
@pytest.mark.vcr()
@pytest.mark.parametrize(
    "text, value",
    [
        ("text", False),
        ("!text", False),
        ("!dd", False),
        ("!candle", False),
        ("!candle/ewfewewfwe/1", False),
        ("!candle/tsla/12314121", False),
        ("!candle/tsla/1/20", True),
        ("!gov_contracts/tsla/15/True", True),
        ("!opt_cc_hist/tsla/2022-03-25/680/Calls", True),
    ],
)
@pytest.mark.record_stdout
def test_non_slash(text, value):
    val = non_slash(
        text, lambda x: print(x), lambda x, y, z: print(f"{x.__name__}{y}{z}")
    )
    assert val == value
