"""Test the covid view."""

import pytest

from openbb_terminal.alternative.covid import covid_view


@pytest.mark.parametrize(
    "country",
    [
        "US",
    ],
)
def test_plot_covid_ov(country):
    plot = covid_view.plot_covid_ov(country)
    assert plot is not None
    assert plot.show.called_once()


@pytest.mark.parametrize(
    "country, stat",
    [
        ("US", "deaths"),
    ],
)
def test_plot_covid_stat(country, stat):
    plot = covid_view.plot_covid_stat(country, stat)
    assert plot is not None
    assert plot.show.called_once()


@pytest.mark.parametrize(
    "country, kwargs",
    [
        ("US", dict()),
    ],
)
def test_display_covid_ov(country, kwargs):
    plot = covid_view.display_covid_ov(country, **kwargs)
    assert plot is not None
    assert plot.show.called_once()


@pytest.mark.parametrize(
    "country, stat, kwargs",
    [
        ("US", "deaths", dict()),
    ],
)
def test_display_covid_stat(country, stat, kwargs):
    plot = covid_view.display_covid_stat(country, stat, **kwargs)
    assert plot is not None
    assert plot.show.called_once()
