"""Test the landRegistry view."""

import pytest

from openbb_terminal.alternative.realestate import landRegistry_view


@pytest.mark.record_verify_screen
@pytest.mark.record_http
@pytest.mark.parametrize(
    "postcode, limit, export",
    [
        ("DA119NF", 10, ""),
    ],
)
def test_display_estate_sales(postcode, limit, export):
    landRegistry_view.display_estate_sales(
        postcode=postcode, limit=limit, export=export
    )


@pytest.mark.record_verify_screen
@pytest.mark.record_http
@pytest.mark.parametrize(
    "town, start_date, end_date, limit, export",
    [
        ("Birmingham", "2020-12-01", "2020-12-31", 10, ""),
    ],
)
def test_display_towns_sold_prices(town, start_date, end_date, limit, export):
    landRegistry_view.display_towns_sold_prices(
        town=town,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        export=export,
    )


@pytest.mark.record_verify_screen
@pytest.mark.record_http
@pytest.mark.parametrize(
    "region, start_date, end_date, export",
    [
        ("Essex", "2020-12-01", "2020-12-31", ""),
    ],
)
def test_display_region_stats(region, start_date, end_date, export):
    landRegistry_view.display_region_stats(
        region=region,
        start_date=start_date,
        end_date=end_date,
        export=export,
    )
