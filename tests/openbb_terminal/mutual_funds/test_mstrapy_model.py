"""Test the mstrapy model."""

import pytest
from mstarpy import Funds
from pandas import DataFrame

from openbb_terminal.mutual_funds import mstarpy_model

EXAMPLE_FUND = Funds(
    "Vanguard",
    "US",
)


@pytest.mark.record_http()
@pytest.mark.parametrize(
    "term, country,",
    [
        ("Vanguard", "US"),
    ],
)
def test_load_funds(term, country):
    loaded_funds = mstarpy_model.load_funds(term=term, country=country)

    assert loaded_funds.country == country
    assert isinstance(loaded_funds, Funds)
    assert isinstance(loaded_funds, EXAMPLE_FUND.__class__)


@pytest.mark.record_http
@pytest.mark.parametrize(
    "term, country, limit, expected_columns",
    [
        ("Vanguard", "US", 1, ["SecId", "TenforeId", "LegalName"]),
    ],
)
def test_search_funds(record, term, country, limit, expected_columns):
    searched_funds = mstarpy_model.search_funds(term=term, country=country, limit=limit)
    record.add_verify(obj=searched_funds)

    assert searched_funds is not None
    assert not searched_funds.empty
    assert expected_columns == searched_funds.columns.tolist()


@pytest.mark.record_http
@pytest.mark.parametrize(
    "loaded_fund, holding_type, expected_columns",
    [
        (EXAMPLE_FUND, "all", ["isin", "securityName", "weighting", "country"]),
    ],
)
def test_load_holdings(record, loaded_fund, holding_type, expected_columns):
    holdings = mstarpy_model.load_holdings(
        loaded_funds=loaded_fund, holding_type=holding_type
    )
    record.add_verify(obj=holdings)

    assert holdings is not None
    assert not holdings.empty
    assert expected_columns == holdings.columns.tolist()


@pytest.mark.record_http
@pytest.mark.parametrize(
    "loaded_fund",
    [
        (EXAMPLE_FUND),
    ],
)
def test_load_carbon_metrics(loaded_fund):
    carbon_metrics = mstarpy_model.load_carbon_metrics(loaded_funds=loaded_fund)

    assert isinstance(carbon_metrics, DataFrame)
    assert not carbon_metrics.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "loaded_fund",
    [
        (EXAMPLE_FUND),
    ],
)
def test_load_exclusion_policy(loaded_fund):
    exclusion_policy = mstarpy_model.load_exclusion_policy(loaded_funds=loaded_fund)

    assert isinstance(exclusion_policy, DataFrame)
    assert not exclusion_policy.empty
