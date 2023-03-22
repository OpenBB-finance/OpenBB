"""Test the fred_view.py"""

import pytest

from openbb_terminal.fixedincome import fred_view


def test_plot_sofr():
    fred_view.plot_sofr()


def test_plot_sonia():
    fred_view.plot_sonia()


def test_plot_ameribor():
    fred_view.plot_ameribor()


def test_plot_fed():
    fred_view.plot_fed()


def test_plot_iorb():
    fred_view.plot_iorb()


def test_plot_fftr():
    fred_view.plot_fftr()


def test_plot_projection():
    fred_view.plot_projection()


@pytest.mark.parametrize(
    "parameter, start_date, end_date, kwargs",
    [
        ("daily_excl_weekend", "2020-01-01", "2020-02-01", dict()),
    ],
)
def test_plot_dwcpcr(parameter, start_date, end_date, kwargs):
    fred_view.plot_dwpcr(parameter, start_date, end_date, **kwargs)


def test_plot_ecb():
    fred_view.plot_ecb()


def test_plot_tmc():
    fred_view.plot_tmc()


def test_plot_ffrmc():
    fred_view.plot_ffrmc()


@pytest.mark.parametrize(
    "date, kwargs",
    [
        ("2021-01-01", dict()),
    ],
)
def test_display_yield_curve(date, kwargs):
    fred_view.display_yield_curve(date=date, **kwargs)


@pytest.mark.parametrize(
    "parameter, maturity, start_date, end_date, kwargs",
    [
        ("tbill", "4_week", "2020-01-01", "2023-02-01", dict()),
    ],
)
def test_plot_usrates(parameter, maturity, start_date, end_date, kwargs):
    fred_view.plot_usrates(parameter, maturity, start_date, end_date, **kwargs)


@pytest.mark.parametrize(
    "parameter, start_date, end_date, kwargs",
    [
        ("3_month", "2020-01-01", "2021-02-01", dict()),
    ],
)
def test_plot_tbffr(parameter, start_date, end_date, kwargs):
    fred_view.plot_tbffr(parameter, start_date, end_date, **kwargs)


def test_plot_icebofa():
    fred_view.plot_icebofa()


def test_plot_moody():
    fred_view.plot_moody()


def test_plot_cp():
    fred_view.plot_cp()


def test_plot_spot():
    fred_view.plot_spot()


def test_plot_hqm():
    fred_view.plot_hqm()
