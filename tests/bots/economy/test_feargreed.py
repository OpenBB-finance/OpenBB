import pytest

from bots.economy.feargreed import feargreed_command


def strftime(_):
    return "1"


@pytest.mark.bots
@pytest.mark.vcr
def test_feargreed_command(recorder):
    value = feargreed_command()
    # TODO: Patch strftime instead
    value["imagefile"] = None

    recorder.capture(value)
