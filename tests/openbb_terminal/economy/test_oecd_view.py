"""Test OECD view."""

import pytest

from openbb_terminal.economy import oecd_view


@pytest.mark.record_http
@pytest.mark.parametrize(
    "countries, kwargs",
    [
        (
            ["united_states"],
            {"units": "USD_CAP", "start_date": "2019-01-01", "end_date": "2021-12-31"},
        ),
    ],
)
def test_plot_gdp(countries, kwargs):
    """Test plot_gdp."""
    plot = oecd_view.plot_gdp(countries, **kwargs)
    assert plot is not None


@pytest.mark.record_http
@pytest.mark.parametrize(
    "countries, kwargs",
    [
        (["united_states"], {"start_date": "2019-01-01", "end_date": "2021-12-31"}),
    ],
)
def test_plot_real_gdp(countries, kwargs):
    """Test plot_real_gdp."""
    plot = oecd_view.plot_real_gdp(countries=countries, **kwargs)
    assert plot is not None


@pytest.mark.record_http
@pytest.mark.parametrize(
    "countries, kwargs",
    [
        (["united_states"], {"start_date": "2024-01-01", "end_date": "2025-12-31"}),
    ],
)
def test_plot_gdp_forecast(countries, kwargs):
    """Test plot_gdp_forecast."""
    plot = oecd_view.plot_gdp_forecast(countries=countries, **kwargs)
    assert plot is not None


@pytest.mark.record_http
@pytest.mark.parametrize(
    "countries, kwargs",
    [
        (["united_states"], {"start_date": "2019-01-01", "end_date": "2021-12-31"}),
    ],
)
def test_plot_cpi(countries, kwargs):
    """Test plot_cpi."""
    plot = oecd_view.plot_cpi(countries=countries, **kwargs)
    assert plot is not None


@pytest.mark.record_http
@pytest.mark.parametrize(
    "countries, kwargs",
    [
        (["united_states"], {"start_date": "2019-01-01", "end_date": "2021-12-31"}),
    ],
)
def test_plot_balance(countries, kwargs):
    """Test plot_balance."""
    plot = oecd_view.plot_balance(countries=countries, **kwargs)
    assert plot is not None


@pytest.mark.record_http
@pytest.mark.parametrize(
    "countries, kwargs",
    [
        (["united_states"], {"start_date": "2019-01-01", "end_date": "2021-12-31"}),
    ],
)
def test_plot_revenue(countries, kwargs):
    """Test plot_revenue."""
    plot = oecd_view.plot_revenue(countries=countries, **kwargs)
    assert plot is not None


@pytest.mark.record_http
@pytest.mark.parametrize(
    "countries, kwargs",
    [
        (["united_states"], {"start_date": "2019-01-01", "end_date": "2021-12-31"}),
    ],
)
def test_plot_spending(countries, kwargs):
    """Test plot_spending."""
    plot = oecd_view.plot_spending(countries=countries, **kwargs)
    assert plot is not None


@pytest.mark.record_http
@pytest.mark.parametrize(
    "countries, kwargs",
    [
        (["united_states"], {"start_date": "2019-01-01", "end_date": "2021-12-31"}),
    ],
)
def test_plot_debt(countries, kwargs):
    """Test plot_debt."""
    plot = oecd_view.plot_debt(countries=countries, **kwargs)
    assert plot is not None


@pytest.mark.record_http
@pytest.mark.parametrize(
    "countries, kwargs",
    [
        (["united_states"], {"start_date": "2019-01-01", "end_date": "2021-12-31"}),
    ],
)
def test_plot_trust(countries, kwargs):
    """Test plot_trust."""
    plot = oecd_view.plot_trust(countries=countries, **kwargs)
    assert plot is not None
