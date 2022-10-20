import pytest
from openbb_terminal.stocks import cboe_model


@pytest.mark.vcr
def test_top_of_book():
    cboe_model.get_top_of_book("AAPL")
