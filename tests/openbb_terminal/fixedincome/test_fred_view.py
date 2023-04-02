"""Test the fred_view.py"""

import pytest

from openbb_terminal.fixedincome import fred_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_plot_sofr():
    fred_view.plot_sofr()


@pytest.mark.record_http
def test_plot_sonia():
    fred_view.plot_sonia()


@pytest.mark.record_http
def test_plot_ameribor():
    fred_view.plot_ameribor()


@pytest.mark.record_http
def test_plot_fed():
    fred_view.plot_fed()


@pytest.mark.record_http
def test_plot_iorb():
    fred_view.plot_iorb()


@pytest.mark.record_http
def test_plot_fftr():
    fred_view.plot_fftr()


@pytest.mark.record_http
def test_plot_projection():
    fred_view.plot_projection()


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, start_date, end_date, kwargs",
    [
        ("daily_excl_weekend", "2020-01-01", "2020-02-01", dict()),
    ],
)
def test_plot_dwcpcr(parameter, start_date, end_date, kwargs):
    fred_view.plot_dwpcr(parameter, start_date, end_date, **kwargs)


@pytest.mark.record_http
def test_plot_ecb():
    fred_view.plot_ecb()


@pytest.mark.record_http
def test_plot_tmc():
    fred_view.plot_tmc()


@pytest.mark.record_http
def test_plot_ffrmc():
    fred_view.plot_ffrmc()


@pytest.mark.record_http
@pytest.mark.parametrize(
    "date, kwargs",
    [
        ("2021-01-01", dict()),
    ],
)
def test_display_yield_curve(date, kwargs):
    fred_view.display_yield_curve(date=date, **kwargs)


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, maturity, start_date, end_date, kwargs",
    [
        ("tbill", "4_week", "2020-01-01", "2023-02-01", dict()),
    ],
)
def test_plot_usrates(parameter, maturity, start_date, end_date, kwargs):
    fred_view.plot_usrates(parameter, maturity, start_date, end_date, **kwargs)


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, start_date, end_date, kwargs",
    [
        ("3_month", "2020-01-01", "2021-02-01", dict()),
    ],
)
def test_plot_tbffr(parameter, start_date, end_date, kwargs):
    fred_view.plot_tbffr(parameter, start_date, end_date, **kwargs)


@pytest.mark.record_http
def test_plot_icebofa():
    fred_view.plot_icebofa()


@pytest.mark.record_http
def test_plot_moody():
    fred_view.plot_moody()


@pytest.mark.record_http
def test_plot_cp():
    fred_view.plot_cp()


@pytest.mark.record_http
def test_plot_spot():
    fred_view.plot_spot()


@pytest.mark.record_http
@pytest.mark.parametrize("date, kwargs", [("2023-03-30", {})])
def test_plot_hqm(date, kwargs):
    fred_view.plot_hqm(date, **kwargs)
