import pytest


# pylint disable=import-outside-toplevel
@pytest.mark.vcr
def test_load_sdk():
    from openbb_terminal.sdk import openbb

    openbb.stocks.load("TSLA")
