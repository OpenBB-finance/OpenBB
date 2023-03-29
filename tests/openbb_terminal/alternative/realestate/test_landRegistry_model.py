import ssl

import pytest

# IMPORTATION INTERNAL
from openbb_terminal.alternative.realestate import landRegistry_model

ssl._create_default_https_context = (  # pylint: disable=protected-access
    ssl._create_unverified_context  # pylint: disable=protected-access
)


@pytest.mark.record_http
def test_get_estate_sales():
    assert len(landRegistry_model.get_estate_sales("DA119NF", 10)) > 0


@pytest.mark.record_http
def test_invalid_postcode_get_estate_sales():
    assert len(landRegistry_model.get_estate_sales("DA11", 10)) == 0


@pytest.mark.record_http
def test_get_towns_sold_prices():
    assert (
        len(
            landRegistry_model.get_towns_sold_prices(
                "DARTFORD", "2019-01-01", "2022-01-01", 10
            )
        )
        > 0
    )


@pytest.mark.record_http
def test_get_region_stats():
    assert (
        len(landRegistry_model.get_region_stats("KENT", "2019-01-01", "2022-01-01")) > 0
    )
