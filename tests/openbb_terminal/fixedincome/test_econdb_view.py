"""Test the econdb_view.py"""

import pytest

from openbb_terminal.fixedincome import econdb_view


@pytest.mark.parametrize(
    "maturity, start_date, end_date, kwargs",
    [
        ("3_month", "2019-01-01", "2022-01-01", dict()),
    ],
)
def test_plot_cmm(maturity, start_date, end_date, kwargs):
    econdb_view.plot_cmn(
        maturity=maturity, start_date=start_date, end_date=end_date, **kwargs
    )


@pytest.mark.parametrize(
    "maturity, start_date, end_date, kwargs",
    [
        ("3_month", "2019-01-01", "2022-01-01", dict()),
    ],
)
def test_plot_tips(maturity, start_date, end_date, kwargs):
    econdb_view.plot_tips(
        maturity=maturity, start_date=start_date, end_date=end_date, **kwargs
    )


@pytest.mark.parametrize(
    "maturity, start_date, end_date, kwargs",
    [
        ("3_month", "2019-01-01", "2022-01-01", dict()),
    ],
)
def test_plot_tbill(maturity, start_date, end_date, kwargs):
    econdb_view.plot_tbill(
        maturity=maturity, start_date=start_date, end_date=end_date, **kwargs
    )
