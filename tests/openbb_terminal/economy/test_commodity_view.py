"""Test the commodity view."""

import pytest

from openbb_terminal.economy import commodity_view


def test_format_large_numbers():
    commodity_view.format_large_numbers(1_000_000_000_000)


@pytest.mark.record_http
def test_display_debt():
    commodity_view.display_debt()
