"""Test the covid model."""

import pytest
from pandas import DataFrame

from openbb_terminal.alternative.covid import covid_model


@pytest.mark.record_http
@pytest.mark.parametrize(
    "country",
    ["US"],
)
def test_get_global_cases(country):
    df = covid_model.get_global_cases(country)
    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "country",
    ["US"],
)
def test_get_global_deaths(country):
    df = covid_model.get_global_deaths(country)
    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "country",
    ["US"],
)
def test_get_covid_ov(country):
    df = covid_model.get_covid_ov(country)
    assert isinstance(df, DataFrame)
    assert not df.empty
