"""CLI option parsing must preserve distinct flag/value pairs."""

import pytest

from openbb_cli.controllers.utils import parse_unknown_args_to_dict


@pytest.mark.parametrize(
    "args,expected",
    [
        (["--missing", "--symbol", "AAPL"], {"symbol": "AAPL"}),
        (["--limit=5", "--symbol=AAPL"], {"limit": 5, "symbol": "AAPL"}),
        (["--threshold", "-2.5"], {"threshold": -2.5}),
        (["--label=--literal"], {"label": "--literal"}),
        (["--some--name", "value"], {"some--name": "value"}),
    ],
)
def test_unknown_option_value_boundaries(args, expected):
    assert parse_unknown_args_to_dict(args) == expected
