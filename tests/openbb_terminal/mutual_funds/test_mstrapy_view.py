"""Test the mstrapy view."""

import pytest

from openbb_terminal.mutual_funds import mstarpy_model, mstarpy_view

EXAMPLE_FUND = mstarpy_model.load_funds(term="Vanguard", country="US")


def test_display_carbon_metrics():
    mstarpy_view.display_carbon_metrics(loaded_funds=EXAMPLE_FUND)


def test_display_exclusion_policy():
    mstarpy_view.display_exclusion_policy(loaded_funds=EXAMPLE_FUND)


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "loaded_fund, start_date, end_date, kwargs",
    [
        (
            EXAMPLE_FUND,
            "2020-01-01",
            "2020-12-31",
            {"comparison": "category", "external_axes": False},
        ),
    ],
)
def test_display_historical(loaded_fund, start_date, end_date, kwargs):
    chart = mstarpy_view.display_historical(
        loaded_funds=loaded_fund,
        start_date=start_date,
        end_date=end_date,
        **kwargs,
    )
    assert chart is not None
    assert hasattr(chart, "save")


@pytest.mark.record_verify_screen
def test_display_holdings():
    mstarpy_view.display_holdings(loaded_funds=EXAMPLE_FUND)


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "term, country",
    [
        ("Vanguard", "united_states"),
    ],
)
def test_display_load(term, country):
    funds = mstarpy_view.display_load(term=term, country=country)
    assert isinstance(funds, EXAMPLE_FUND.__class__)


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "term, country, limit",
    [
        ("Vanguard", "united_states", 10),
    ],
)
def test_display_search(term, country, limit):
    mstarpy_view.display_search(term=term, country=country, limit=limit)


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "loaded_fund, asset_type, external_axes",
    [
        (EXAMPLE_FUND, "all", False),
    ],
)
def test_display_sector(loaded_fund, asset_type, external_axes):
    chart = mstarpy_view.display_sector(
        loaded_funds=loaded_fund, asset_type=asset_type, external_axes=external_axes
    )
    assert chart is not None
    assert hasattr(chart, "to_html")
