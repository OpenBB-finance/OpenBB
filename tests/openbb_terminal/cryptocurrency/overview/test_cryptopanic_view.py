import pytest

from openbb_terminal.cryptocurrency.overview import cryptopanic_view


@pytest.mark.record_http
def test_display_news():
    cryptopanic_view.display_news(limit=2)
