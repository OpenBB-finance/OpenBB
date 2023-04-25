"""Test the avanza view."""

import pytest

from openbb_terminal.mutual_funds import avanza_view


@pytest.mark.record_http
@pytest.mark.parametrize(
    "isin",
    ["LU0424681269"],
)
def test_display_info(isin):
    avanza_view.display_info(isin=isin)
