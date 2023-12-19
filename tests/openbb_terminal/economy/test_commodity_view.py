"""Test the commodity view."""


from openbb_terminal.economy import commodity_view


def test_format_large_numbers():
    commodity_view.format_large_numbers(1_000_000_000_000)
