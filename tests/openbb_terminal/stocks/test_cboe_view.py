import pytest
from openbb_terminal.stocks import cboe_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_top_of_book():
    cboe_view.display_top_of_book("AAPL")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_top_of_book_bad_ticker():
    cboe_view.display_top_of_book("JBEUCEBFY")
