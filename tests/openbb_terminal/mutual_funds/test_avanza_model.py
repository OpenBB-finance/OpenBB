"""Test the avanza model."""

import pytest

from openbb_terminal.mutual_funds import avanza_model


@pytest.mark.record_http
@pytest.mark.parametrize(
    "isin",
    ["LU0476876163"],
)
def test_get_data(isin):
    data = avanza_model.get_data(isin=isin)

    assert isinstance(data, dict)
    assert data
