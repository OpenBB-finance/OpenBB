"""Test the yfinance_view.py"""

import pytest

from openbb_terminal.fixedincome import yfinance_view


@pytest.mark.parametrize(
    "maturity, kwargs",
    [
        ("5_year", {"start_date": "2021-01-01", "end_date": "2022-01-01"}),
    ],
)
def test_plot_ty(maturity, kwargs):
    fig = yfinance_view.plot_ty(maturity=maturity, **kwargs)
    assert fig is not None
