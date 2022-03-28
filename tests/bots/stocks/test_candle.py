import pytest
from bots.stocks.candle import candle_command


@pytest.mark.skip
@pytest.mark.vcr
def test_candle_command(recorder):
    value = candle_command("TSLA")

    value["imagefile"] = str(type(value["imagefile"]))
    recorder.capture(value)
