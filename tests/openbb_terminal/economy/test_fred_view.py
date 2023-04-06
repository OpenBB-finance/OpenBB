"""Test the fred view."""

import pytest

from openbb_terminal.economy import fred_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


def test_format_units():
    """Test the format units function."""
    assert fred_view.format_units(1) == "1"
    assert fred_view.format_units(1000) == "1K"
    assert fred_view.format_units(1000000) == "1M"
    assert fred_view.format_units(1000000000) == "1B"
    assert fred_view.format_units(1000000000000) == "1T"


@pytest.mark.record_http
@pytest.mark.parametrize("query, kwargs", [("GDP", {})])
def test_notes(query, kwargs):
    """Test the notes function."""
    fred_view.notes(query, **kwargs)


@pytest.mark.record_http
@pytest.mark.parametrize(
    "series_ids, start_date, end_date, kwargs",
    [
        (["GNPCA"], "2019-01-01", "2020-01-01", {}),
    ],
)
def test_display_fred_series(series_ids, start_date, end_date, kwargs):
    """Test the display fred series function."""
    fred_view.display_fred_series(series_ids, start_date, end_date, **kwargs)
