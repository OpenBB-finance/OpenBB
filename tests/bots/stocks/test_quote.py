import pytest

try:
    from bots.stocks.quote import quote_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
def test_quote_command(recorder):
    value = quote_command("TSLA")

    recorder.capture(value)


@pytest.mark.bots
def test_quote_command_none():
    with pytest.raises(Exception):
        quote_command(None)
